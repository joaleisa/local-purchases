import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import people, payment_methods, purchases, reports

app = FastAPI(title="Mis Compras")

init_db()

app.include_router(people.router, prefix="/api")
app.include_router(payment_methods.router, prefix="/api")
app.include_router(purchases.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

# Static files catch-all (must be last). html=True serves index.html for /
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
