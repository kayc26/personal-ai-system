# ADR-0003: Kitchen multi-user data model

- **Date**: 2026-11-20
- **Iteration**: 1
- **Status**: Draft
- **Deciders**: Kay (decides), Ari (Claude Opus 5.5, recommends)
- **Source**: [seed-2026-11-20-separating-the-system](seed-2026-11-20-separating-the-system.md)

**TL;DR**: One kitchen server serves one household. The inventory is shared by everyone signed in. Recipes and the "this week" list belong to each person. Kay's existing rows become hers.

---

## Context

Kitchen gets three users (Kay and two roommates), signing in per [ADR-0002](0002-oauth-through-neon-auth.md), with recipes moving in from food-journal per [ADR-0001](0001-split-the-system-by-area.md). From the seed:
- One shared inventory for the household.
- Recipe inboxes are per person.
- A recipe gets marked cooked; there's no home-cook journal on the kitchen side.
- Languages differ. Item names need **no change**: `add_item` already takes the everyday name, other-language names can go in `details`, and every add or miss lists similar items (by words, spelling, or a name in details), so the model merges duplicates.

## Decision (agreed in the seed)

1. **One deployment = one household.** Everyone allowed on the server shares one inventory. No households table.
2. **Inventory is shared.** No owner on items. Every allowed user can add, use, and remove anything.
3. **Recipes are per person.** Saved recipes and the "this week" list get a `user_id`. Every recipe query is scoped to the signed-in user server-side.
4. **Cooked marker.** A recipe records when it was last cooked, so "cooked recently" comes from code, not the model.
5. **Kay's data migrates to Kay.** Kay's recipes copied from `kayfoodlab` get her user id once she has one. Tests prove that one user can't read or change another's recipes.
6. **Skills become general.** "Kay" leaves skill text. Personal rules come from the place decided in Q-PERSONAL-RULES. Reply language follows the user (the model matches their language; in Claude Code, the `language` setting).

Do not build: households, item owners, sharing recipes between people, name normalization or translation tables, roles or admin users.

---

## Questions

### QST-RECIPE-VISIBILITY: Can roommates see each other's recipes?
- Status: answered
- Why asking: decision 3 makes recipes private. If roommates cook for each other, private inboxes might get in the way. If not, shared ones add clutter and token cost.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Private**: each person sees only their own recipes and "this week" list.
- **B — Readable by the household**: you see your own by default and can ask for a roommate's ("what's on Mia's list?"). Only the owner can change them.
- **C — One shared recipe box**: like the inventory.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Private.** Rationale: Kay said inboxes differ, and private is the simplest rule to test. Opening reads later is a query change; taking visibility away after people have used it is harder.
Confidence: 0.7, because I don't know how the roommates cook together. If wrong: if they plan meals together, B.

**ANS:** (by kayc26)
b

---

### QST-PERSONAL-RULES: Where do per-person rules live?
- Status: answered
- Why asking: skills must be general, but suggest-what-to-cook and check-nutrition use personal rules (macros, diet, schedule). Kay keeps them in a Project file today. Roommates on the phone don't want a long setup, and a Claude Project with a file is setup.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — A profile on the server**: each user has a short free-text profile, read and written with a tool. Works the same in the app, on the phone, and in Claude Code, with zero setup. Content is the person's own rules, never Kay's.
- **B — A file each person keeps**: a Project file in the Claude app, or `CLAUDE.md` in Claude Code. Matches today's layer table ("personal rules a skill reads"), but costs setup on every surface.
- **C — No personal rules for roommates yet**: only Kay has a file; roommates get general suggestions.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**C — none for roommates yet**, with A as the path if they ask. Rationale: nothing in the seed says the roommates have rules, and the build-only-what's-decided rule applies. Kay keeps her Project file.
Confidence: 0.6, because roommates may well want dietary notes (allergies, vegetarian) as soon as they use suggestions. If wrong: if any roommate has a dietary rule on day one, A.

**ANS:** (by kayc26)
a

---
