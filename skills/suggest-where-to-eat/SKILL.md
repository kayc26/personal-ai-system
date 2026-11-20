---
name: "suggest-where-to-eat"
description: "Suggest where Kay should eat out, based on where she is, when, who she's with, budget, and cravings, drawing on her saved restaurants and places she has loved. Use when she asks where to eat, for a restaurant pick, or somewhere for a date, friends, or family."
---

# Suggest Where to Eat

Pick where Kay should eat for this occasion, in this area, at this time. A good pick is
open, reachable, fits who she's with and what she wants to spend, and draws on the
places she saved and what she has loved before.

Data comes from the food-journal connector and the Google Places search tool. If one
isn't available, say so in a few words and work with the other.

## Step 1: Read the situation

Find out only what's missing, in one question with tappable options where possible:
- **Where:** a neighborhood, a cross street, "near [place]", or a Maps link. You can't
  see her location, so ask if she says "near me". Default city is Philadelphia unless
  she names another.
- **When:** now / tonight / a specific day and time
- **Who:** solo / friends / date / family / work
- **Budget:** $ / $$ / $$$
- **Craving** (optional): a cuisine, a dish, or "surprise me"

Where and who matter most. If she skips the rest, assume tonight, $$, no craving, and
say so in one line.

## Step 2: Build candidates

Use two routes, depending on how tight the location is.

**Saved-first** (a whole city or a broad area, or planning ahead):
- `list_places` with the city and `status` `want_to_go`. Add `cuisine` if she has a
  craving. Always pass a city or status: she has about 1,500 saved places.
- `list_places` with the city and `recommended_only` `yes`, for reliable favorites.
- `list_places` with `status` `been`, to catch verdicts like "skip".

**Nearby-first** ("now", walking distance, or a specific neighborhood):
- Search Google Places for restaurants near the area, filtered by craving if she has
  one.
- For each result, `get_place` to check whether she has saved it, been, or visited.
  Saved and loved places rank higher; places with a "skip" verdict or "once is enough"
  are dropped.

Many imported places have no exact location. When you look one up in Places, pass the
Place ID and coordinates back with `update_place`, and save any cuisine you work out,
so the next search is faster.

## Step 3: Rank

Apply in this order. Earlier rules win.
1. **Hard filters.** Open at that time (check Places hours), reachable (about 15 min
   walk for "now", otherwise say the transit or drive time), within budget (Places
   price level).
2. **Occasion fit.**
   - Date: atmosphere, can talk, takes reservations.
   - Friends or family: shareable dishes, takes groups, reservations for 4+.
   - Solo: counter or bar seating, quick, one great dish.
   - Work: quieter, reliable, easy menu.
3. **Craving match**, if she has one.
4. **Her history.** Favor cuisines and dishes she rates highly (`get_explored`,
   past visits). Drop places where she said she wouldn't return.
5. **Why she saved it.** A specific reason ("famous khao soi", a friend's pick) beats
   a place saved with no note.
6. **New vs. reliable.** Default to somewhere new. For a high-stakes occasion (an
   important date, guests from out of town), lead with a reliable favorite.

Only check the details (hours, price, reservations) for the top 3 to 5, not every
candidate.

## Step 4: Offer 3 picks

Label each one **New** (saved, not tried), **Reliable** (she loved it), or **Wildcard**
(not saved, but a strong fit found nearby). For each:
- Name, neighborhood, and distance or travel time
- Why it fits this occasion, in one line
- What to order: from her saved "why", her own past dishes there, or the menu
- Price level, open until, and whether to reserve
- Maps link

If a Wildcard is new to her, offer to save it (`save_place`, status `want_to_go`) only
after she says yes.

## After

When she eats there, log-food takes over and logs the visit and dishes.

## Style

Short, warm, fast. Match her language (Chinese, English, or mixed).