import sys
import os
import webbrowser
import threading
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import people, payment_methods, purchases, reports


def resource_path(relative_path: str) -> str:
    """Path to bundled resources (read-only, inside the exe)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


app = FastAPI(title="Mis Compras")

init_db()

app.include_router(people.router, prefix="/api")
app.include_router(payment_methods.router, prefix="/api")
app.include_router(purchases.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all so an unexpected bug shows a clean message instead of a raw
    traceback/stack trace in the browser (which could leak file paths, etc.)."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error inesperado. Intentá de nuevo."},
    )


# Static files catch-all (must be last). html=True serves index.html for /
app.mount("/", StaticFiles(directory=resource_path("static"), html=True), name="static")


def _open_browser():
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    threading.Timer(1.0, _open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)