from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter(tags=["people"])


class PersonIn(BaseModel):
    name: str


@router.get("/people")
def list_people():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM people ORDER BY name").fetchall()
        return [dict(r) for r in rows]


@router.post("/people", status_code=201)
def create_person(body: PersonIn):
    with get_db() as conn:
        try:
            cur = conn.execute("INSERT INTO people (name) VALUES (?)", (body.name.strip(),))
            return {"id": cur.lastrowid, "name": body.name.strip()}
        except Exception:
            raise HTTPException(400, "El nombre ya existe")


@router.put("/people/{id}")
def update_person(id: int, body: PersonIn):
    with get_db() as conn:
        conn.execute("UPDATE people SET name=? WHERE id=?", (body.name.strip(), id))
        return {"id": id, "name": body.name.strip()}


@router.delete("/people/{id}", status_code=204)
def delete_person(id: int):
    with get_db() as conn:
        in_use = conn.execute(
            "SELECT 1 FROM purchase_participants WHERE person_id=?", (id,)
        ).fetchone()
        if in_use:
            raise HTTPException(400, "La persona está en uso en compras existentes")
        conn.execute("DELETE FROM people WHERE id=?", (id,))
