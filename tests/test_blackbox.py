"""Black-box tests derived from REQUIREMENTS.md, not implementation branches.
Do not change expected outcomes to match faulty implementation.
"""
import copy
import pytest
from registration import Student, Course, check_credit_limit, prerequisites_satisfied, registration_decision, register_course, withdraw_course

CASES = [('ECP01', 'ECP', 'FR-01,FR-08', 'Valid registration, no prerequisites', 'decision', 10, 3, 0, '', '', False, 0, 3, 'REGISTERED'), ('ECP02', 'ECP', 'FR-04', 'Positive dues Rs. 1 block', 'decision', 10, 3, 1, '', '', False, 0, 3, 'DUES_BLOCK'), ('ECP03', 'ECP', 'FR-04', 'Positive dues Rs. 1001 block', 'decision', 10, 3, 1001, '', '', False, 0, 3, 'DUES_BLOCK'), ('ECP04', 'ECP', 'FR-15', 'Negative dues invalid', 'decision', 10, 3, -1, '', '', False, 0, 3, 'ValueError: Invalid dues'), ('ECP05', 'ECP', 'FR-05', 'Already registered', 'decision', 10, 3, 0, '', '', True, 0, 3, 'ALREADY_REGISTERED'), ('ECP06', 'ECP', 'FR-03,FR-06', 'All prerequisites completed', 'decision', 10, 3, 0, 'CS101|MATH101', 'CS101|MATH101', False, 0, 3, 'REGISTERED'), ('ECP07', 'ECP', 'FR-03,FR-06', 'Some prerequisites completed', 'decision', 10, 3, 0, 'CS101', 'CS101|MATH101', False, 0, 3, 'PREREQUISITES_MISSING'), ('ECP08', 'ECP', 'FR-03,FR-06', 'No prerequisites completed', 'decision', 10, 3, 0, '', 'CS101|MATH101', False, 0, 3, 'PREREQUISITES_MISSING'), ('ECP09', 'ECP', 'FR-07', 'Combined credits exceed maximum', 'decision', 16, 3, 0, '', '', False, 0, 3, 'CREDIT_LIMIT'), ('ECP10', 'ECP', 'FR-08', 'Full course waitlisted', 'decision', 10, 3, 0, '', '', False, 3, 3, 'WAITLISTED'), ('ECP11', 'ECP', 'FR-08', 'One available seat', 'decision', 10, 3, 0, '', '', False, 2, 3, 'REGISTERED'), ('ECP12', 'ECP', 'FR-02', 'Invalid course credits 0', 'decision', 10, 0, 0, '', '', False, 0, 3, 'ValueError: Invalid course credits'), ('ECP13', 'ECP', 'FR-15', 'Invalid capacity 0', 'decision', 10, 3, 0, '', '', False, 0, 0, 'ValueError: Invalid capacity or enrollment'), ('ECP14', 'ECP', 'FR-15', 'Enrollment exceeds capacity', 'decision', 10, 3, 0, '', '', False, 4, 3, 'ValueError: Invalid capacity or enrollment'), ('BVA01', 'BVA', 'FR-02', 'Current credits lower invalid -1', 'credit', -1, 3, 0, '', '', False, 0, 3, 'ValueError: Invalid current credits'), ('BVA02', 'BVA', 'FR-01', 'Current credits minimum 0', 'credit', 0, 3, 0, '', '', False, 0, 3, 'True'), ('BVA03', 'BVA', 'FR-01', 'Current credits minimum +1', 'credit', 1, 3, 0, '', '', False, 0, 3, 'True'), ('BVA04', 'BVA', 'FR-01', 'Total 17 allowed', 'credit', 14, 3, 0, '', '', False, 0, 3, 'True'), ('BVA05', 'BVA', 'FR-01', 'Total exactly 18 allowed', 'credit', 15, 3, 0, '', '', False, 0, 3, 'True'), ('BVA06', 'BVA', 'FR-01', 'Total 19 rejected', 'credit', 16, 3, 0, '', '', False, 0, 3, 'False'), ('BVA07', 'BVA', 'FR-02', 'Current credits maximum 18', 'credit', 18, 1, 0, '', '', False, 0, 3, 'False'), ('BVA08', 'BVA', 'FR-02', 'Current credits above max 19', 'credit', 19, 1, 0, '', '', False, 0, 3, 'ValueError: Invalid current credits'), ('BVA09', 'BVA', 'FR-02', 'Course credits below minimum 0', 'credit', 10, 0, 0, '', '', False, 0, 3, 'ValueError: Invalid course credits'), ('BVA10', 'BVA', 'FR-01', 'Course credits minimum 1', 'credit', 10, 1, 0, '', '', False, 0, 3, 'True'), ('BVA11', 'BVA', 'FR-01', 'Course credits maximum 4', 'credit', 10, 4, 0, '', '', False, 0, 3, 'True'), ('BVA12', 'BVA', 'FR-02', 'Course credits above maximum 5', 'credit', 10, 5, 0, '', '', False, 0, 3, 'ValueError: Invalid course credits'), ('BVA13', 'BVA', 'FR-04', 'Dues exactly zero', 'decision', 10, 3, 0, '', '', False, 0, 3, 'REGISTERED'), ('BVA14', 'BVA', 'FR-04', 'Dues 1 rupee', 'decision', 10, 3, 1, '', '', False, 0, 3, 'DUES_BLOCK'), ('BVA15', 'BVA', 'FR-08', 'Seats just below capacity', 'decision', 10, 3, 0, '', '', False, 2, 3, 'REGISTERED'), ('BVA16', 'BVA', 'FR-08', 'Seats exactly capacity', 'decision', 10, 3, 0, '', '', False, 3, 3, 'WAITLISTED'), ('BVA17', 'BVA', 'FR-15', 'Enrollment above capacity', 'decision', 10, 3, 0, '', '', False, 4, 3, 'ValueError: Invalid capacity or enrollment'), ('BVA18', 'BVA', 'FR-15', 'Capacity minimum 1', 'decision', 10, 3, 0, '', '', False, 0, 1, 'REGISTERED'), ('BVA19', 'BVA', 'FR-02', 'Both credit arguments invalid; current first', 'credit', -1, 0, 0, '', '', False, 0, 3, 'ValueError: Invalid current credits')]

