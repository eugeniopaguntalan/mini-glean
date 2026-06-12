"""
AWS Lambda Entry Point

Wraps the FastAPI app with Mangum so it can run behind API Gateway. Secrets are
pulled from SSM Parameter Store at cold start *before* the application config is
imported, because ``config.Settings()`` validates required environment variables
the moment it is imported.

Locally (no ``AWS_EXECUTION_ENV``) this module is inert — the existing ``.env``
flow in ``config.py`` is used instead.
"""

import os

# Default SSM parameter names. The infra stack passes these through as env vars
# so the names can be overridden without code changes.
_SSM_PARAMETERS = {
    "OPENAI_API_KEY": os.environ.get(
        "OPENAI_API_KEY_PARAM", "/miniglean/openai-api-key"
    ),
    "DATABASE_URL": os.environ.get(
        "DATABASE_URL_PARAM", "/miniglean/database-url"
    ),
}


def _bootstrap_secrets() -> None:
    """Populate required secrets from SSM when running inside Lambda.

    Only runs in the Lambda runtime (``AWS_EXECUTION_ENV`` is set) and never
    overwrites a value that is already present in the environment.
    """
    if not os.environ.get("AWS_EXECUTION_ENV"):
        return

    missing = {
        env_var: param
        for env_var, param in _SSM_PARAMETERS.items()
        if not os.environ.get(env_var)
    }
    if not missing:
        return

    import boto3

    ssm = boto3.client("ssm")
    for env_var, param_name in missing.items():
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        os.environ[env_var] = response["Parameter"]["Value"]


# Must happen before importing the app (config validates env on import).
_bootstrap_secrets()

from mangum import Mangum  # noqa: E402
from main import app  # noqa: E402

# Lifespan is disabled: the startup DB ping is only diagnostic and the engine is
# reused across warm invocations, so we don't want it torn down per request.
_asgi_handler = Mangum(app, lifespan="off")


def handler(event, context):
    """Lambda handler.

    Short-circuits scheduled warmer pings (``{"warmer": true}``) so they keep the
    function warm without paying the cost of routing through the ASGI app.
    """
    if isinstance(event, dict) and event.get("warmer"):
        return {"warmed": True}
    return _asgi_handler(event, context)
