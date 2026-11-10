# Member 1 – Black-Box Test Execution Results

Source of expected results: `REQUIREMENTS.md` v1.0. Original `registration.py` was NOT modified.

Command: `python -m pytest tests/test_blackbox.py -q`

**Actual execution: 49 tests; 37 passed; 12 failed.**

## Failed tests (potential defects)

- `test_ecp_and_bva[ECP02]` — AssertionError: ECP02 FR-04: Positive dues Rs. 1 block
- `test_ecp_and_bva[ECP07]` — AssertionError: ECP07 FR-03,FR-06: Some prerequisites completed
- `test_ecp_and_bva[ECP10]` — AssertionError: ECP10 FR-08: Full course waitlisted
- `test_ecp_and_bva[BVA05]` — AssertionError: BVA05 FR-01: Total exactly 18 allowed
- `test_ecp_and_bva[BVA14]` — AssertionError: BVA14 FR-04: Dues 1 rupee
- `test_ecp_and_bva[BVA16]` — AssertionError: BVA16 FR-08: Seats exactly capacity
- `test_prerequisites[PR03_some]` — AssertionError: assert True is False
- `test_decision_priority[DT01]` — AssertionError: DT01
- `test_decision_priority[DT05]` — AssertionError: DT05
- `test_register_waitlist_only_and_no_duplicate` — AssertionError: assert 'REGISTERED' == 'WAITLISTED'
- `test_register_rejection_does_not_mutate` — AssertionError: assert 'REGISTERED' == 'DUES_BLOCK'
- `test_withdraw_success_decrements_enrollment` — assert (10, set(), 2) == (10, set(), 1)

## Suggested GitHub Issues (group by root cause)

1. **FR-01**: exact 18 credits incorrectly rejected (`BVA05`).
2. **FR-03/FR-06**: partial prerequisite completion incorrectly accepted (`ECP07`, `PR03_some`).
3. **FR-04**: positive dues Rs. 1 incorrectly accepted (`ECP02`, `BVA14`, `DT01`, failed register state).
4. **FR-08/FR-12**: full course incorrectly registered instead of waitlisted (`ECP10`, `BVA16`, `DT05`, waitlist state).
5. **FR-13**: withdrawal does not decrement course enrollment.

Create GitHub Issues with test IDs, requirements, expected vs actual, and steps to reproduce. Do not fix `registration.py` on the black-box branch.
