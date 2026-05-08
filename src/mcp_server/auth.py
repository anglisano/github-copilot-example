import asyncio
import base64
import hashlib
import logging
import os
import secrets
import time
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

import httpx
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    TokenError,
    construct_redirect_uri,
)
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
from mcp.shared.auth import InvalidRedirectUriError, OAuthClientInformationFull, OAuthToken
from pydantic import AnyUrl

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
JWT_ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
AZURE_AUTHORIZE_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
AZURE_TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
MCP_SERVER_BASE = os.getenv("MCP_SERVER_BASE_URL", "http://localhost:8000")
# MCP_SERVER_BASE = os.getenv("MCP_SERVER_BASE_URL", "http://localhost:30800")

_AUTH_ENABLED = bool(TENANT_ID and CLIENT_ID)

# Simple in-memory JWKS cache to avoid repeated Azure AD calls
_jwks_cache: dict = {}  # {kid: public_key}
_jwks_cache_ts: float = 0.0
_JWKS_TTL = 3600  # refresh every hour


async def _get_public_key_async(kid: str):
    """Fetch Azure AD public key async (non-blocking). Uses a TTL cache."""
    global _jwks_cache, _jwks_cache_ts
    now = time.time()
    if now - _jwks_cache_ts > _JWKS_TTL or kid not in _jwks_cache:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(JWKS_URI)
            resp.raise_for_status()
        _jwks_cache = {
            k["kid"]: RSAAlgorithm.from_jwk(k)
            for k in resp.json()["keys"]
        }
        _jwks_cache_ts = now
    if kid not in _jwks_cache:
        raise ValueError("Public key not found in JWKS")
    return _jwks_cache[kid]


def _get_public_key(kid: str):
    """Synchronous JWKS fetch — only used outside async context (kept for compat)."""
    resp = requests.get(JWKS_URI, timeout=10)
    resp.raise_for_status()
    for key in resp.json()["keys"]:
        if key["kid"] == key["kid"] and key["kid"] == kid:
            return RSAAlgorithm.from_jwk(key)
    raise ValueError("Public key not found in JWKS")


async def validate_token_string_async(token: str) -> dict:
    """
    Async version of validate_token_string — non-blocking, safe to call in async handlers.
    """
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("Token header missing 'kid'")
        public_key = await _get_public_key_async(kid)
        return jwt.decode(
            token,
            public_key,  # type: ignore[arg-type]
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Invalid audience")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid issuer")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Token validation failed: {exc}")


def validate_token_string(token: str) -> dict:
    """
    Validate a raw Bearer token string against Azure AD.
    Returns the decoded payload on success, raises ValueError on failure.
    Only call this when _AUTH_ENABLED is True.
    """
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("Token header missing 'kid'")
        public_key = _get_public_key(kid)
        return jwt.decode(
            token,
            public_key,  # type: ignore[arg-type]
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Invalid audience")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid issuer")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Token validation failed: {exc}")


def get_auth_settings() -> AuthSettings:
    """
    Build FastMCP auth settings.
    The issuer_url points to this MCP server itself (it owns /authorize, /token, etc.)
    because AzureOAuthProvider proxies the full flow from here.
    """
    resource_server_url = os.getenv("MCP_RESOURCE_SERVER_URL", f"{MCP_SERVER_BASE}/sse")

    return AuthSettings(
        issuer_url=MCP_SERVER_BASE,  # type: ignore[arg-type]
        resource_server_url=resource_server_url,  # type: ignore[arg-type]
        required_scopes=None,
        client_registration_options=ClientRegistrationOptions(enabled=True),
    )


# Known VS Code MCP redirect URIs (both http and https variants used depending on context)
_VSCODE_REDIRECT_URIS = [
    AnyUrl("https://vscode.dev/redirect"),
    AnyUrl("http://127.0.0.1:33418/"),
    AnyUrl("http://localhost:33418/"),
    AnyUrl("https://127.0.0.1:33418"),
    AnyUrl("https://localhost:33418"),
]


class _PermissiveClient(OAuthClientInformationFull):
    """Client that accepts ANY redirect_uri, so our proxy never rejects VS Code's callback."""

    def validate_redirect_uri(self, redirect_uri: AnyUrl | None) -> AnyUrl:
        if redirect_uri is not None:
            return redirect_uri
        if self.redirect_uris and len(self.redirect_uris) == 1:
            return self.redirect_uris[0]
        raise InvalidRedirectUriError("redirect_uri must be specified")


