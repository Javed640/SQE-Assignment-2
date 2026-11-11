"""Member 3 - White-box coverage / condition / MC-DC tests.

Expected results come from REQUIREMENTS.md (SRS), not from the code.
Tests marked WBC-xx. Some tests are EXPECTED to fail on the supplied code
because they expose real defects (do not change their expected values).
"""
import pytest
from registration import Student, Course, registration_decision, register_course, withdraw_course


def mk(dues=0, done=None, credits=0, regd=None):
    return Student("S001", set(done or []), credits, dues, set(regd or []))


def course(enrolled=0, cap=5, ch=3, prereq=None, code="CS201"):
    return Course(code, ch, cap, enrolled, set(prereq or []))


# ---- Branch coverage of validation (line 46-49) ----
def test_wbc_01_negative_dues_raises():            # line 46 True
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(mk(dues=-1), course())


# ---- MC/DC for line 48:  not(c1 and c2) or c3
# c1: 0 <= enrolled   c2: enrolled <= capacity   c3: capacity < 1
def test_wbc_02_mcdc_T1_all_valid():               # c1=T c2=T c3=F -> D=F
    assert registration_decision(mk(), course(enrolled=0, cap=5)) == "REGISTERED"


def test_wbc_03_mcdc_T2_enrolled_negative():       # c1=F c2=NE c3=F -> D=T
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk(), course(enrolled=-1, cap=5))


def test_wbc_04_mcdc_T3_enrolled_above_capacity():  # c1=T c2=F c3=F -> D=T
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk(), course(enrolled=6, cap=5))


def test_wbc_05_mcdc_T4_capacity_zero():           # c1=T c2=T c3=T -> D=T
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk(), course(enrolled=0, cap=0))


# ---- Remaining branches of registration_decision ----
def test_wbc_06_dues_block_true_branch():          # line 50 True
    assert registration_decision(mk(dues=5000), course()) == "DUES_BLOCK"


def test_wbc_07_already_registered_branch():       # line 52 True
    assert registration_decision(mk(regd=["CS201"]), course()) == "ALREADY_REGISTERED"


def test_wbc_08_prereq_missing_branch():           # line 54 True
    assert registration_decision(mk(), course(prereq=["CS101"])) == "PREREQUISITES_MISSING"


def test_wbc_09_credit_limit_branch():             # line 56 True
    assert registration_decision(mk(credits=18), course(ch=1)) == "CREDIT_LIMIT"


def test_wbc_10_full_course_should_waitlist():     # line 58/59 (SRS FR-08)
    assert registration_decision(mk(), course(enrolled=5, cap=5)) == "WAITLISTED"


# ---- register_course / withdraw_course branches ----
def test_wbc_11_register_waitlist_adds_id_once():  # lines 70-71 (FR-12)
    s, c = mk(), course(enrolled=5, cap=5)
    assert register_course(s, c) == "WAITLISTED"
    register_course(s, c)
    assert c.waitlist == ["S001"] and s.current_credits == 0 and c.enrolled == 5


def test_wbc_12_withdraw_decrements_enrolled():    # FR-13
    s, c = mk(credits=3, regd=["CS201"]), course(enrolled=1)
    assert withdraw_course(s, c) is True
    assert s.current_credits == 0 and c.enrolled == 0


# ---- check_credit_limit validation branches (lines 30-33), FR-02 ----
from registration import check_credit_limit


def test_wbc_13_invalid_current_credits():         # line 31
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 3)


def test_wbc_14_invalid_course_credits():          # line 33
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(10, 5)


def test_wbc_15_total_exactly_18_allowed():        # FR-01 (exposes '< 18' defect)
    assert check_credit_limit(15, 3) is True
