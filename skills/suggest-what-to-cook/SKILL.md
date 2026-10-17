---
name: "suggest-what-to-cook"
description: "Suggest what Kay should cook and give her a full, followable recipe, using her 'this week' list, kitchen inventory and expiring items, what she cooked recently, her saved and cook-again recipes, and today's training and remaining macros. Use when she asks what to cook, make, or eat at home, what to do with an ingredient, wants ideas from what she has, asks for a recipe for a dish, asks to plan her week's cooking, or adds to or asks about her 'this week' list."
---

# Suggest What to Cook

Pick what Kay should cook right now and hand her a recipe she can actually follow.
A good suggestion fits her evening (time, energy, who's eating), uses what's in her
kitchen before it goes bad, fits today's nutrition, and isn't something she just made.

Her "this week" list comes first. It holds saved recipes she already decided she wants
to cook soon, with no day attached. Pick from it before suggesting anything else.

Data comes from three connectors. If one isn't available, say so in a few words and
work with the rest.
- food-journal: saved recipes, the "this week" list, and cooking history.
- kitchen-inventory: what's on hand and when it expires.
- workout-log: whether today is a training day.

## Step 1: Read the situation

Find out only what's missing from her message, in one question with tappable options:
- **Time:** 15 min / 30 min / an hour+
- **Mood:** comfort / light / something new
- **Who:** just me / me + leftovers / guests

If she says "just pick" or skips, assume 30 minutes, just her, leftovers welcome, and
say so in one line.

Always ask for today's numbers in the same question: add "Paste Macros Remaining" as
an option. If she pastes MacroFactor's JSON, use it (the nutrition profile explains how
to read it). If she doesn't, skip macros entirely and don't ask again.

## Step 2: Gather, in parallel

- `list_saved_recipes` with `queued` `true`: the "this week" list, oldest queued first.
- `get_expiring` with `days` 4: what needs using soon, soonest first.
- `list_inventory` (all locations): proteins and everything else on hand.
- `list_saved_recipes` with `status` `cook_again`, then with `status` `saved`: her own
  recipes. For the 1 or 2 items expiring soonest, repeat both with `ingredient` set to
  that item.
- `get_recent` with `days` 14 and `domain` home: what she cooked lately.
- `get_training_status`: training day, rest day, or cardio day.

## Step 3: Build candidates

Pull 6 to 10 candidates, in this order:
1. **This week:** every queued recipe.
2. **Her recipes:** other `cook_again` and `saved` recipes, especially ones that use an
   expiring item.
3. **One new idea**, only if the "this week" list is empty or nothing on it survives
   the hard filters in Step 4: a dish, cuisine, or technique she hasn't explored
   (`get_explored` with `cuisine` or `technique`) that her inventory can mostly cover.

Skip recipes with status `cooked` (tried, wouldn't make again) unless she asks for
them or they're queued.

## Step 4: Rank

Apply in this order. Earlier rules win.
1. **Hard filters.** Drop anything that doesn't fit the time, needs more than 3
   ingredients she doesn't have (unless she said she'll shop), or that she cooked in
   the last 7 days. Avoid the same dish family two nights running. Queued recipes go
   through the same filters.
2. **This week first.** A queued recipe that passes the filters beats anything that
   isn't queued. Among queued recipes, use the rules below to pick.
3. **Nutrition fit.** Apply check-nutrition: protein-forward, carbs placed around
   training, and fits what's left today if she pasted it.
4. **Uses what's expiring.** A dish that saves the bok choy beats one that doesn't.
5. **Her recipes before new.** `cook_again`, then `saved`, then the new idea.
6. **Her taste.** Favor cuisines and dishes she has rated highly.

## Step 5: Offer 3 options

For each option, give one short block:
- Label (**This week**, **Cook again**, **Saved recipe**, or **New**) and the dish name
- Why tonight, in one line (e.g. "uses the gai lan expiring Thursday, 25 min")
- To buy: at most 3 items, or "nothing". Garlic, ginger, scallions, soy sauce, sesame
  oil and other everyday aromatics and seasonings are assumed on hand.

