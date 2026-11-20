# ADR-0001: Split the system by area

- **Date**: 2026-11-20
- **Iteration**: 1
- **Status**: Draft
- **Deciders**: Kay (decides), Ari (Claude Opus 5.5, recommends)
- **Source**: [seed-2026-11-20-separating-the-system](seed-2026-11-20-separating-the-system.md)

**TL;DR**: Kitchen, workout, and restaurants each become one repo, one Neon project, and one Claude Code plugin (server and skills together). Recipes move from food-journal to kitchen. personal-ai-system stops being the hub.

---

## Context

The three areas have different users:

| Area | Users | Notes |
|---|---|---|
| Kitchen | Kay and two roommates | Shared household inventory, separate recipe inboxes, different languages. Setup must be short and cheap on tokens. Used from the phone. |
| Workout | Kay only | The coach needs to get smarter (its own seed later). |
| Restaurants | Kay only for now | Barely used today and needs a redesign (its own seed later). It may offer public read access later. |

Today one hub repo (this one) holds all the skills, and the servers are split differently: recipes live in food-journal next to restaurants. Kay also wants kitchen and food-journal in separate Neon projects. Today both are databases (`neondb` and `kayfoodlab`) in one project, `my-fridge-inventory`.

## Decision (agreed in the seed)

1. **One repo = one plugin = one area.** Each server repo also carries its skills and plugin manifest, following the CIS 7000 `packaged` pattern (server plus skill in one installable thing) and the layout networking-log already uses.

   | Repo | Server | Skills | Users |
   |---|---|---|---|
   | kitchen-inventory | inventory, plus saved recipes moved in | manage-kitchen-inventory, clip-recipe, suggest-what-to-cook | Multi-user ([ADR-0003](0003-kitchen-multi-user-data-model.md)) |
   | workout-log | unchanged | coaching (to design) | Kay |
   | food-journal | restaurants, visits, lists, dish catalog, and existing home cooks | suggest-where-to-eat, log-food (restaurant side) | Kay; public reads later |

2. **Recipes move to kitchen.** saved recipes and the "this week" list move from `kayfoodlab` to kitchen's database. This **reverses** the decision "Restaurants and recipes stay in one server and one database". The dish catalog link between recipes and restaurants is given up; Kay didn't list it as something to keep.
3. **Cross-area links live in skills, not between servers.** suggest-what-to-cook reads training from workout-log when that connector is installed and skips it otherwise. No server calls another.
4. **One Neon project per server.** The order matters:
   1. Copy recipes from `kayfoodlab` to `neondb`. Both are in the same project, so it's a table copy.
   2. Move `kayfoodlab`, now restaurants only, to a new Neon project.

   A fresh project, not `personal-ai-auth`. That project is left over from an earlier auth attempt that didn't work out.
5. **Auth on all three** is [ADR-0002](0002-oauth-through-neon-auth.md).

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
