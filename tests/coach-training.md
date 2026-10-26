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