If a queued recipe got filtered out, say why in a few words ("dan dan noodles needs
an hour, saving it for the weekend"). End with "Which one?" and include "Something
else" as an option.

## Step 6: Give a real recipe

Once she picks, give a recipe she can cook from without opening anything else.

**Where the recipe comes from, in order:**
1. **Her recipe.** If she has a `cook_again` or `saved` recipe for this dish (from
   Step 2, or `get_dish_history`, which lists a dish's saved recipes), call
   `get_saved_recipe` for the full text. Prefer `cook_again` over `saved`, and skip
   ones marked `cooked` (tried, didn't want again). If the recipe only has a link to
   an open site (Serious Eats, a blog, Just One Cookbook, The Woks of Life), read the
   page. Paywalled sites (NYT Cooking, ATK): use what's stored and say the full recipe
   is behind the paywall.
2. **No recipe of hers.** Search for a well-regarded recipe from a reliable source (Serious
   Eats, The Woks of Life, Made With Lau, Just One Cookbook, Maangchi, or strong
   Chinese sources for Chinese dishes), then adapt it. Write from general knowledge
   only as a last resort, and say so.

If she has cooked this dish before, check `get_dish_history` and use the `changes` and
notes from earlier attempts to adjust. Say it in one line ("Last time: too sweet, sauce
too thin. This time: less sugar, reduce longer.").

**Format:**
- Title, servings, total time, source link
- Ingredients with amounts (grams where it matters, plus spoons and cups), marked
  "have" or "buy"
- Numbered steps, each with heat, time, and a doneness cue ("until the edges brown,
  about 3 min")
- One nutrition tweak from check-nutrition, if it matters (e.g. "add an egg for
  protein", "eat the greens first")
- Scaled to her servings. If leftovers are wanted, say how to store them.

Don't estimate calories. MacroFactor handles the numbers.

## Plan my week

When she asks to plan the week ("plan my week", "what should I cook this week", "fill
my list"), queue 3 to 5 recipes. Only saved recipes can be queued.

1. Gather: the current list (`list_saved_recipes` with `queued` `true`),
   `get_expiring` with `days` 7, `list_saved_recipes` with `status` `cook_again` and
   `saved` (plus `ingredient` for the 2 or 3 items expiring soonest), and `get_recent`
   with `days` 14 and `domain` home.
2. Pick enough to bring the list to 3 to 5. Favor recipes that use expiring items,
   then `cook_again` favorites. Mix dish families and cuisines, include at least one
   quick weeknight dish (30 min or less), and skip anything cooked in the last 7 days.
3. Show the picks, one line each (dish, why, what to buy), plus one combined to-buy
   list. Offer "Queue all" / "Let me pick".
4. Queue each one with `update_saved_recipe` (field `queued`, value `yes`). Confirm in
   one line: "This week: 4 recipes. To buy: gai lan, chicken thighs, rice cakes."

## Adding to or taking off the list

- "Add this to this week": find the recipe (`list_saved_recipes`, or `find_dish` for
  the dish's saved recipes) and set `queued` to `yes`. If there's no saved recipe yet,
  save one first with the clip-recipe skill, then queue it.
- "Take X off" / "not this week": set `queued` to empty. Losing interest in the recipe
  entirely is `status` `dropped`, which also takes it off.
- "What's on this week": `list_saved_recipes` with `queued` `true`. One line each, with
  how many days it has been queued.

Re-queuing a recipe keeps its original date. Queuing doesn't change its status: a
`cook_again` favorite stays `cook_again`.

## After

When she says she cooked it, log-food takes over: it logs the meal, links the saved
recipe (which takes it off the "this week" list), asks whether she'd make it again,
and offers to deduct the ingredients from the inventory. If she wants to save a new
recipe along the way, clip-recipe saves it.

## Style

Short, warm, fast. Match her language (Chinese, English, or mixed). Keep dish names in
the form she uses.