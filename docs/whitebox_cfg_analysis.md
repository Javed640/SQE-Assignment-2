# White-box analysis — `registration_decision()`

**Phase 1 — Analysis & Graph Construction (tasks 1, 2, 5)**
**Phase 2 — Cyclomatic complexity & paths (tasks 3, 4, 6)**
**Phase 3 — Test implementation (tasks 7, 8)**

Target: `registration_decision()` in `registration.py`, lines 44–60.
Diagram: `docs/cfg.png` — regenerated with `python scripts/make_cfg.py`.

---

## 1. Phase 1 — locate the code and find the decision points

### 1.1 The function under analysis

```python
44: def registration_decision(student: Student, course: Course) -> str:
45:     """Evaluate registration without changing student or course state."""
46:     if student.outstanding_dues < 0:                                        # D1
47:         raise ValueError("Invalid dues")                                     # P1
48:     if not 0 <= course.enrolled <= course.capacity or course.capacity < 1:   # D2  (compound)
49:         raise ValueError("Invalid capacity or enrollment")                    # P2
50:     if student.outstanding_dues > 1000:                                      # D3
51:         return "DUES_BLOCK"                                                  # R1
52:     if course.code in student.registered_courses:                            # D4
53:         return "ALREADY_REGISTERED"                                          # R2
54:     if not prerequisites_satisfied(student.completed_courses, course.prerequisites):   # D5
55:         return "PREREQUISITES_MISSING"                                       # R3
56:     if not check_credit_limit(student.current_credits, course.credit_hours): # D6
57:         return "CREDIT_LIMIT"                                                # R4
58:     if course.enrolled > course.capacity:                                    # D7
59:         return "WAITLISTED"                                                  # R5
60:     return "REGISTERED"                                                      # R6
```

### 1.2 The short-circuit rule (task 2)

A compound condition is **not** one decision. Because Python evaluates
`and` / `or` with short-circuiting, the condition splits into a chain of
separate checks, the next one reached only when the previous one is true:

```python
if age >= 18 and has_id:      #  Check 1 (age >= 18)
    ...                       #      -> if true, Check 2 (has_id)
```

Line 48 is the only compound condition in the function:

```
D2 = not 0 <= course.enrolled <= course.capacity  or  course.capacity < 1
   = not (C2 and C3) or C4
        C2 = 0 <= course.enrolled              -> decision node D2a
        C3 = course.enrolled <= capacity       -> decision node D2b  (reached only when C2 is True)
        C4 = course.capacity < 1               -> decision node D2c  (reached only when C2 and C3 are True)
```

`not` binds to the result of the chained comparison, and the chained
comparison is itself Python shorthand for `C2 and C3`, so the expression is
exactly the two-level short-circuit above. Three atoms → three decision nodes.

### 1.3 Nodes and edges (tasks 1 and 5)

**N = 19 nodes**, numbered `n1 … n19` in the order execution reaches them:

| # | Node | Line | Kind | Statement / condition |
|---|---|---|---|---|
| n1 | `E` | — | entry | function entry |
| n2 | `D1` | 46 | decision | `outstanding_dues < 0` |
| n3 | `P1` | 47 | process | `raise ValueError("Invalid dues")` |
| n4 | `D2a` | 48 | decision | `0 <= enrolled` |
| n5 | `D2b` | 48 | decision | `enrolled <= capacity` |
| n6 | `D2c` | 48 | decision | `capacity < 1` |
| n7 | `P2` | 49 | process | `raise ValueError("Invalid capacity or enrollment")` |
| n8 | `D3` | 50 | decision | `outstanding_dues > 1000` |
| n9 | `R1` | 51 | return | `return "DUES_BLOCK"` |
| n10 | `D4` | 52 | decision | `code in registered_courses` |
| n11 | `R2` | 53 | return | `return "ALREADY_REGISTERED"` |
| n12 | `D5` | 54 | decision | `not prerequisites_satisfied(...)` |
| n13 | `R3` | 55 | return | `return "PREREQUISITES_MISSING"` |
| n14 | `D6` | 56 | decision | `not check_credit_limit(...)` |
| n15 | `R4` | 57 | return | `return "CREDIT_LIMIT"` |
| n16 | `D7` | 58 | decision | `enrolled > capacity` |
| n17 | `R5` | 59 | return | `return "WAITLISTED"` |
| n18 | `R6` | 60 | return | `return "REGISTERED"` |
| n19 | `X` | — | exit | single exit node |

