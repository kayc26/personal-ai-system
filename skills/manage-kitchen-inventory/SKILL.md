---
name: "manage-kitchen-inventory"
description: "Keep Kay's kitchen inventory accurate: add groceries from a haul photo or receipt with realistic expiry dates, answer what's on hand, and run the weekly review of expiring, expired, and low-stock items plus a shopping list for her 'this week' recipes. Use when she sends a grocery haul or receipt, asks what she has or what's expiring, says she used up, tossed, opened, or moved something, wants to correct an item, or asks for the weekly inventory review or shopping list."
---

# Manage Kitchen Inventory

The inventory is only useful if it's right. Adding groceries should take one photo, and
the weekly review catches what slipped through: snacks, food eaten straight from the
fridge, and things thrown out.

Data comes from the kitchen-inventory connector, plus food-journal for the "this week"
recipe list in the weekly review. Deducting ingredients after a home-cooked meal is
handled by log-food, not here.

## Grocery haul or receipt

1. **Read everything** in the photo or receipt. Receipts use store abbreviations
   ("ORG BBY SPNCH"); turn them into plain names.
2. **Name each item** the way the tool wants: short, generic, everyday ("spinach",
   "chicken thighs", "greek yogurt"). Brand, variety, and pack size go in `details`.
3. **Pick the location:** fridge, freezer, pantry, or countertop, from what the item
   is and how she usually stores it (check `list_inventory` if unsure).
4. **Set expiry:** use the package date if it's visible. Otherwise use the shelf-life
   table below, from today, at the conservative end.
5. **Low-stock thresholds** only for staples she restocks (eggs, rice, protein
   staples, milk), and only if the item doesn't already have one.
6. **Skip** salt, oil, and everyday aromatics and seasonings (garlic, ginger,
   scallions, soy sauce, sesame oil). They're assumed on hand and not tracked unless
   she asks.
7. Call `add_item` for each item. If a response lists a similar existing item, add to
   that one instead of creating a duplicate.
8. **Confirm in one short summary** grouped by location, flagging only what you
   guessed: "Added 14: fridge 9, freezer 3, pantry 2. Guessed expiry for spinach (Oct
   1) and tofu (Oct 5)." Ask only about items you couldn't identify.

## Used up, tossed, opened, moved, or corrected

Confirm each change in one line.

- **Partly used:** `use_item`. **Gone:** `remove_item`.
- **Opened:** for items with an "opened" row in the shelf-life table (milk, yogurt,
  tofu, hard cheese), set expiry with `update_item` to the earlier of the current
  expiry and today + the opened shelf life, conservative end. Don't ask; she told you
  it's open. "Milk now expires Oct 7."
- **Moved:** `update_item` field `location`. Moving doesn't change expiry, so ask
  whether it should switch to the new location's shelf life from today, and suggest
  the date: "Chicken is in the freezer now. Change expiry from Oct 4 to Jan 2?"
- **made_date changed:** `update_item` field `made_date`, then ask whether expiry
  should move to made_date + 4 days, and suggest the date.
- **Any other correction** (expiry, quantity, name, details, low-stock threshold):
  `update_item`, one field per call. Never remove and re-add an item to edit it.

## What's on hand

For "what do I have" or "do I have X", call `list_inventory` (a location if she named
one). Answer briefly, grouped by location, and flag anything expiring within 3 days.
For "what's expiring", call `get_expiring` (default 7 days; use the number she gives)
instead of scanning the list. For "what should I make with it", hand off to
suggest-what-to-cook.

## Weekly review

Run when she asks, or when the weekly scheduled task starts it.

1. **Gather, in parallel:** `get_expiring` with `days` 7, `check_low_stock`, and
   `list_saved_recipes` with `queued` `true` (the "this week" list). If `get_expiring`
   reports `no_expiry_count` above 0, also call `list_inventory` to find those items.
