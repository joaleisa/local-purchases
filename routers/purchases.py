from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import get_db

router = APIRouter(tags=["purchases"])


class PurchaseIn(BaseModel):
    description: str
    purchase_date: Optional[str] = None
    total_amount: float
    num_installments: int = 1
    first_payment_month: int
    first_payment_year: int
    payment_method_id: int
    owner_participates: bool = True
    participant_ids: List[int] = []


def _fetch_purchase(conn, purchase_id: int):
    row = conn.execute(
        """SELECT p.*, pm.name AS payment_method_name, pm.type AS payment_method_type
           FROM purchases p
           JOIN payment_methods pm ON p.payment_method_id = pm.id
           WHERE p.id = ?""",
        (purchase_id,),
    ).fetchone()
    if not row:
        return None
    result = dict(row)
    result["owner_participates"] = bool(result["owner_participates"])
    participants = conn.execute(
        """SELECT pp.person_id, pe.name
           FROM purchase_participants pp
           JOIN people pe ON pp.person_id = pe.id
           WHERE pp.purchase_id = ?""",
        (purchase_id,),
    ).fetchall()
    result["participants"] = [dict(p) for p in participants]
    return result


@router.get("/purchases")
def list_purchases():
    with get_db() as conn:
        rows = conn.execute(
            """SELECT p.*, pm.name AS payment_method_name, pm.type AS payment_method_type
               FROM purchases p
               JOIN payment_methods pm ON p.payment_method_id = pm.id
               ORDER BY p.first_payment_year DESC, p.first_payment_month DESC, p.id DESC"""
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["owner_participates"] = bool(item["owner_participates"])
            participants = conn.execute(
                """SELECT pp.person_id, pe.name
                   FROM purchase_participants pp
                   JOIN people pe ON pp.person_id = pe.id
                   WHERE pp.purchase_id = ?""",
                (item["id"],),
            ).fetchall()
            item["participants"] = [dict(p) for p in participants]
            result.append(item)
        return result


@router.get("/purchases/{id}")
def get_purchase(id: int):
    with get_db() as conn:
        result = _fetch_purchase(conn, id)
        if not result:
            raise HTTPException(404, "Compra no encontrada")
        return result


@router.post("/purchases", status_code=201)
def create_purchase(body: PurchaseIn):
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO purchases
               (description, purchase_date, total_amount, num_installments,
                first_payment_month, first_payment_year, payment_method_id, owner_participates)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                body.description.strip(),
                body.purchase_date,
                body.total_amount,
                body.num_installments,
                body.first_payment_month,
                body.first_payment_year,
                body.payment_method_id,
                1 if body.owner_participates else 0,
            ),
        )
        purchase_id = cur.lastrowid
        for person_id in body.participant_ids:
            conn.execute(
                "INSERT INTO purchase_participants (purchase_id, person_id) VALUES (?, ?)",
                (purchase_id, person_id),
            )
        return _fetch_purchase(conn, purchase_id)


@router.put("/purchases/{id}")
def update_purchase(id: int, body: PurchaseIn):
    with get_db() as conn:
        conn.execute(
            """UPDATE purchases SET
               description=?, purchase_date=?, total_amount=?, num_installments=?,
               first_payment_month=?, first_payment_year=?, payment_method_id=?,
               owner_participates=?
               WHERE id=?""",
            (
                body.description.strip(),
                body.purchase_date,
                body.total_amount,
                body.num_installments,
                body.first_payment_month,
                body.first_payment_year,
                body.payment_method_id,
                1 if body.owner_participates else 0,
                id,
            ),
        )
        conn.execute("DELETE FROM purchase_participants WHERE purchase_id=?", (id,))
        for person_id in body.participant_ids:
            conn.execute(
                "INSERT INTO purchase_participants (purchase_id, person_id) VALUES (?, ?)",
                (id, person_id),
            )
        result = _fetch_purchase(conn, id)
        if not result:
            raise HTTPException(404, "Compra no encontrada")
        return result


@router.delete("/purchases/{id}", status_code=204)
def delete_purchase(id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM purchases WHERE id=?", (id,))