**E = 27 edges** (`T` = condition true, `F` = condition false):

| # | Edge | # | Edge | # | Edge |
|---|---|---|---|---|---|
| 1 | `E → D1` | 10 | `D2c → D3` (F) | 19 | `D5 → D6` (F) |
| 2 | `D1 → P1` (T) | 11 | `P2 → X` | 20 | `R3 → X` |
| 3 | `D1 → D2a` (F) | 12 | `D3 → R1` (T) | 21 | `D6 → R4` (T) |
| 4 | `P1 → X` | 13 | `D3 → D4` (F) | 22 | `D6 → D7` (F) |
| 5 | `D2a → P2` (F) | 14 | `R1 → X` | 23 | `R4 → X` |
| 6 | `D2a → D2b` (T) | 15 | `D4 → R2` (T) | 24 | `D7 → R5` (T) |
| 7 | `D2b → P2` (F) | 16 | `D4 → D5` (F) | 25 | `D7 → R6` (F) |
| 8 | `D2b → D2c` (T) | 17 | `R2 → X` | 26 | `R5 → X` |
| 9 | `D2c → P2` (T) | 18 | `D5 → R3` (T) | 27 | `R6 → X` |

Every edge in the diagram is labelled with its node pair, so this table can be
checked one-to-one against `docs/cfg.png`.

---

## 2. Phase 2 — cyclomatic complexity

### 2.1 Formula 1 (edges and nodes)

```
V(G) = E − N + 2
     = 27 − 19 + 2
     = 10
```

### 2.2 Formula 2 (predicate nodes)

`P` counts decision nodes whose condition branches into two paths — here that
is every diamond: `D1, D2a, D2b, D2c, D3, D4, D5, D6, D7` → **P = 9**.

```
V(G) = P + 1
     = 9 + 1
     = 10
```

### 2.3 Consistency check

```
Formula 1  gives 10
Formula 2  gives 10            ✔ both formulas agree
```

Because the short-circuit rule was applied, the compound condition at line 48
contributes **three** predicate nodes rather than one; P = 9 = 7 obvious
`if` checks + 2 extra atoms of D2. (If instead one collapsed D2 back into a
single node, the graph would have N = 17, E = 23 and V(G) = 23 − 17 + 2 = 8 =
7 + 1; both numbers describe the same code and differ exactly by the two extra
atomic conditions. The expanded graph is the one used here, as the brief
requires.)

### 2.4 Independent basis paths (task 6)

Exactly **V(G) = 10** paths are needed. The set is built the standard way: the
first path follows every "false / fall-through" branch, and each further path
introduces exactly **one new edge**. That one-new-edge guarantee is what makes
the set linearly independent.

| Path | Full node route | New edge introduced | Feasible? | Test |
|---|---|---|---|---|
| BP1 | `E → D1 → P1 → X` | `D1 → P1` | yes | `test_bp1_dues_validation_raises` |
| BP2 | `E → D1 → D2a → P2 → X` | `D2a → P2` | yes | `test_bp2_enrolled_below_zero_raises` |
| BP3 | `E → D1 → D2a → D2b → P2 → X` | `D2b → P2` | yes | `test_bp3_enrolled_above_capacity_raises` |
| BP4 | `E → D1 → D2a → D2b → D2c → P2 → X` | `D2c → P2` | yes | `test_bp4_zero_capacity_raises` |
| BP5 | `E → … → D2c → D3 → R1 → X` | `D2c → D3` and `D3 → R1` | yes | `test_bp5_dues_block` |
| BP6 | `E → … → D4 → R2 → X` | `D3 → D4`, `D4 → R2` | yes | `test_bp6_already_registered` |
| BP7 | `E → … → D5 → R3 → X` | `D4 → D5`, `D5 → R3` | yes | `test_bp7_prerequisites_missing` |
| BP8 | `E → … → D6 → R4 → X` | `D5 → D6`, `D6 → R4` | yes | `test_bp8_credit_limit` |
| BP9 | `E → … → D7 → R5 → X` | `D6 → D7`, `D7 → R5`, `R5 → X` | **no — infeasible** | `test_bp9_waitlist_branch_is_unreachable` |
| BP10 | `E → … → D7 → R6 → X` | `D7 → R6`, `R6 → X` | yes | `test_bp10_registered` |