# In-memory stores (sufficient for single-process/local use)
_clients: dict[str, _PermissiveClient] = {}
_auth_codes: dict[str, AuthorizationCode] = {}
# Side-channel metadata keyed by state_token or code string
_auth_meta: dict[str, dict] = {}  # {state_token -> {original_state, ...}, code -> {azure_code, ...}}
_access_tokens: dict[str, AccessToken] = {}
_refresh_tokens: dict[str, RefreshToken] = {}


class AzureOAuthProvider:
    """
    OAuthAuthorizationServerProvider that proxies the Authorization Code flow
    to Azure AD. The MCP server exposes its own /authorize and /token endpoints
    which in turn talk to Azure AD.
    """

    # ── Client registration ────────────────────────────────────────────────

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        if client_id in _clients:
            return _clients[client_id]
        # Auto-create a permissive public client for any requesting client_id.
        # Security is enforced by Azure AD during the actual token exchange.
        client = _PermissiveClient(
            client_id=client_id,
            redirect_uris=_VSCODE_REDIRECT_URIS,
            token_endpoint_auth_method="none",
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
            scope="openid profile offline_access",
        )
        _clients[client_id] = client
        return client

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        cid = client_info.client_id or secrets.token_urlsafe(16)
        client = _PermissiveClient(
            client_id=cid,
            redirect_uris=client_info.redirect_uris or _VSCODE_REDIRECT_URIS,
            token_endpoint_auth_method=client_info.token_endpoint_auth_method or "none",
            grant_types=client_info.grant_types,
            response_types=client_info.response_types,
            scope=client_info.scope,
            client_name=client_info.client_name,
        )
        _clients[str(cid)] = client

    # ── Authorization ──────────────────────────────────────────────────────

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """
        Build the Azure AD authorization URL and redirect the browser there.
        Azure will redirect back to /callback on this server.
        """
        callback_uri = f"{MCP_SERVER_BASE}/callback"

        # Store the original client redirect_uri and state so /callback can resume
        state_token = secrets.token_urlsafe(24)
        _auth_codes[f"state:{state_token}"] = AuthorizationCode(
            code=state_token,
            client_id=str(client.client_id),
            scopes=params.scopes or [],
            expires_at=time.time() + 600,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        # Generate our OWN PKCE for the Azure leg (public client — no secret needed)
        az_code_verifier = secrets.token_urlsafe(48)
        az_code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(az_code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        # Side-channel: store original state + our Azure PKCE verifier
        _auth_meta[state_token] = {
            "original_state": params.state,
            "az_code_verifier": az_code_verifier,
        }

        # Use only standard OIDC scopes — no custom api:// scope required
        scope = "openid profile email offline_access"

        az_params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": callback_uri,
            "scope": scope,
            "state": state_token,
            "code_challenge": az_code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{AZURE_AUTHORIZE_URL}?{urlencode(az_params)}"

    # ── Authorization code handling ────────────────────────────────────────

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        entry = _auth_codes.get(f"code:{authorization_code}")
        if entry is None:
            logger.warning(
                "[auth] /token code not found: client_id=%s code=%s...",
                client.client_id,
                authorization_code[:12],
            )
            return None
        if entry.expires_at < time.time():
            _auth_codes.pop(f"code:{authorization_code}", None)
            logger.warning(
                "[auth] /token code expired: client_id=%s code=%s...",
                client.client_id,
                authorization_code[:12],
            )
            return None
        logger.info(
            "[auth] /token code loaded: client_id=%s stored_client_id=%s",
            client.client_id,
            entry.client_id,
        )
        return entry

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        code_key = f"code:{authorization_code.code}"
        _auth_codes.pop(code_key, None)

        # Exchange the stored Azure code for real tokens
        az_meta = _auth_meta.pop(f"az:{authorization_code.code}", {})
        az_code = az_meta.get("azure_code")
        az_code_verifier = az_meta.get("az_code_verifier")
        if not az_code:
            raise TokenError(error="invalid_grant", error_description="No Azure code stored")

        callback_uri = f"{MCP_SERVER_BASE}/callback"
        token_data: dict[str, str | None] = {
            "grant_type": "authorization_code",
            "code": az_code,
            "redirect_uri": callback_uri,
            "client_id": CLIENT_ID,
        }
        if az_code_verifier:
            token_data["code_verifier"] = az_code_verifier
        if CLIENT_SECRET:
            token_data["client_secret"] = CLIENT_SECRET

        resp = requests.post(
            AZURE_TOKEN_URL,
            data={k: v for k, v in token_data.items() if v is not None},
            timeout=15,
        )
        if not resp.ok:
            logger.error(
                "[auth] Azure token exchange failed: status=%s body=%s",
                resp.status_code,
                resp.text,
            )
            print(f"[auth] Azure token exchange failed: status={resp.status_code} body={resp.text}")
            raise TokenError(error="invalid_grant", error_description=resp.text)

        data = resp.json()
        access_token_str = data["access_token"]
        id_token_str = data.get("id_token")
        refresh_token_str = data.get("refresh_token")
        expires_in = int(data.get("expires_in", 3600))
        expires_at = int(time.time()) + expires_in

        # Decode tokens to extract user info and scopes (no sig check — Azure already validated)
        payload = jwt.decode(access_token_str, options={"verify_signature": False})
        scp = payload.get("scp", "")
        scopes = [s for s in scp.split() if s] if scp else []

        # Log authenticated user info
        if id_token_str:
            id_claims = jwt.decode(id_token_str, options={"verify_signature": False})
            name = id_claims.get("name") or id_claims.get("preferred_username")
            email = id_claims.get("email") or id_claims.get("upn")
        else:
            name = payload.get("name")
            email = payload.get("upn") or payload.get("preferred_username")
        logger.info("[auth] User authenticated: name=%s  email=%s  scopes=%s", name, email, scopes)
        print(f"[auth] ✓ Usuario autenticado: {name} <{email}>  scopes={scopes}")

        at = AccessToken(
            token=access_token_str,
            client_id=str(client.client_id),
            scopes=scopes,
            expires_at=expires_at,
        )
        _access_tokens[access_token_str] = at

        rt: RefreshToken | None = None
        if refresh_token_str:
            rt = RefreshToken(token=refresh_token_str, client_id=str(client.client_id), scopes=scopes)
            _refresh_tokens[refresh_token_str] = rt

        return OAuthToken(
            access_token=access_token_str,
            token_type="Bearer",
            expires_in=expires_in,
            refresh_token=refresh_token_str,
            scope=" ".join(scopes) if scopes else None,
        )

    # ── Refresh token ──────────────────────────────────────────────────────

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        return _refresh_tokens.get(refresh_token)

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        resp = requests.post(
            AZURE_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token.token,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": " ".join(scopes) if scopes else None,
            },
            timeout=15,
        )
        if not resp.ok:
            raise TokenError(error="invalid_grant", error_description=resp.text)

        data = resp.json()
        access_token_str = data["access_token"]
        new_refresh_token_str = data.get("refresh_token", refresh_token.token)
        expires_in = int(data.get("expires_in", 3600))

        at = AccessToken(
            token=access_token_str,
            client_id=str(client.client_id),
            scopes=scopes,
            expires_at=int(time.time()) + expires_in,
        )
        _access_tokens[access_token_str] = at

        new_rt = RefreshToken(token=new_refresh_token_str, client_id=str(client.client_id), scopes=scopes)
        _refresh_tokens.pop(refresh_token.token, None)
        _refresh_tokens[new_refresh_token_str] = new_rt

        return OAuthToken(
            access_token=access_token_str,
            token_type="Bearer",
            expires_in=expires_in,
            refresh_token=new_refresh_token_str,
            scope=" ".join(scopes) if scopes else None,
        )

    # ── Access token verification ──────────────────────────────────────────

    async def load_access_token(self, token: str) -> AccessToken | None:
        # Check in-memory cache first (no network call needed)
        if token in _access_tokens:
            at = _access_tokens[token]
            if at.expires_at and at.expires_at < int(time.time()):
                _access_tokens.pop(token, None)
                return None
            return at
        # Fallback: validate against Azure AD JWT (async — does not block event loop)
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            logger.info(
                "[auth] validating bearer token — aud=%s  iss=%s  exp=%s",
                unverified.get("aud"), unverified.get("iss"), unverified.get("exp"),
            )
            print(
                f"[auth] token claims → aud={unverified.get('aud')}  "
                f"iss={unverified.get('iss')}  "
                f"expected_aud={CLIENT_ID}  expected_iss={JWT_ISSUER}"
            )
            payload = await validate_token_string_async(token)
        except ValueError as exc:
            logger.warning("[auth] bearer token rejected: %s", exc)
            print(f"[auth] bearer token rejected: {exc}")
            return None

        scp = payload.get("scp", "")
        scopes = [s for s in scp.split() if s] if scp else []
        exp = payload.get("exp")
        expires_at = int(exp) if isinstance(exp, (int, float)) else None
        client_id = str(payload.get("azp") or payload.get("appid") or payload.get("sub") or "unknown")

        at = AccessToken(token=token, client_id=client_id, scopes=scopes, expires_at=expires_at)
        _access_tokens[token] = at
        return at

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            _access_tokens.pop(token.token, None)
        else:
            _refresh_tokens.pop(token.token, None)
