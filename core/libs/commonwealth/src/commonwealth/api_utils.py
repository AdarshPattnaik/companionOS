"""
CoratiaOS API Utilities — Shared FastAPI helpers for all services.
"""
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger


def create_app(
    title: str,
    description: str,
    version: str = "1.0.0",
    prefix: str = "/v1.0",
) -> FastAPI:
    """Create a standard CoratiaOS FastAPI application."""
    app = FastAPI(
        title=f"CoratiaOS — {title}",
        description=description,
        version=version,
        docs_url=f"{prefix}/docs" if prefix else "/docs",
        redoc_url=f"{prefix}/redoc" if prefix else "/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def run_service(app: FastAPI, port: int, name: str = "service") -> None:
    """Run a CoratiaOS service with uvicorn."""
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description=f"CoratiaOS {name}")
    parser.add_argument("--port", type=int, default=port, help="Service port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Service host")
    args = parser.parse_args()

    logger.info(f"Starting {name} on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