(BP5–BP8 also traverse the D2 atoms' *continue* edges `D2a → D2b`, `D2b → D2c`
and `D2c → D3`, which BP4 does not reach — so those edges are still new
relative to the set built so far.)

### 2.5 Edge coverage of the selected paths

Adding up the edges each path uses:

| Path | Edges of its route | Running edge count once the set is complete |
|---|---|---|
| BP1 | 1, 2, 4 | 3 |
| BP2 | 1, 3, 5, 11 | 5 new (3, 5, plus entry 1; 11 shared) |
| BP3 | 1, 3, 6, 7, 11 | 2 new (6, 7) |
| BP4 | 1, 3, 6, 8, 9, 11 | 2 new (8, 9) |
| BP5 | 1, 3, 6, 8, 10, 12, 14 | 2 new (10, 12; 14 reaches X) |
| BP6 | 1, 3, 6, 8, 10, 13, 15, 17 | 3 new (13, 15, 17) |
| BP7 | 1, 3, 6, 8, 10, 13, 16, 18, 20 | 3 new (16, 18, 20) |
| BP8 | 1, 3, 6, 8, 10, 13, 16, 19, 21, 23 | 3 new (19, 21, 23) |
| BP9 | 1, 3, 6, 8, 10, 13, 16, 19, 22, 24, 26 | **infeasible** (24, 26) |
| BP10 | 1, 3, 6, 8, 10, 13, 16, 19, 22, 25, 27 | 3 new (22, 25, 27) |

Total: **25 of 27 distinct edges are covered at least once** by the feasible
paths; every node is reached at least once except `R5` (n17).

The two uncovered edges — `D7 → R5` and `R5 → X` — are the two edges of the
infeasible branch, so they are not merely "not tested"; they are *proven
unreachable* by the next section. Remove that one dead branch (which is what
the FR-08 defect is about: `>` should be `>=`) and the same test set covers
**100 % of the edges of the reachable graph**.

### 2.6 Why BP9 is infeasible

To take `D7 → R5` an input must reach D7 with `enrolled > capacity`. To reach
D7 at all, BP's own guard chain must be passed, and that chain contains

```
D2a: 0 <= enrolled          -> True
D2b: enrolled <= capacity   -> True      (this is exactly how BP8/BP10 arrive at D7)
```

so `enrolled <= capacity` is already established before D7 is evaluated, and
`enrolled > capacity` can then never be true. In other words the two edges of
R5 are dead code: the validation on line 48 already rejects every input that
would satisfy line 58. A course that is full (`enrolled == capacity`) is
therefore reported as `REGISTERED` instead of `WAITLISTED` — a requirements
defect, recorded separately from this graph.

The consequence for the test suite: nine of the ten basis paths are executable,
and `tests/test_whitebox.py::test_bp9_waitlist_branch_is_unreachable` documents
the finding by asserting that the input which *would* drive D7 true (a full
course) instead raises the ValueError from P2. All ten tests pass.

---

## 3. Phase 3 — test cases for each path (task 7)

Each basis path needs input values that force the corresponding decision
outcomes. D1/D2 are driven by `outstanding_dues`, `enrolled` and `capacity`;
D3 requires a balance; D4–D6 need `registered_courses`, `completed_courses`/
`prerequisites` and `current_credits`; D7's route is BP10's fall-through.

