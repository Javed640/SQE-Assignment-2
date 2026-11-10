# SE3002 Assignment 2 — Student Registration Module

This is the **system under test** for black-box and white-box testing, not a reference-correct solution.

## Files
- `registration.py`: Python application to test.
- `REQUIREMENTS.md`: authoritative functional requirements, status strings, and sample scenarios.
- `requirements.txt`: dependencies for test development.

## Getting started
```bash
python -m pip install -r requirements.txt
python -c "from registration import Student, Course, register_course; print(register_course(Student('S001'), Course('CS201', 3, 30)))"
```

## Suggested student workflow
1. Derive ECP/BVA/decision table tests from `REQUIREMENTS.md` **without using implementation behavior as the expected result**.
2. Create `tests/test_blackbox.py`, execute the cases, and log suspected defects as GitHub Issues.
3. Inspect the code and develop `tests/test_whitebox.py` to exercise decisions, branches, conditions, and basis paths.
4. Document CFG and manual MC/DC pairs for a selected function.
5. Record failing tests faithfully. Do not alter expected results to force tests to pass.
6. Make any defect fixes in a separate Pull Request with accompanying regression tests.

Some tests may fail against the supplied source. This is intentional for the exercise.

## Member 1 — Black-box testing

Test design is based on `REQUIREMENTS.md`, not the implementation. The original `registration.py` must remain unchanged during initial testing.

- `tests/test_blackbox.py`: ECP, BVA, decision-table, state-transition, and no-mutation tests.
- `docs/blackbox_test_design.xlsx`: requirements traceability and ECP/BVA cases.
- `docs/decision_table.xlsx`: registration decision priority rules and test mapping.

Run from the project root:

```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_blackbox.py -v
```

Some tests may fail because the starter implementation deliberately contains defects. Record actual results and create GitHub Issues with test IDs and reproduction steps. Do not change the expected results to make tests pass.

### Recorded initial black-box execution

The initial local run produced **37 passing and 12 failing tests** out of 49. See `docs/blackbox_execution_results.md`. Re-run on your own machine before reporting final results.
