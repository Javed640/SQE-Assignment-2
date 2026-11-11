# White-Box Coverage and MC/DC Analysis

**Course:** SE3002 Software Quality Engineering, Assignment 2
**Author:** Member 3
**Branch:** `whitebox-coverage`
**System under test:** `registration.py`
**Test file:** `tests/test_whitebox_coverage.py`

---

## 1. Objective

This document measures the structural coverage achieved on `registration.py`, analyses atomic-condition coverage and Modified Condition/Decision Coverage (MC/DC) for a selected compound decision, and records the additional tests written to close coverage gaps. Expected results for every test are derived from `REQUIREMENTS.md` (the SRS), not from the implementation.

## 2. Coverage Measurement

Coverage was measured with `pytest-cov` using branch coverage enabled.

```bash
# Initial coverage (black-box suite only)
python -m pytest tests/test_blackbox.py --cov=registration --cov-branch --cov-report=term-missing

# Coverage after all suites
python -m pytest tests/ --cov=registration --cov-branch --cov-report=term-missing
```

| Stage | Test suites executed | Statement coverage | Branch coverage | Uncovered lines |
|---|---|---|---|---|
| Initial | `test_blackbox.py` (Member 1) | `__ %` | `__ %` | `__` |
| Intermediate | + `test_whitebox.py` (Member 2) | `__ %` | `__ %` | `__` |
| Final | + `test_whitebox_coverage.py` (Member 3) | `__ %` | `__ %` | `__` |

> Replace the `__` placeholders with the values printed by `pytest-cov` on your machine.

**Definitions**

- Statement coverage = executed statements / total statements x 100
- Branch coverage = executed branch outcomes / total branch outcomes x 100

## 3. Coverage Gaps and Unreachable Code

### 3.1 Reachable gaps closed by new tests

| Location | Construct | Closed by |
|---|---|---|
| Lines 46-47 | Negative dues raises `ValueError` | WBC-01 |
| Lines 48-49 | Invalid capacity / enrollment raises `ValueError` | WBC-03, WBC-04, WBC-05 |
| Line 31 | Invalid `current_credits` in `check_credit_limit` | WBC-13 |
| Line 33 | Invalid `new_credits` in `check_credit_limit` | WBC-14 |
| Line 78 | `withdraw_course` returns `False` when the course is not registered (FR-14) | WBC-16 |

### 3.2 Unreachable code (implementation defect)

Line 59 (`return "WAITLISTED"`) and lines 70-71 of `register_course` (waitlist append) **cannot be executed with any valid or invalid input**.

- Line 58 tests `course.enrolled > course.capacity`.
- Line 48 already raises `ValueError` whenever `enrolled > capacity`, so line 58 can never evaluate to True.
- SRS FR-08 requires `WAITLISTED` when `enrolled == capacity`, so the condition should be `>=`.

As a result, 100% statement and branch coverage is not achievable on the supplied code. Tests WBC-10 and WBC-11a to WBC-11d encode the SRS-correct behaviour and fail against the current implementation; they are retained as defect evidence and their expected values must not be altered.

## 4. Atomic Conditions

Atomic conditions in `registration_decision`:

| ID | Atomic condition | Line |
|---|---|---|
| c1 | `0 <= course.enrolled` | 48 |
| c2 | `course.enrolled <= course.capacity` | 48 |
| c3 | `course.capacity < 1` | 48 |
| c4 | `student.outstanding_dues < 0` | 46 |
| c5 | `student.outstanding_dues > 1000` | 50 |
| c6 | `course.code in student.registered_courses` | 52 |
| c7 | `prerequisites_satisfied(...)` | 54 |
| c8 | `check_credit_limit(...)` | 56 |
| c9 | `course.enrolled > course.capacity` | 58 |

## 5. MC/DC Analysis

**Selected decision (line 48):**

```python
if not 0 <= course.enrolled <= course.capacity or course.capacity < 1:
```

This is equivalent to `D = not (c1 and c2) or c3`. It was selected because it is the only compound decision in `registration_decision` with three atomic conditions.

### 5.1 Short-circuit behaviour

Python evaluates the chained comparison left to right and stops at the first False result. The `or` operator also stops as soon as its left operand is True. Therefore:

- If `c1` is False, `c2` is **not evaluated**.
- If `not (c1 and c2)` is True, `c3` is **not evaluated**.

### 5.2 Truth table (True / False / Not evaluated)

| Test | enrolled | capacity | c1 | c2 | c3 | Decision D |
|---|---|---|---|---|---|---|
| WBC-02 (T1) | 0 | 5 | T | T | F | F |
| WBC-03 (T2) | -1 | 5 | F | NE | NE | T |
| WBC-04 (T3) | 6 | 5 | T | F | NE | T |
| WBC-05 (T4) | 0 | 0 | T | T | T | T |

NE = not evaluated because of short-circuiting.

### 5.3 Independence pairs