2. **Build the lists:**
   - **Expired:** `days_left` below 0. Ask in one tap: "Toss all" / "Some are still
     good".
   - **Use this week:** `days_left` 0 to 7, soonest first.
   - **Running low:** from `check_low_stock`.
   - **Still there?** Items with no expiry at all. Ask once whether they're still
     around, and remove what isn't.
   - **Opened?** Items with an "opened" row in the shelf-life table whose expiry is
     further out than the opened shelf life (so still dated as unopened). Ask "Opened
     any of these?" with the items as options (multi-select). For each she picks,
     apply the "Opened" rule above.
3. **This week's recipes.** For each queued recipe:
   - Check what it needs against the inventory. Call `get_saved_recipe` and check
     the full ingredient list. Aromatics and seasonings are assumed on hand.
   - **Link only** (no full recipe text): check its `ingredients` tags, and say the
     list is partial: "Miso salmon is link only, so its shopping list may be missing
     things. Open it in Chrome and say 'get the recipe'." Don't guess the rest.
   - Note which queued recipes use items from "Use this week". Those should be cooked
     first; say so.
   - **Stale:** if `days_queued` is 10 or more, ask in one tap: "Keep" / "Take off
     the list" / "Drop the recipe". Take off = `update_saved_recipe` field `queued`,
     empty value. Drop = field `status`, value `dropped`.
4. **Shopping list.** One list, grouped by store section (produce, protein, dairy,
   pantry): what the queued recipes need and the inventory lacks, plus "Running low".
   Merge duplicates. Skip anything already on hand in enough quantity.
5. **Catch-up:** don't ask her to remember. Show the fridge and countertop items not
   already covered above, one compact list grouped by location, and ask "Any of these
   gone or partly used?" Update from her answer (`remove_item` or `use_item`).
6. **Meals for leftovers.** For "Use this week" items that no queued recipe covers,
   suggest 1 or 2 meals, following suggest-what-to-cook (her saved and cook-again
   recipes first). If the list is empty, offer "Plan my week" (suggest-what-to-cook
   queues 3 to 5 recipes).
7. **Summary line:** "Removed 3 expired, 5 to use this week, 4 queued recipes, 7 to
   buy."

**When the scheduled task runs it** and nobody is there to answer: don't remove,
unqueue, or drop anything. Build the lists and the shopping list, and put every
question (expired items, still there?, opened?, stale recipes, the catch-up list) at
the end for her to answer
when she's back.

## Shelf-life table

For items without a package date. Days from purchase, conservative end.

| Item | Fridge | Freezer |
|---|---|---|
| Leafy greens, herbs, bean sprouts | 3 to 5 days | not recommended |
| Bok choy, gai lan, choy sum | 3 to 5 days | not recommended |
| Broccoli, cauliflower, cabbage (cut) | 5 to 7 days | 10 to 12 months (blanched) |
| Whole cabbage, carrots, celery | 2 to 3 weeks | 10 to 12 months (blanched) |
| Peppers, zucchini, eggplant | 5 to 7 days | 10 to 12 months (blanched) |
| Mushrooms | 5 to 7 days | 10 to 12 months (cooked) |
| Berries | 3 to 5 days | 8 to 12 months |
| Apples, citrus | 3 to 4 weeks | not recommended |
| Tofu, opened | 3 to 5 days (in water, changed daily) | 3 to 5 months |
| Eggs | 3 to 5 weeks | not recommended |
| Milk, opened | 5 to 7 days | 3 months |
| Yogurt, opened | 7 to 14 days | 1 to 2 months |
| Hard cheese, opened | 3 to 4 weeks | 6 months |
| Raw chicken or ground meat | 1 to 2 days | 3 to 4 months (ground), 9 months (pieces) |
| Raw steaks, chops, roasts | 3 to 5 days | 4 to 12 months |
| Raw fish, shrimp | 1 to 2 days | 3 to 8 months |
| Cooked leftovers, cooked rice | 3 to 4 days | 2 to 3 months |
| Bread | 5 to 7 days (counter) | 3 months |

Pantry and freezer items with a printed date: use the date. Onions, potatoes, garlic,
and winter squash on the counter or in the pantry: 1 to 2 months.

## Style

Short, warm, fast. Match her language (Chinese, English, or mixed).