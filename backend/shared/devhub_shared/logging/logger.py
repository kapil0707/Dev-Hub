"""
=============================================================================
Structured JSON Logger — devhub_shared.logging.logger
=============================================================================
PURPOSE:
    Provides a unified, structured JSON logger for all Dev-Hub microservices.

WHY STRUCTURED LOGGING?
    When you have 6 separate services, you cannot debug by just reading a wall
    of text. Structured logging outputs JSON lines like:
        {"timestamp": "...", "level": "INFO", "service": "bff", "correlation_id": "...", "message": "..."}

    This makes it trivial to:
    - Filter logs by service: grep '"service": "identity"'
    - Trace a request: grep '"correlation_id": "abc-123"' across ALL service logs
    - Feed logs into tools like Datadog, Splunk, or Grafana Loki in production

USAGE (in any service):
    from devhub_shared.logging.logger import get_logger
    logger = get_logger(__name__, service_name="identity")
    logger.info("User created", extra={"user_id": "...", "correlation_id": "..."})
=============================================================================
"""
import logging
import sys
from pythonjsonlogger import jsonlogger


def get_logger(name: str, service_name: str = "devhub") -> logging.Logger:
    """
    Creates and returns a structured JSON logger.

    Args:
        name: Usually __name__ of the calling module (e.g., "identity.routes.auth")
        service_name: The microservice name tag (e.g., "bff", "identity", "snippet_engine")

    Returns:
        A configured Python Logger that outputs JSON to stdout.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if this function is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # --- JSON Handler (stdout) -----------------------------------------------
    # In production, stdout is captured by Docker/Kubernetes log drivers
    # and forwarded to your centralized logging system.
    handler = logging.StreamHandler(sys.stdout)

    # Custom JSON format: timestamp + level + service tag + message + extras
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Inject the service name into every log record from this logger
    logger = logging.LoggerAdapter(logger, extra={"service": service_name})

    return logger