| Test | Path | Inputs `(student, course)` | Expected outcome |
|---|---|---|---|
| BP1 | `E-D1-P1-X` | `dues = -1` | `ValueError("Invalid dues")` |
| BP2 | `E-D1-D2a-P2-X` | `dues = 0`, `enrolled = -1`, `capacity = 30` | `ValueError("Invalid capacity or enrollment")` (C2 false → P2) |
| BP3 | `E-D1-D2a-D2b-P2-X` | `dues = 0`, `enrolled = 31`, `capacity = 30` | same error (C2 true, C3 false → P2) |
| BP4 | `E-…-D2c-P2-X` | `dues = 0`, `enrolled = 0`, `capacity = 0` | same error (C2 true, C3 true, C4 true → P2) |
| BP5 | `E-…-D3-R1-X` | `dues = 1001`, `enrolled = 0`, `capacity = 30` | `"DUES_BLOCK"` |
| BP6 | `E-…-D4-R2-X` | `dues = 0`, `registered = {CS201}`, same course | `"ALREADY_REGISTERED"` |
| BP7 | `E-…-D5-R3-X` | `completed = {}`, `prerequisites = {MATH101}` | `"PREREQUISITES_MISSING"` |
| BP8 | `E-…-D6-R4-X` | `credits = 16`, course 3 credits | `"CREDIT_LIMIT"` (16 + 3 > 18) |
| BP9 | `E-…-D7-R5-X` | `enrolled = 31`, `capacity = 30` | raises (the branch is unreachable) |
| BP10 | `E-…-D7-R6-X` | all valid, `enrolled = 0` | `"REGISTERED"` |

Note on BP8: `check_credit_limit(16, 3)` returns False on the supplied code
(19 is not `< 18`) and would return False on a `<= 18` implementation too, so
the test is version-independent — it forces the D6 *true* edge without
depending on the buggy operator.

### 3.1 The test suite (task 8)

`tests/test_whitebox.py` contains ten functions, one per basis path, named
`test_bp<N>_<description>` so that every test maps to exactly one path:

```
$ python -m pytest tests/test_whitebox.py -v
tests/test_whitebox.py::test_bp1_dues_validation_raises PASSED
tests/test_whitebox.py::test_bp2_enrolled_below_zero_raises PASSED
tests/test_whitebox.py::test_bp3_enrolled_above_capacity_raises PASSED
tests/test_whitebox.py::test_bp4_zero_capacity_raises PASSED
tests/test_whitebox.py::test_bp5_dues_block PASSED
tests/test_whitebox.py::test_bp6_already_registered PASSED
tests/test_whitebox.py::test_bp7_prerequisites_missing PASSED
tests/test_whitebox.py::test_bp8_credit_limit PASSED
tests/test_whitebox.py::test_bp9_waitlist_branch_is_unreachable PASSED
tests/test_whitebox.py::test_bp10_registered PASSED

=========== 10 passed in 0.09s ===========
```

```
$ python -m pytest tests/ --cov=registration --cov-branch --cov-report=term-missing

Name              Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------
registration.py      57     16     26      3    70%   31, 33, 59, 65-72, 77-81
TOTAL                57     16     26      3    70%
=========== 10 passed in 0.19s ===========
```

Reading that number against the scope of this analysis:

* Inside the target function (`registration_decision`, lines 44–60) the suite
  covers **14 of 15 statements = 93 %** — the single miss is line 59 (`R5`).
* Every branch arc of the function is traversed except the two arcs of the
  dead branch, `58 → 59` and `59 → exit`, i.e. **20 of 22 arcs = 91 %**, and
  both missing arcs are the same finding as section 2.6. Coverage.py cannot
  measure the graph's *short-circuit* atoms directly (it sees line 48 as one
  branch), which is precisely why the path-level analysis is done over the
  expanded graph with executable tests rather than from the tool alone.
* The remaining module lines are outside the CFG under analysis: 65–81 are
  `register_course` / `withdraw_course` (state-changing wrappers over the
  same decision function) and 31/33 are `check_credit_limit`'s input guards.
  The deliberately 70 %-with-this-suite figure is the expected footprint of a
  ten-test basis-path suite, not an error in the design.

So: **10 of 10 tests pass**, and the coverage residual is the measurable
footprint of the infeasible path BP9 documented in section 2.6. The only way
to close line 59 and the `58 → 59` edge is to fix the `>` condition — writing
more tests cannot.

---

## 4. Artefacts

| Artefact | What it contains |
|---|---|
| `docs/cfg.png` | the CFG drawn above, nodes n1–n19 and all 27 edges labelled, generated by `scripts/make_cfg.py` |
| `docs/whitebox_cfg_analysis.md` | this document |
| `tests/test_whitebox.py` | ten basis-path tests, one per path, `10 passed` |
| `tests/conftest.py` | makes `import registration` resolve for any pytest invocation |
| `scripts/make_cfg.py` | regenerates `docs/cfg.png` (`python scripts/make_cfg.py`) |