A condition has an *independent effect* when two tests (a) differ in that condition, (b) give different decision outcomes, and (c) every other condition either keeps the same value or is not evaluated by Python (masked by short-circuiting), so it cannot be the cause of the change.

| Condition | Test pair | c1 | c2 | c3 | D | Justification |
|---|---|---|---|---|---|---|
| c1 | T1 vs T2 | T to F | T to NE | F to NE | F to T | Only c1 changes. Once c1 is False, `c1 and c2` is False and D is True regardless of c2 and c3, so Python skips both. The outcome change is therefore caused by c1. |
| c2 | T1 vs T3 | T (same) | T to F | F to NE | F to T | c1 is True in both, so c2 is evaluated and decides `c1 and c2`. c3 is skipped in T3 because D is already True. The outcome change is caused by c2. |
| c3 | T1 vs T4 | T (same) | T (same) | F to T | F to T | c1 and c2 are True and identical in both tests; only c3 differs, and D changes. This is the only pair where all other conditions are evaluated and equal. |

NE means "not evaluated". For T2 and T3 the skipped conditions still have logical values (c2 = True and c3 = False in T2; c3 = False in T3), which are identical to those in T1. This is why the pairs remain valid even if the NE entries are read as their logical values.

For three atomic conditions the minimum MC/DC set is n + 1 = 4 tests, which is exactly the set above. **MC/DC = 3 / 3 conditions = 100% for the decision on line 48.**

### 5.4 Note on measurement

`pytest-cov` reports statement and branch coverage only; it does not measure condition coverage or MC/DC. The figures in this section were derived manually from the truth table.

## 6. Added Tests

| Test ID | Target | SRS reference | Expected on current code |
|---|---|---|---|
| WBC-01 | Line 46 True: negative dues | FR-15 | Pass |
| WBC-02 | MC/DC T1: all conditions valid | FR-15 | Pass |
| WBC-03 | MC/DC T2: `enrolled < 0` (c1 False) | FR-15 | Pass |
| WBC-04 | MC/DC T3: `enrolled > capacity` (c2 False) | FR-15 | Pass |
| WBC-05 | MC/DC T4: `capacity < 1` (c3 True) | FR-15 | Pass |
| WBC-06 | Line 50 True: dues block | FR-04 | Pass |
| WBC-07 | Line 52 True: already registered | FR-05 | Pass |
| WBC-08 | Line 54 True: prerequisites missing | FR-06 | Pass |
| WBC-09 | Line 56 True: credit limit | FR-07 | Pass |
| WBC-10 | Line 58/59: full course is waitlisted | FR-08 | **Fail** (defect) |
| WBC-11a | Line 70: `register_course` on a full course returns `WAITLISTED` | FR-12 | **Fail** (defect) |
| WBC-11b | Line 71: student ID is appended to the waitlist | FR-12 | **Fail** (defect) |
| WBC-11c | Line 70: no duplicate entry when the ID is already waitlisted | FR-12 | **Fail** (defect) |
| WBC-11d | Waitlisting leaves credits, registered courses and `enrolled` unchanged | FR-12 | **Fail** (defect) |
| WBC-12 | `withdraw_course` decrements `enrolled` | FR-13 | **Fail** (defect) |
| WBC-16 | Line 78: withdrawing a course that is not registered returns `False`, no state change | FR-14 | Pass |
| WBC-13 | Line 31: invalid current credits | FR-02 | Pass |
| WBC-14 | Line 33: invalid course credits | FR-02 | Pass |
| WBC-15 | Total of exactly 18 credits is allowed | FR-01 | **Fail** (defect) |

## 7. Defects Exposed

| Failing test | Requirement | Location | Observed behaviour | Expected behaviour |
|---|---|---|---|---|
| WBC-10, WBC-11a to 11d | FR-08, FR-12 | Line 58 | `enrolled > capacity` is never True; `WAITLISTED` unreachable | `enrolled >= capacity` returns `WAITLISTED` |
| WBC-12 | FR-13 | `withdraw_course` | `course.enrolled` is not decremented | `enrolled` decreases by one |
| WBC-15 | FR-01 | Line 34 | `current + new < 18` rejects a total of 18 | `current + new <= 18` |

Additional defects visible in the source and expected to be caught by the black-box suite: prerequisites use `intersection` (any) instead of all required courses (FR-03), and the dues check uses `> 1000` instead of `> 0` (FR-04).

## 8. Actual Results

Paste the final `pytest-cov` terminal output here, followed by the pass/fail summary.

```
<paste output>
```

**Conclusion.** The added tests achieve 100% MC/DC on the selected decision and close all reachable statement and branch gaps. The remaining uncovered code (line 59, lines 70-71) is unreachable due to the defect described in Section 3.2.

### Note on test independence (WBC-11)
Each waitlist check is a separate test (WBC-11a to WBC-11d), so a failure in one assertion does not hide the others. All four currently fail for the same root cause: line 58 never returns `WAITLISTED` (Section 3.2), so `register_course` returns `REGISTERED` for a full course.
