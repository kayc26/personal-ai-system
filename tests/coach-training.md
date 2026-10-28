# coach-training test cases

Real failures turned into checks. Run each in a new Food & Training chat, once with the
current skill (before) and once after a change (after). Record the date, the skill
commit, and pass or fail. A rewrite ships only when every case passes.

## 1. Lifting after a long cardio morning
Origin: 2026-10-25, the coach planned an afternoon delts/triceps/core session after a
morning 8K run.

Prompt: "I ran 8K this morning. What should I do this afternoon?"

Pass:
- No lifting session that afternoon; rest, mobility, or an easy walk instead.
- If it mentions the rest of the week, nothing heavy for legs the next morning either.

Fail: any lifting session that afternoon, or a session presented as optional extra
volume.

## 2. Moving or adding work between days
Origin: 2026-10-25, after Kay dropped the Sunday delts/triceps/core session, the coach
suggested moving lateral raises and triceps to the pull day with no reasoning. The
placement itself isn't necessarily wrong (it would train those muscles twice a week);
the failure was deciding without counting or checking.

Prompt: "I want more side delt and triceps work. Where should it go?"

Pass:
- States the current weekly sets for side delts and triceps (helper sets count half)
  and how many sessions a week train them.
- Proposes a placement with its reason (frequency, recovery, overlap with the day's
  other exercises) and the new set totals.
- Checks that each changed day still fits about 60 minutes.
- Waits for Kay's OK before calling set_program; if it's mid-block, suggests saving
  the change for the next block.

Fail: a placement with no set count or time check, or a program change applied without
asking.

## Results
| Date | Skill commit | Case 1 | Case 2 | Notes |
|---|---|---|---|---|
| 2026-10-28 | f25f2c2 (before) | Fail | Fail | 1: swapped in Upper B that afternoon and moved Lower B to the next day; offered a trimmed Lower B as the alternative. 2: gave the new totals (8 side delt, 8 to 9 triceps sets) but not the current ones, didn't half-count pressing for triceps; reasons and a 60-minute check were there, and it asked first, but it's mid-block and it proposed starting today. |
| 2026-10-28 | c45bc7d (after) | Pass | Pass | 1: no lifting, Lower B moved, no leg day next morning. But it planned runs from a stale cardio line in the program description (Thu run, Sun long run), and offered Lower A on the Monday after that long run, against its own rule. 2: correct counts (side delts 4.5, triceps 6.5, once a week), next block, waits; new totals 9.5 still under 10 and not flagged; time check hedged instead of reading logged session lengths. |
