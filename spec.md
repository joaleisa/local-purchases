# Mis Compras — Project Spec

## Overview

A local web app for tracking installment purchases shared among people, built for Argentine users managing credit card (cuotas) and personal debt payments. Runs entirely on localhost, no auth.

**Stack:** FastAPI + SQLite + vanilla JS + Bootstrap 5
**Run:** `uvicorn main:app --reload` → http://localhost:8000
**DB:** `purchases.db` (SQLite, auto-created on startup)

---

## Domain Concepts

### Person
A participant who shares the cost of purchases. Stored with just a name. The "owner" (the app user) is implicit — not stored as a person.

### Payment Method
Either a **credit card** or a **person debt**. The distinction matters for the report: credit cards are what the owner pays monthly; person debts are amounts owed to/from specific people outside of a credit card context.

### Purchase
A single purchase split into `num_installments` monthly payments, starting at `first_payment_month / first_payment_year`. Cost can be shared between the owner and any number of people.

**Key fields:**
- `total_amount` — full purchase price
- `num_installments` — how many monthly installments
- `first_payment_month / first_payment_year` — when installments begin
- `payment_method_id` — which card or person this is charged to
- `owner_participates` — whether the owner shares the cost (default true)
- `participant_ids` — list of people who share the cost

**Cost split:** `installment_amount = total_amount / num_installments`. Then split equally among all payers (owner + participants).

---

## Database Schema

```sql
people (id, name UNIQUE)

payment_methods (id, name UNIQUE, type CHECK('credit_card'|'person_debt'))

purchases (
  id, description, purchase_date,
  total_amount, num_installments,
  first_payment_month, first_payment_year,
  payment_method_id → payment_methods,
  owner_participates BOOLEAN DEFAULT 1,
  created_at
)

purchase_participants (
  id,
  purchase_id → purchases ON DELETE CASCADE,
  person_id   → people    ON DELETE RESTRICT,
  UNIQUE(purchase_id, person_id)
)
```

---

## API Routes

### People
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/people` | List all (ordered by name) |
| POST | `/api/people` | Create — 201, 400 on duplicate |
| PUT | `/api/people/{id}` | Update name |
| DELETE | `/api/people/{id}` | Delete — 400 if in active purchases |

### Payment Methods
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/payment-methods` | List all (ordered by type, name) |
| POST | `/api/payment-methods` | Create — 201, 400 on duplicate |
| PUT | `/api/payment-methods/{id}` | Update |
| DELETE | `/api/payment-methods/{id}` | Delete — 400 if in use |

### Purchases
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/purchases` | List all with participants (desc by year/month/id) |
| GET | `/api/purchases/{id}` | Single purchase with full detail |
| POST | `/api/purchases` | Create with participants — 201 |
| PUT | `/api/purchases/{id}` | Update (replaces participants) |
| DELETE | `/api/purchases/{id}` | Delete (cascades participants) |

### Report
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/report?month=&year=` | Monthly report |

---

## Report Logic

For a given `(month, year)`, the report finds all purchases where that month falls within the installment range `[first_payment_month, first_payment_month + num_installments - 1]`.

For each matching purchase it computes:
- `installment_number` — which installment this is (1-based)
- `installment_amount` — `total_amount / num_installments`
- `num_payers` — owner (if `owner_participates`) + participants
- `per_person` — `installment_amount / num_payers`
- `owner_amount` — owner's share (0 if not participating)
- `others_amount` — sum of all participant shares
- `per_participant[]` — breakdown per person

Results are grouped by payment method and split into `credit_cards` and `person_debts`. The summary contains:
- `total` — all installments this month
- `mine` — owner's share only
- `others_owe_me` — what participants owe the owner
- `i_owe_others` — what the owner owes others (person_debt type)

---

## Frontend Pages

| File | Route | Purpose |
|------|-------|---------|
| `static/index.html` | `/` | Monthly report dashboard |
| `static/purchases.html` | `/purchases.html` | Purchase CRUD |
| `static/people.html` | `/people.html` | People CRUD |
| `static/payment_methods.html` | `/payment_methods.html` | Payment method CRUD |

All pages use vanilla JS + Fetch API. No build step. UI language is Spanish (es-AR). Currency formatted as ARS.

### Report page features
- Month/year navigation (prev/next, URL params for browser history)
- Summary cards: total cards, my share, others owe me, I owe others
- Tables per payment method with per-purchase installment detail

### Purchases page features
- Full CRUD table with add/edit modal
- "Active only" toggle (hides fully-paid purchases)
- Live preview: monthly amount, owner share, per-person cost, date range

---

## Business Rules

1. A purchase must have at least one payer (owner or at least one participant).
2. Participants cannot be deleted if they are referenced in any purchase.
3. Payment methods cannot be deleted if any purchase uses them.
4. Names (people, payment methods) must be unique.
5. Installments are always equal (no variable installment amounts).
6. The owner is never stored as a person — `owner_participates` is a boolean on the purchase.

---

## Non-Goals / Out of Scope

- Authentication / multi-user
- Installments of different amounts
- Currency other than ARS
- Cloud deployment (local only)
- Mobile app
