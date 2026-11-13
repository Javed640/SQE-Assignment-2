"""White-box basis-path test suite for registration_decision().

Phase 3 of the white-box assignment (tasks 7 and 8).

Each test below corresponds to exactly one independent basis path of the CFG
in docs/cfg.png, as tabulated in docs/whitebox_cfg_analysis.md (section 2.4).
The dependency is deliberately one-to-one and the naming makes it greppable:

    test_bp<N>_<text>   ==  basis path BP<N>

Test data is chosen so each test forces execution down exactly one route
(section 3 of the analysis doc lists the route and the input rationale).
All ten paths pass on the supplied implementation: BP9 documents the one
provably unreachable branch instead of pretending to execute it.
"""

import pytest

from registration import Course, Student, registration_decision


# --------------------------------------------------------------------------
# helpers - keep every test's intent visible in one line
# --------------------------------------------------------------------------
def course(code="CS201", credits=3, capacity=30, enrolled=0, prerequisites=None):
    return Course(code, credits, capacity, enrolled=enrolled,
                  prerequisites=prerequisites or set())


def student(dues=0, completed=None, current_credits=0, registered=None):
    return Student("S001", completed_courses=completed or set(),
                   current_credits=current_credits,
                   outstanding_dues=dues,
                   registered_courses=registered or set())


# --------------------------------------------------------------------------
# BP1 - E - D1 - P1 - X   (new edge: D1 -> P1)
# --------------------------------------------------------------------------
def test_bp1_dues_validation_raises():
    """BP1: dues < 0 forces D1 true -> raise ValueError('Invalid dues')."""
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student(dues=-1), course(capacity=30, enrolled=0))


# --------------------------------------------------------------------------
# BP2 - E - D1 - D2a - P2 - X   (new edge: D2a -> P2)
# --------------------------------------------------------------------------
def test_bp2_enrolled_below_zero_raises():
    """BP2: enrolled = -1 makes C2 (0 <= enrolled) false, so D2a short-circuits.

    With C2 false, ``not (C2 and C3)`` is already True, so the first operand of
    the ``or`` is true and the second atom ``capacity < 1`` (D2c) is never
    evaluated - the run goes straight to P2 via the D2a -> P2 edge.
    """
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student(), course(capacity=30, enrolled=-1))


# --------------------------------------------------------------------------
# BP3 - E - D1 - D2a - D2b - P2 - X   (new edge: D2b -> P2)
# --------------------------------------------------------------------------
def test_bp3_enrolled_above_capacity_raises():
    """BP3: C2 true (0 <= 31), C3 false (31 <= 30 fails) -> D2b -> P2."""
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student(), course(capacity=30, enrolled=31))


# --------------------------------------------------------------------------
# BP4 - E - D1 - D2a - D2b - D2c - P2 - X   (new edge: D2c -> P2)
# --------------------------------------------------------------------------
def test_bp4_zero_capacity_raises():
    """BP4: only test that reaches the third atom - capacity < 1 is true."""
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student(), course(capacity=0, enrolled=0))


# --------------------------------------------------------------------------
# BP5 - E - ... - D2c - D3 - R1 - X   (new edges: D2c -> D3, D3 -> R1)
# --------------------------------------------------------------------------
def test_bp5_dues_block():
    """BP5: a valid course plus dues above the implemented threshold."""
    assert registration_decision(
        student(dues=1001), course(capacity=30, enrolled=0)
    ) == "DUES_BLOCK"


# --------------------------------------------------------------------------
# BP6 - E - ... - D4 - R2 - X   (new edges: D3 -> D4, D4 -> R2)
# --------------------------------------------------------------------------
def test_bp6_already_registered():
    """BP6: the course code is already in registered_courses -> D4 true."""
    assert registration_decision(
        student(registered={"CS201"}), course(code="CS201")
    ) == "ALREADY_REGISTERED"


# --------------------------------------------------------------------------
# BP7 - E - ... - D5 - R3 - X   (new edges: D4 -> D5, D5 -> R3)
# --------------------------------------------------------------------------
def test_bp7_prerequisites_missing():
    """BP7: completed is empty and MATH101 is required -> prerequisites fail.

    With completed = {} the intersection test can never return True for a
    non-empty requirement, so this input reaches R3 on both the supplied and a
    corrected subset check.
    """
    assert registration_decision(
        student(), course(prerequisites={"MATH101"})
    ) == "PREREQUISITES_MISSING"


# --------------------------------------------------------------------------
# BP8 - E - ... - D6 - R4 - X   (new edges: D5 -> D6, D6 -> R4)
# --------------------------------------------------------------------------
def test_bp8_credit_limit():
    """BP8: 16 + 3 = 19 credits exceeds the 18-credit ceiling -> D6 true.

    Independent of the '<' vs '<=' question: 19 is outside 18 either way, so
    the D6 true edge is forced without depending on the buggy operator.
    """
    assert registration_decision(
        student(current_credits=16), course(capacity=30, enrolled=0)
    ) == "CREDIT_LIMIT"


# --------------------------------------------------------------------------
# BP9 - E - ... - D7 - R5 - X   (would add D7 -> R5, R5 -> X) - INFEASIBLE
# --------------------------------------------------------------------------
def test_bp9_waitlist_branch_is_unreachable():
    """BP9: the D7 -> R5 edge cannot be taken - documented, not hidden.

    BP9 itself is an UNREACHABLE path and is never executed by this test: to
    reach D7 at all, the line-48 guard chain must pass, and D2a and D2b
    together assert 0 <= enrolled <= capacity. D7 then asks the negation
    (enrolled > capacity), which can therefore never be true, so R5 (line 59)
    is dead code.

    What this test actually executes is the false edge D7 -> R6 (BP10's route)
    with the closest legal input, a full course (enrolled == capacity): the
    run returns "REGISTERED" and never hits R5. That assertion documents the
    finding; the infeasible path BP9 stays out of the executed set - see
    analysis section 2.6.
    """
    full_course = course(capacity=30, enrolled=30)
    assert registration_decision(student(), full_course) == "REGISTERED"


# --------------------------------------------------------------------------
# BP10 - E - ... - D7 - R6 - X   (new edges: D7 -> R6, R6 -> X)
# --------------------------------------------------------------------------
def test_bp10_registered():
    """BP10: the all-false fall-through route - the single 'REGISTERED' path."""
    assert registration_decision(
        student(current_credits=14), course(capacity=30, enrolled=10)
    ) == "REGISTERED"
