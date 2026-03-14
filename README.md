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

