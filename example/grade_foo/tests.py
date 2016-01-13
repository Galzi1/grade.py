"""Example test script using grade.py

Test functions are written as methods which take a module as an
argument. Behind the scenes this method will be run using both
the student and master modules. Then the output will be compared.

Test methods are generator functions, using the yield syntax. Any
expression that is yielded is considered to be a sub-test-case. If
the value is different using the student and master modules, this
will be recorded in the report, which is meant to be used directly
as feedback to students, along with human-written comments.
"""
from gradepy import Tester, Check, ECF


@ECF(tests=['add_one'])  # marks the function for error carried forward, more below
def test_add_one(module):
    """Demonstrates testing a simple function on a list of arguments."""

    # The yield statement below can be read as:
    # assert student.add_one(1) == master.add_one(1).
    yield module.add_one(1), 'This is simple: add_one(1)'
    # This line uses the simpler style, yielding an expression along with
    # a name for it. This name will get pludgged into the feedback:
    # "{name} should be {m_val}, but it is {s_val}" where m_val
    # and s_val are the values depending on which module is used.

    for i in range(2, 5):
        # The second style is to use the Check class. This has some advantages
        # including decreased redundancy. More importantly, if an exception is
        # generated by evaluating the expression, the test continues,
        # marking the exception of course.
        yield Check('add_one({i})')

    # Note that the namespace of `module` as well as this local name space will
    # be available during evaluation. All strings will be formatted by this
    # same name space, so {big} below will be replaced by 100 in the evaluation
    # as well as the feedback.
    big = 100
    yield Check('add_one({big})', "It's okay, {big} is a hard one")

    # add_one(100) causes an exception, but the test below will still run
    quip = 'takes one to know'
    yield Check('add_one(quip)')

    # If we want the value of a variable to be printed in the output,
    # rather than the name, we can put brackets around the variable.
    # Note that {quip} below will be replaced by 'takes one to know'
    # with quotations preserved.
    yield Check('add_one({quip})')


def test_foo(module):
    """Demonstrates testing a stateful class."""
    foo = module.Foo('2')

    yield Check('foo.arg')
    # Anything that you execute outside of Checks will have the expected
    # side effects. However, if the line below raises an exception, it will
    # prevent the completion of the test method.
    foo.bar()
    yield Check('foo.arg', 'after calling foo.bar()')

    # The code executed in Checks has side effects as well.
    yield Check('foo.bar()')
    yield Check('foo.arg', 'after calling foo.bar() twice')

# A very nice feature of grade.py is automated error carried forward.
# We track error carried forward using a decorator. The `tests` parameter
# indicates that the wrapped test method tests the given student functions.
# If the test finds errors, those functions will be added to a list of faulty
# functions to be replaced by the solution function for ECF. The `depends`
# parameter indicates which functions the currently tested functions depend on.
#
# If the test method below finds errors, and `add_one` has previously been
# found to have errors, then the test will be reexecuted using `ecf_mod`, a
# moudle based on the student module but with `add_one` replaced with the
# master implementation.
#
# Note that at present, we make no promises about exactly
# which functions may be changed during ECF. The current implementation
# never removes a correct solution function from the ECF module after it
# is added. It is not clear to me what the best way to handle this is.
@ECF(depends=['add_one'])
def test_add_two(module):
    yield Check('add_two(1)')
    yield Check('add_two(2)')

def test_divide(module):
    """Demonstrates how uncaught exceptions are handled.

    Also demonstrates the inferiority of python 2
    """
    yield module.divide(2, 4), 'divide(2, 4)'
    zero = module.divide(1, 0)  # exception, test_method ends
    yield zero, "we won't get this far..."


TESTS = [
         test_foo,
         test_divide,
         test_add_one,
         test_add_two
         ]

def main(student_file):
    from master import foo
    return Tester(foo, student_file).run_tests(*TESTS)


""""
OUTPUT:


======================================================================
Automated testing for flc37/foo.py
======================================================================

---------- test_foo ----------

foo.arg should be '222', but it is '22'
 Note: after calling foo.bar()

foo.arg should be '222222222', but it is '2222'
 Note: after calling foo.bar() twice

-------- test_add_one --------

This is simple: add_one(1) should be 2, but it is 0

add_one(4) should be 5, but it is 0

add_one(100) should be 101, but student code raised an exception:
  File "flc37/foo.py", line 15, in add_one
    1/0
ZeroDivisionError: integer division or modulo by zero
 Note: It's okay, 100 is a hard one

add_one(quip) should be 'takes one to know one', but it is 'takes one to know two'

add_one('takes one to know') should be 'takes one to know one', but it is 'takes one to know two'

-------- test_divide ---------

divide(2, 4) should be 0.5, but it is 0

Fatal exception in student code. Cannot finish test.
  File "grade_foo.py", line 109, in test_divide
    zero = module.divide(1, 0)  # exception, test_method ends
  File "flc37/foo.py", line 23, in divide
    return x / y
ZeroDivisionError: integer division or modulo by zero

-------- test_add_two --------

add_two(1) should be 3, but it is 1
Trying again with helper functions corrected.
Problem solved!

"""
