# ADR-0001: Split the system by area

- **Date**: 2026-11-20
- **Iteration**: 2
- **Status**: Draft
- **Deciders**: Kay (decides), Ari (Claude Opus 5.5, recommends)
- **Source**: [seed-2026-11-20-separating-the-system](seed-2026-11-20-separating-the-system.md)

**TL;DR**: Kitchen, workout, and restaurants each become one repo, one Neon project, and one Claude Code plugin (server and skills together), replacing today's single plugin in this repo. Recipes and home cooks move from food-journal to kitchen. personal-ai-system freezes and its stats stop.

---

## Context

The three areas have different users:

| Area | Users | Notes |
|---|---|---|
| Kitchen | Kay and two roommates | Shared household inventory, separate recipe inboxes, different languages. Setup must be short and cheap on tokens. Used from the phone. |
| Workout | Kay only | The coach needs to get smarter (its own seed later). |
| Restaurants | Kay only for now | Barely used today and needs a redesign (its own seed later). It may offer public read access later. |

What exists today (checked against `origin/main` at b917a60; iteration 1 was written from a checkout 59 commits behind):
- **This repo is already one plugin** ("Package the repo as a Claude Code plugin", PR #1): `.claude-plugin/plugin.json`, a `kay` marketplace listing it, and `.mcp.json` with the three servers' URLs from env vars. The servers are disabled in its project settings.
- **Nine skills**: manage-kitchen-inventory, clip-recipe, suggest-what-to-cook, check-nutrition, log-home-cooking, log-dining-out, log-ready-to-eat, coach-training, suggest-where-to-eat. `scripts/check_skills.py` keeps the loaded copies in sync, and `skills/RETIRED.txt` lists removed ones.
- **One profile per person** (decision log): one `PROFILE.md` read by every skill, plus guidance files (`TRAINING_GUIDANCE.md`) as Project files. The log already names packaging for others as "a direction, not a build".
- **Meals with check-ins**: log-home-cooking, log-dining-out, and log-ready-to-eat each record a meal (`start_meal` / `end_meal`, hunger and fullness) in food-journal. Home cooks are a separate record, linked to the dish catalog.
- **Databases**: kitchen uses `neondb` and food-journal `kayfoodlab`, both in Neon project `my-fridge-inventory`. Kay wants them in separate projects.

## Decision

1. **One repo = one plugin = one area.** Each server repo carries its own skills and plugin manifest, following the CIS 7000 `packaged` pattern (server plus skills in one installable thing). This replaces the single plugin in this repo.

   | Repo | Server | Skills | Users |
   |---|---|---|---|
   | kitchen-inventory | inventory, plus saved recipes and home cooks moved in | manage-kitchen-inventory, clip-recipe, suggest-what-to-cook, check-nutrition, log-home-cooking | Multi-user ([ADR-0003](0003-kitchen-multi-user-data-model.md)) |
   | workout-log | unchanged | coach-training | Kay |
   | food-journal | restaurants, visits, lists, dish catalog, meals (see QST-MEALS-HOME) | suggest-where-to-eat, log-dining-out, log-ready-to-eat | Kay; public reads later |

2. **Recipes and home cooks move to kitchen** (QST-HOME-COOKS: C). Saved recipes, the "this week" list, and the home-cook history move from `kayfoodlab` to kitchen's database. This **reverses** "Restaurants and recipes stay in one server and one database". What happens to the home cooks' dish-catalog links is QST-HOME-COOK-DISHES.
3. **Cross-area links live in skills, not between servers.** suggest-what-to-cook reads training from workout-log when that connector is installed and skips it otherwise. check-nutrition ships with kitchen (QST-NUTRITION-HOME: A). No server calls another.
4. **One Neon project per server.** The order matters:
   1. Copy recipes and home cooks from `kayfoodlab` to `neondb`. Both are in the same project, so it's a table copy.
   2. Move `kayfoodlab`, now restaurants only, to a new Neon project.

   A fresh project, not `personal-ai-auth`, which is left over from an earlier auth attempt.
5. **This repo freezes** (QST-HUB-SUNSET: A). Skills move to their area repos; this repo keeps README, map, and records until the personal website exists, with a note pointing to the three repos. The daily stats action stops. Skills move with their history (`check_skills.py` and `RETIRED.txt` go to each area repo, or are retired, per the build prompts).
6. **Auth on all three** is [ADR-0002](0002-oauth-through-neon-auth.md).

Not decided here: the coach redesign, the restaurant redesign, public read access, and the personal website. Each gets its own seed.

---

## Questions

### QST-NUTRITION-HOME: Which plugin carries check-nutrition?
- Status: answered
- Why asking: check-nutrition is already general (it reads a per-person `NUTRITION_PROFILE.md`) and is used by suggest-what-to-cook. In the wrong plugin, either roommates lose it or kitchen depends on a plugin they don't have.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Kitchen plugin**: it ships with suggest-what-to-cook. A person without a nutrition profile gets suggestions without nutrition rules.
- **B — Workout plugin**: it's Kay's training nutrition. Kitchen suggestions use it only when workout is installed, like training.
- **C — Its own plugin**: installed separately by anyone who wants it.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Kitchen plugin.** Rationale: its main caller is suggest-what-to-cook (skills/suggest-what-to-cook/SKILL.md), and its description already says it's for any person's rules, not Kay's.
Confidence: 0.7, because the roommates' use of it is a guess. If wrong: if nobody but Kay would ever write a nutrition profile, B keeps the kitchen plugin smaller.

**ANS:** (by kayc26)
A

---

### QST-HOME-COOKS: What happens to the home-cook journal?
- Status: answered
- Why asking: Kay said "just mark recipes as cooked" for kitchen. But food-journal holds Kay's existing home cooks (photos, thoughts, ratings), and log-food writes them. "Cooked recently" needs a source after the split.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Keep the history, stop logging**: existing home cooks stay in food-journal, read-only. Kitchen recipes get a cooked date, backfilled from home cooks linked to a recipe. log-food keeps only the restaurant side.
- **B — Keep both**: kitchen marks recipes cooked, and Kay can still journal a home cook in food-journal when she wants to. Two places record a cook.
- **C — Move the history to kitchen**: home cooks become a kitchen table owned by Kay.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Keep the history, stop logging.** Rationale: it matches "just mark recipes as cooked", loses no data, and avoids two records of one cook. Under the layer rule, two sources of "cooked recently" could disagree.
Confidence: 0.6, because I don't know how much Kay values journaling home cooks (photos, ratings). If wrong: if Kay wants to keep journaling them, B, with the kitchen cooked date as the only source for suggestions.

**ANS:** (by kayc26)
c

---

### QST-HUB-SUNSET: When does personal-ai-system stop?
- Status: answered
- Why asking: this repo holds the public README, the architecture map (`index.html`), and the daily stats action. The action reads each server's public `/stats`, and kitchen's will soon include roommates' counts.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Freeze now**: skills move to their repos; this repo keeps README, map, and records until the website exists, with a note pointing to the three repos. The stats action stops.
- **B — Freeze now, keep stats**: as A, but the stats action keeps running. That needs a decision on what kitchen's `/stats` may show with three users.
- **C — Archive now**: move the story to the website first, then archive.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Freeze now.** Rationale: the records (seed, ADRs) still need a home while the split happens, and the website doesn't exist yet. Stopping the stats action removes a public output that would soon count other people's data.
Confidence: 0.7, because the website timeline is unknown. If wrong: if Kay wants the live counts on the website, B, with `/stats` limited to non-personal totals.

**ANS:** (by kayc26)
a

---

### QST-MEALS-HOME: Where do meals with check-ins live?
- Status: answered
- Why asking: all three meal skills record a meal (hunger and fullness check-ins) in food-journal. log-home-cooking now moves to kitchen (QST-HOME-COOKS: C), so a home-cooked dinner would write the cook to kitchen and the meal to food-journal. Roommates using log-home-cooking would also need somewhere for meals, or a way to skip them.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Meals stay in food-journal, Kay only**: log-home-cooking records the meal only when the food-journal connector is present (Kay); roommates log the cook without check-ins. One meal history for Kay across home, out, and packaged.
- **B — Meals move to kitchen, per user**: every user gets meals; log-dining-out and log-ready-to-eat then write meals to kitchen too, so restaurants depends on kitchen.
- **C — Meals become their own small area**: a fourth server for eating check-ins, used by all three meal skills.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Meals stay in food-journal, Kay only.** Rationale: check-ins are Kay's mindful-eating practice (decision "Meals and mindful-eating check-ins"), and two of the three meal skills stay with food-journal. A keeps one meal history and uses the same "if the connector is present" link as training (decision 3).
Confidence: 0.6, because I don't know whether the roommates would want check-ins. If wrong: if a roommate wants check-ins, B; if meals grow beyond food (sleep, energy), C.

**ANS:** (by kayc26)
sunset those

---

### QST-HOME-COOK-DISHES: What happens to home cooks' dish-catalog links?
- Status: answered
- Why asking: each home cook links to a dish in the catalog, which stays in food-journal. The catalog is what lets "have I cooked this or had it out?" (`get_dish_history`) and restaurant dish search work across home and out.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Keep the dish name as text**: kitchen stores the dish name as written (and the recipe link when there is one). Cross home-and-out history is given up.
- **B — Copy the catalog into kitchen**: kitchen gets its own dish catalog. Two catalogs can drift apart.
- **C — Kitchen stores the food-journal dish id**: cross-server ids; kitchen can't check them, and they mean nothing to roommates.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Keep the dish name as text.** Rationale: decision 3 rules out servers depending on each other, B duplicates a fact (layer rule), and most home cooks that matter link to a saved recipe, which moves with them.
Confidence: 0.65, because I haven't measured how often Kay uses dish history across home and out. If wrong: if that cross history is something Kay uses weekly, B, with the catalog owned by kitchen.

**ANS:** (by kayc26)
b

---

### QST-MARKETPLACE: Where do people install the plugins from?
- Status: answered
- Why asking: today the `kay` marketplace in this repo lists one plugin. With three plugins in three repos and this repo frozen, roommates need one short install step.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Each area repo is its own marketplace**: a roommate runs `/plugin marketplace add kayc26/mcp-kitchen-inventory` and installs kitchen. Each repo is fully self-contained.
- **B — This repo keeps the `kay` marketplace**: it lists all three plugins from their repos. One place to look, but the frozen repo stays live.
- **C — A new small marketplace repo**: lists all three; this repo can be archived later.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Each area repo is its own marketplace.** Rationale: roommates only want kitchen, and A gives them one repo name; it matches the `packaged` course pattern (`extras/marketplace/`) and leaves nothing live in the frozen hub.
Confidence: 0.6, because I haven't checked how plugins installed this way show up in the Claude app versus Claude Code. If wrong: if Kay wants one place to install all three, C.

**ANS:** (by kayc26)
a

---

## Iterations

### Iteration 1 — 2026-11-20
- **Trigger**: seed chunked into ADRs.
- **Contributors**: Kay, Ari (Claude Opus 5.5).
- **Changes**: first draft; three questions.
- **Outcome**: Draft. Kay answered all three (NUTRITION-HOME A, HOME-COOKS C, HUB-SUNSET A).

### Iteration 2 — 2026-11-20
- **Trigger**: Kay's answers, and iteration 1 found to be written from a checkout 59 commits behind `origin/main`.
- **Contributors**: Kay, Ari (Claude Opus 5.5).
- **Changes**: Context rewritten from the current repo (existing plugin, nine skills, one profile per person, meals). Decision updated with the three answers: home cooks and log-home-cooking move to kitchen, check-nutrition ships with kitchen, this repo freezes. New questions: QST-MEALS-HOME, QST-HOME-COOK-DISHES, QST-MARKETPLACE.
- **Outcome**: Draft.