@pytest.mark.parametrize('case', CASES, ids=[c[0] for c in CASES])
def test_ecp_and_bva(case):
    (test_id, technique, req, description, operation, current, new, dues,
     completed, required, already, enrolled, capacity, expected) = case
    if operation == 'credit':
        call = lambda: check_credit_limit(current, new)
    else:
        student = Student('S001', set(filter(None, completed.split('|'))), current, dues,
                          {'CS201'} if already else set())
        course = Course('CS201', new, capacity, enrolled, set(filter(None, required.split('|'))))
        before = (copy.deepcopy(student), copy.deepcopy(course))
        call = lambda: registration_decision(student, course)
    if expected.startswith('ValueError: '):
        with pytest.raises(ValueError, match='^' + expected.split(': ', 1)[1] + '$'):
            call()
    else:
        actual = call()
        expected_value = {'True': True, 'False': False}.get(expected, expected)
        assert actual == expected_value, f'{test_id} {req}: {description}'
    if operation == 'decision':
        assert (student, course) == before, 'FR-10: decision must not mutate state'

@pytest.mark.parametrize('completed,required,expected', [
    (set(), set(), True),
    ({'CS101','MATH101'}, {'CS101','MATH101'}, True),
    ({'CS101'}, {'CS101','MATH101'}, False),
    (set(), {'CS101'}, False),
], ids=['PR01_empty','PR02_all','PR03_some','PR04_none'])
def test_prerequisites(completed, required, expected):
    assert prerequisites_satisfied(completed, required) is expected

@pytest.mark.parametrize('case_id,dues,already,prereq_ok,credit_ok,full,expected', [('DT01', 1, True, False, False, True, 'DUES_BLOCK'), ('DT02', 0, True, False, False, True, 'ALREADY_REGISTERED'), ('DT03', 0, False, False, False, True, 'PREREQUISITES_MISSING'), ('DT04', 0, False, True, False, True, 'CREDIT_LIMIT'), ('DT05', 0, False, True, True, True, 'WAITLISTED'), ('DT06', 0, False, True, True, False, 'REGISTERED')],
 ids=[r[0] for r in [('DT01', 1, True, False, False, True, 'DUES_BLOCK'), ('DT02', 0, True, False, False, True, 'ALREADY_REGISTERED'), ('DT03', 0, False, False, False, True, 'PREREQUISITES_MISSING'), ('DT04', 0, False, True, False, True, 'CREDIT_LIMIT'), ('DT05', 0, False, True, True, True, 'WAITLISTED'), ('DT06', 0, False, True, True, False, 'REGISTERED')]])
def test_decision_priority(case_id,dues,already,prereq_ok,credit_ok,full,expected):
    student = Student('S001', {'CS101'} if prereq_ok else set(),
                      10 if credit_ok else 17, dues,
                      {'CS201'} if already else set())
    course = Course('CS201', 3, 3, 3 if full else 2, {'CS101'})
    before = (copy.deepcopy(student), copy.deepcopy(course))
    assert registration_decision(student,course) == expected, case_id
    assert (student,course) == before

def test_register_success_updates_all_fields():
    student = Student('S001', current_credits=10)
    course = Course('CS201',3,2,enrolled=0)
    assert register_course(student,course) == 'REGISTERED'
    assert student.registered_courses == {'CS201'}
    assert student.current_credits == 13
    assert course.enrolled == 1
    assert course.waitlist == []

def test_register_waitlist_only_and_no_duplicate():
    student = Student('S001', current_credits=10)
    course = Course('CS201',3,1,enrolled=1)
    assert register_course(student,course) == 'WAITLISTED'
    assert (student.current_credits, student.registered_courses, course.enrolled) == (10,set(),1)
    assert course.waitlist == ['S001']
    assert register_course(student,course) == 'WAITLISTED'
    assert course.waitlist == ['S001']

def test_register_rejection_does_not_mutate():
    student = Student('S001',current_credits=10,outstanding_dues=1)
    course = Course('CS201',3,3)
    before = (copy.deepcopy(student),copy.deepcopy(course))
    assert register_course(student,course) == 'DUES_BLOCK'
    assert (student,course) == before

def test_withdraw_success_decrements_enrollment():
    student = Student('S001',current_credits=13,registered_courses={'CS201'})
    course = Course('CS201',3,3,enrolled=2)
    assert withdraw_course(student,course) is True
    assert (student.current_credits,student.registered_courses,course.enrolled) == (10,set(),1)

def test_withdraw_nonregistered_no_mutation():
    student = Student('S001',current_credits=10)
    course = Course('CS201',3,3,enrolled=2)
    before = (copy.deepcopy(student),copy.deepcopy(course))
    assert withdraw_course(student,course) is False
    assert (student,course) == before

def test_validation_dues_before_capacity():
    student = Student('S001',outstanding_dues=-1)
    course = Course('CS201',3,0)
    with pytest.raises(ValueError,match='^Invalid dues$'):
        registration_decision(student,course)
