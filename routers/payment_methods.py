from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from database import get_db

router = APIRouter(tags=["payment_methods"])


class PaymentMethodIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["credit_card", "person_debt"]

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v


@router.get("/payment-methods")
def list_payment_methods():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM payment_methods ORDER BY type, name"
        ).fetchall()
        return [dict(r) for r in rows]


@router.post("/payment-methods", status_code=201)
def create_payment_method(body: PaymentMethodIn):
    with get_db() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO payment_methods (name, type) VALUES (?, ?)",
                (body.name.strip(), body.type),
            )
            return {"id": cur.lastrowid, "name": body.name.strip(), "type": body.type}
        except Exception:
            raise HTTPException(400, "El nombre ya existe")


@router.put("/payment-methods/{id}")
def update_payment_method(id: int, body: PaymentMethodIn):
    with get_db() as conn:
        conn.execute(
            "UPDATE payment_methods SET name=?, type=? WHERE id=?",
            (body.name.strip(), body.type, id),
        )
        return {"id": id, "name": body.name.strip(), "type": body.type}


@router.delete("/payment-methods/{id}", status_code=204)
def delete_payment_method(id: int):
    with get_db() as conn:
        in_use = conn.execute(
            "SELECT 1 FROM purchases WHERE payment_method_id=?", (id,)
        ).fetchone()
        if in_use:
            raise HTTPException(400, "El método de pago está en uso en compras existentes")
        conn.execute("DELETE FROM payment_methods WHERE id=?", (id,))