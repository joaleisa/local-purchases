from fastapi import APIRouter
from database import get_db

router = APIRouter(tags=["reports"])


def _month_idx(year: int, month: int) -> int:
    """Monotonic index for month comparisons only (not used for recovery)."""
    return year * 12 + month


@router.get("/report")
def get_report(month: int, year: int):
    with get_db() as conn:
        all_purchases = conn.execute(
            """SELECT p.*, pm.name AS payment_method_name, pm.type AS payment_method_type
               FROM purchases p
               JOIN payment_methods pm ON p.payment_method_id = pm.id"""
        ).fetchall()

        target = _month_idx(year, month)
        items = []

        for row in all_purchases:
            p = dict(row)
            first = _month_idx(p["first_payment_year"], p["first_payment_month"])
            last = first + p["num_installments"] - 1

            if not (first <= target <= last):
                continue

            installment_number = target - first + 1
            installment_amount = round(p["total_amount"] / p["num_installments"], 2)

            participants = conn.execute(
                """SELECT pp.person_id, pe.name
                   FROM purchase_participants pp
                   JOIN people pe ON pp.person_id = pe.id
                   WHERE pp.purchase_id = ?""",
                (p["id"],),
            ).fetchall()
            participants = [dict(pp) for pp in participants]

            num_payers = (1 if p["owner_participates"] else 0) + len(participants)
            per_person = round(installment_amount / num_payers, 2) if num_payers > 0 else installment_amount
            owner_amount = per_person if p["owner_participates"] else 0.0
            others_amount = round(per_person * len(participants), 2)

            items.append({
                "purchase_id": p["id"],
                "description": p["description"],
                "payment_method_id": p["payment_method_id"],
                "payment_method_name": p["payment_method_name"],
                "payment_method_type": p["payment_method_type"],
                "installment_number": installment_number,
                "num_installments": p["num_installments"],
                "installment_amount": installment_amount,
                "owner_amount": owner_amount,
                "others_amount": others_amount,
                "participants": participants,
                "owner_participates": bool(p["owner_participates"]),
            })

        # Group by payment method
        by_method: dict = {}
        for item in items:
            mid = item["payment_method_id"]
            if mid not in by_method:
                by_method[mid] = {
                    "payment_method_id": mid,
                    "payment_method_name": item["payment_method_name"],
                    "payment_method_type": item["payment_method_type"],
                    "total": 0.0,
                    "mine": 0.0,
                    "others_owe_me": 0.0,
                    "items": [],
                }
            g = by_method[mid]
            g["total"] = round(g["total"] + item["installment_amount"], 2)
            g["mine"] = round(g["mine"] + item["owner_amount"], 2)
            g["others_owe_me"] = round(g["others_owe_me"] + item["others_amount"], 2)
            g["items"].append(item)

        groups = list(by_method.values())
        credit_cards = [g for g in groups if g["payment_method_type"] == "credit_card"]
        person_debts = [g for g in groups if g["payment_method_type"] == "person_debt"]

        return {
            "month": month,
            "year": year,
            "credit_cards": credit_cards,
            "person_debts": person_debts,
            "summary": {
                "cards_total": round(sum(g["total"] for g in credit_cards), 2),
                "cards_mine": round(sum(g["mine"] for g in credit_cards), 2),
                "cards_others_owe_me": round(sum(g["others_owe_me"] for g in credit_cards), 2),
                "debts_total": round(sum(g["total"] for g in person_debts), 2),
                "my_real_total": round(
                    sum(g["mine"] for g in credit_cards)
                    + sum(g["mine"] for g in person_debts),
                    2,
                ),
            },
        }
