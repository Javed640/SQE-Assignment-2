"""Member 3 - White-box coverage / condition / MC-DC tests.

Expected results come from REQUIREMENTS.md (SRS), not from the code.
Tests are labelled WBC-xx. Some tests are EXPECTED to fail on the supplied
code because they expose real defects (do not change their expected values).
NE = condition not evaluated because of Python short-circuiting.
"""
import pytest
from registration import (
    Student, Course, check_credit_limit,
    registration_decision, register_course, withdraw_course,
)


def mk(dues=0, done=None, credits=0, regd=None):
    return Student("S001", set(done or []), credits, dues, set(regd or []))


def course(enrolled=0, cap=5, ch=3, prereq=None, code="CS201", waitlist=None):
    return Course(code, ch, cap, enrolled, set(prereq or []), list(waitlist or []))


# ---- Branch coverage of validation (line 46-47) ----
def test_wbc_01_negative_dues_raises():             # line 46 True
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(mk(dues=-1), course())


# ---- MC/DC for line 48:  D = not(c1 and c2) or c3
# c1: 0 <= enrolled   c2: enrolled <= capacity   c3: capacity < 1
def test_wbc_02_mcdc_T1_all_valid():                # c1=T c2=T c3=F  -> D=F
    assert registration_decision(mk(), course(enrolled=0, cap=5)) == "REGISTERED"


def test_wbc_03_mcdc_T2_enrolled_negative():        # c1=F c2=NE c3=NE -> D=T
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk(), course(enrolled=-1, cap=5))


def test_wbc_04_mcdc_T3_enrolled_above_capacity():  # c1=T c2=F c3=NE -> D=T
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk(), course(enrolled=6, cap=5))


def test_wbc_05_mcdc_T4_capacity_zero():            # c1=T c2=T c3=T  -> D=T
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk(), course(enrolled=0, cap=0))


# ---- Remaining branches of registration_decision ----
def test_wbc_06_dues_block_true_branch():           # line 50 True
    assert registration_decision(mk(dues=5000), course()) == "DUES_BLOCK"


def test_wbc_07_already_registered_branch():        # line 52 True
    assert registration_decision(mk(regd=["CS201"]), course()) == "ALREADY_REGISTERED"


def test_wbc_08_prereq_missing_branch():            # line 54 True
    assert registration_decision(mk(), course(prereq=["CS101"])) == "PREREQUISITES_MISSING"


def test_wbc_09_credit_limit_branch():              # line 56 True
    assert registration_decision(mk(credits=18), course(ch=1)) == "CREDIT_LIMIT"


def test_wbc_10_full_course_should_waitlist():      # line 58/59 (FR-08)
    assert registration_decision(mk(), course(enrolled=5, cap=5)) == "WAITLISTED"


# ---- WBC-11: waitlist behaviour of register_course (FR-12), one check per test ----
def test_wbc_11a_register_full_course_returns_waitlisted():   # line 70 condition
    assert register_course(mk(), course(enrolled=5, cap=5)) == "WAITLISTED"


def test_wbc_11b_student_id_appended_to_waitlist():           # line 71
    s, c = mk(), course(enrolled=5, cap=5)
    register_course(s, c)
    assert c.waitlist == ["S001"]


def test_wbc_11c_no_duplicate_waitlist_entry():               # line 70, 'not in' False
    s, c = mk(), course(enrolled=5, cap=5, waitlist=["S001"])
    assert register_course(s, c) == "WAITLISTED"
    assert c.waitlist == ["S001"]


def test_wbc_11d_waitlisting_leaves_other_state_unchanged():  # FR-12
    s, c = mk(), course(enrolled=5, cap=5)
    register_course(s, c)
    assert s.current_credits == 0
    assert s.registered_courses == set()
    assert c.enrolled == 5


# ---- withdraw_course ----
def test_wbc_12_withdraw_decrements_enrolled():     # FR-13
    s, c = mk(credits=3, regd=["CS201"]), course(enrolled=1)
    assert withdraw_course(s, c) is True
    assert s.current_credits == 0 and c.enrolled == 0


def test_wbc_16_withdraw_not_registered_returns_false():  # line 78 True branch, FR-14
    s, c = mk(credits=3), course(enrolled=2)
    assert withdraw_course(s, c) is False
    assert s.current_credits == 3
    assert s.registered_courses == set()
    assert c.enrolled == 2


# ---- check_credit_limit validation branches (lines 30-33), FR-02 ----
def test_wbc_13_invalid_current_credits():          # line 31
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 3)


def test_wbc_14_invalid_course_credits():           # line 33
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(10, 5)


def test_wbc_15_total_exactly_18_allowed():         # FR-01 (exposes '< 18' defect)
    assert check_credit_limit(15, 3) is True


def test_wbc_16_withdraw_unregistered_course_returns_false():
    # line 78: course not in registered_courses
    student = Student(student_id='S001', current_credits=0, registered_courses=set())
    course = Course(code='CS201', credit_hours=3, capacity=3, enrolled=1)
    assert withdraw_course(student, course) is False
    assert (student.current_credits, student.registered_courses, course.enrolled) == (0, set(), 1)


def test_wbc_17_register_course_rejection_does_not_mutate():
    # branches 66->70 and 70->72: decision is not REGISTERED and not WAITLISTED
    student = Student(student_id='S001', current_credits=0, registered_courses=set(), outstanding_dues=5000)
    course = Course(code='CS201', credit_hours=3, capacity=3, enrolled=1, waitlist=[])
    assert register_course(student, course) == "DUES_BLOCK"
    assert (student.current_credits, student.registered_courses, course.enrolled, course.waitlist) == (0, set(), 1, [])


def test_wbc_18_over_enrolled_course_is_rejected_by_validation():
    # Documents why line 59 and lines 70-71 are unreachable: line 49 raises
    # ValueError for enrolled > capacity before the waitlist check at line 58.
    import pytest
    student = Student(student_id='S001', current_credits=0, registered_courses=set())
    course = Course(code='CS201', credit_hours=3, capacity=3, enrolled=4, waitlist=[])
    with pytest.raises(ValueError):
        register_course(student, course)
    assert course.waitlist == []

from unittest.mock import patch

def test_wbc_19_waitlist_branch_via_mock():
    """Cover line 70 True branch and line 71 in register_course() via white-box mocking."""
    student = Student("S99", "Test Student", current_credits=0, outstanding_dues=0)
    course = Course("CS999", credit_hours=3, capacity=1, enrolled=1)
    with patch("registration.registration_decision", return_value="WAITLISTED"):
        decision = register_course(student, course)
    assert decision == "WAITLISTED"
    assert "S99" in course.waitlist
