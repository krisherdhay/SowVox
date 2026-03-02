import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

AUTH0_DOMAIN = os.environ.get(
    "AUTH0_DOMAIN", "dev-6tmjmta61xzkh331.us.auth0.com"
)
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")
AUTH0_ALGORITHMS = ["RS256"]

security = HTTPBearer()

_jwks_cache = None


def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        response = httpx.get(url)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)

        # Find the signing key that matches the token's kid
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Signing key not found")

        # Skip audience validation if no audience is configured
        decode_options = {}
        if not AUTH0_AUDIENCE:
            decode_options["verify_aud"] = False

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_AUDIENCE or None,
            issuer=f"https://{AUTH0_DOMAIN}/",
            options=decode_options,
        )
        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {e}")
