"""Independent HTTP API for VLMB."""

from fastapi import FastAPI

app = FastAPI(
    title="VLMB API",
    version="4.0.0-rc1",
)


@app.get("/health", tags=["system"])
async def health():
    """Return basic API process health."""
    return {"status": "ok"}
