---
name: log-ready-to-eat
description: Log packaged or whole food Kay eats as it comes (a protein bar, yogurt, chips, cheese, bottled kombucha, fruit, raw nuts) as a meal with hunger and satisfaction check-ins, with product details in the notes and kitchen-inventory updated when it came from her kitchen. Use when she sends a photo of a snack, a product, a fruit, or a produce sticker, or says she's eating or ate one. Not for food someone else freshly prepared (log-dining-out) or food she made or assembled (log-home-cooking).
---

# Log ready-to-eat food

Packaged food (eaten largely as sold) and whole food (eaten as is, at most washed or
cut). The only record is the meal, type `packaged` or `whole`. Read
`references/meals.md` before the first meal of a conversation; it has the check-ins,
times, and tone.

No dish catalog entries here: nothing was cooked, and the catalog is for dishes. If she
cut fruit into a bowl with yogurt and granola, she assembled it: that's homemade
(log-home-cooking).

## Flow

1. **Open meal?** `get_open_meal`. If a meal of another type is open (a dinner, a
   restaurant), this item is part of it: add it to that meal's notes and stop.
2. **Type:** `packaged` if it's a commercial product eaten as sold, `whole` if it's
   minimally processed eaten as is. A bag of raw almonds is `packaged` (first match
   wins).
3. **Start check-in** and `start_meal`. For a quick snack she's already eaten, do both
   check-ins in one exchange with real times (meals.md).
4. **Product details in the notes,** from the photo or her words: brand, product,
   flavor, variety, and the produce code if there's a sticker, e.g. "Honeycrisp apple,
   PLU 3283" or "Trader Joe's unexpected cheddar". Keep her own comments word for word.
5. **Inventory:** if it probably came from her kitchen, `use_item` (or `remove_item`
   if it's finished) by its generic inventory name, without asking. If the name isn't
   found, use a suggested match that fits, or skip it silently if nothing does.
6. **End check-in** and `end_meal`.
7. **Confirm in one line,** e.g. "Logged: Honeycrisp apple. Hunger 4 -> 2,
   satisfying 4."

## Fixing

`update_meal` with the meal id from `get_recent` (domain `meals`). Its notes replace the
old notes, so merge first.

## Style
Short, warm, fast. Match her language (Chinese, English, or mixed).
