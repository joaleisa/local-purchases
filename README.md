# local-purchases


## Why do I need this app?

In Argentina is very common to buy things with credit cards. We do this because the store usually has promotions like
three installments with no interest, 6 installments, etc.

In my case I am always using my credit card to finance my purchases and try to win to inflation that is very high in
Argentina. The thing is, most of the expense or purchase trackers only track the current month. This creates a problem
for me when I buy something in installments cause I want to know how much I already have to pay the next month in
order to decide if I should buy something or wait.

### Scenarios:
1. I buy something in one or more installments with my credit card: in this case I would add the purchase and its
month and year first installment due date.
- I buy a pair of sneakers in three payments starting on march 2026. So i need to split the total amount in three and
add the first payment due date to that month/year. In this case id the total was $300.000, march 2026 $100.000, april
2026 $100.000 and may 2026 $100.000.
2. Same as the first scenario but the purchase I make it's not just for me. Imagine the example of the sneakers but the
store has a 2 for one discount so i say to a friend "hey, let's buy two pairs and we only pay the half of just one pair each".
In this case I add the total amount, the quantity of installments(it might be just one payment or several), the first
payment's due date and in how many people should that payment value be splitted.
3. Same scenario for 1 or 2 but now I make the purchase but it is not for me. Imagine the example of case 2 but in this
case I lend two friends my credit card so they can use the promotion of that store. When I add the purchase to the app
I do it with the same data or parameters but I get $0.0 on my individual total

## Needs

1. Add a purchase and track the total amount for all the payments in any given month/year.
2. Add a purchase and select the first payment due date.
3. Add a purchase and select how many people will be paying that purchase and who are they, so i need a people selector and total amounts for people in any given month/year.
4. Same case with 3 but I don't pay that purchase cause I bought something for others.
5. With the purchase record I need to select the payment method.

## Report

- I need to see every purchase made in every month and what payment method was used(mostly credit cards of different banks).
- Example march 2026.
  - Sneakers | Santander | $100.000 | 1/3 payments | Me
  - T-Shirt | Santander | $50.000 | 1/1 payment | Me
  - Jacket | Mercadopago |$30.000 | 3/6 payments | "Me" and "Lucas"
  - Monitor | American Express | $200.000 | 2/6 | "Lucas"
  - Disney plus | I OWE TO "X" PERSON | $3.000 | 1/1 | Me


Notice that it would be helpful to add as a payment method a person for when I owe someone, kind of like scenario number 3 but I use someones credit card.
The idea is to check how much my credit card final amount is, how much of that amount is mine and how much is from others that have to pay me, how much i owe to other people, etc.

The thing is I had a previous report that show those totals but I always have to enter the excel I used for a database to see each purchase and check I forgot one or added the charge for the wrong person.
So, it'd be nice to have like the summarized report for the totals of my payment methods, the individual total for those methods and maybe another report to see every purchase and edit them, delete them, etc.

## Running locally (development)

```bash
pip install -r requirements.txt
python main.py
```

This opens `http://127.0.0.1:8000` in your browser automatically. `purchases.db` is created next to `main.py` on first run.

## Building a standalone executable

To share the app with someone who doesn't have Python installed, it can be packaged into a single
executable file with [PyInstaller](https://pyinstaller.org/). The resulting file bundles Python, all
dependencies, and the `static/` folder — the person only needs that one file plus the same operating
system you built it on (PyInstaller does **not** cross-compile: a binary built on macOS only runs on
macOS, etc.).

### One-time setup

```bash
pip install pyinstaller
```

### Build command

Run from the project root (same folder as `main.py`).

**macOS / Linux:**
```bash
pyinstaller --onefile --name MisCompras \
  --add-data "static:static" \
  --collect-submodules uvicorn \
  --hidden-import uvicorn.lifespan.on \
  --hidden-import uvicorn.lifespan.off \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets.auto \
  --hidden-import uvicorn.loops.auto \
  main.py
```

**Windows** (note: `--add-data` uses `;` instead of `:` on Windows):
```bash
pyinstaller --onefile --name MisCompras --add-data "static;static" --collect-submodules uvicorn --hidden-import uvicorn.lifespan.on --hidden-import uvicorn.lifespan.off --hidden-import uvicorn.protocols.http.auto --hidden-import uvicorn.protocols.websockets.auto --hidden-import uvicorn.loops.auto main.py
```

The output is `dist/MisCompras` (or `dist/MisCompras.exe` on Windows) — that single file is what gets shared.

**Why the `--hidden-import` flags are needed:** uvicorn picks its event loop, HTTP protocol, and
lifespan implementations dynamically at runtime, so PyInstaller's static import scanner can't see
them automatically. Without these flags the built executable will run but immediately fail with an
import error when uvicorn tries to start. If a future uvicorn/fastapi upgrade changes this, the build
will let you know via a clear `ModuleNotFoundError` in the terminal when you test the new exe (see below).

### After building — always test before sending it to anyone

```bash
cd dist
rm -f purchases.db          # start from a clean slate
./MisCompras                # MisCompras.exe on Windows
```

Confirm:
- It opens a browser at `http://127.0.0.1:8000` automatically and the pages load.
- You can add a person, a payment method, and a purchase, and the report shows correct numbers.
- A `purchases.db` file appears next to the executable (this is where that machine's data lives).

### Cleaning up build artifacts

PyInstaller leaves a `build/` folder and a `.spec` file behind; safe to delete between builds (or
keep the `.spec` file if you want to tweak build options without retyping the whole command):

```bash
rm -rf build dist *.spec
```

### Sharing with friends

Send only the single executable file (`MisCompras` / `MisCompras.exe`). Tell them:
- It only listens on `127.0.0.1` (their own machine), so nobody else on their Wi-Fi can reach it.
- Running it creates `purchases.db` next to wherever they put the file — that file *is* their data,
  so it should travel with the executable if they move it.
- Since it's an unsigned, homemade executable, their OS will likely show a security warning the
  first time they run it (Windows SmartScreen, macOS "unidentified developer", etc.) — this is
  expected and they can click through it ("More info → Run anyway" on Windows; right-click → Open
  on macOS).
- Each friend's copy is fully independent — there's no shared data or syncing between instances.