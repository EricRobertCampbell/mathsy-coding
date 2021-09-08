---
title: Simple Python Unit Testing with unittest
date: 2020-12-13
description: A quick introduction to Python testing with unittest
---

This week, I've been doing a lot of development using our Django backend. As a result, I've also been writing a lot of unit tests. I find that writing code and the tests for the code concurrently help me to clarify my thinking, write  less buggy code, and have more confidence that the code that I wrote actually does what I expect!

## Setting Up Tests and Making Assertions

I've been using the excellent Python `unittest` module to write most of my tests. This module comes as part of Python and does what I need it to do. The documentation is up-to-date, fairly easy to understand, and perhaps as importantly, there is a large stockpile of answered questions about it on Stack Overflow!

The process of setting up tests and running them is fairly straightforward - you just create a regular Python file whose name starts with `test_` and write your tests in there! Each test suite (group of tests covering a particular aspect of your code) is a subclass of the `unittest.TestCase` class and the individual test cases (tests of one individual part of the suite) are methods of the class that you write whose name starts with `test_`. Within each test, you will create assertions about the behaviour of your system.

Generally, a test file will look something like the following:

```python
import unittest

class TestSomething(unittest.TestCase):
	def test_one_aspect(self):
		self.assertSomething(some parameters, "message if there is a failure")
```

In order to run this test, you would type something like the following in your terminal:

```bash
python -m unittest test_something_i_care_about.py
```

In each test, you will be adding one or more assertions about the behaviour you are trying to test. These assertions are special functions that are part of the `TestCase` class. The ones that I use most often are
- `self.assertEqual(a, b, 'Message')` - whether `a` and `b` are equal (same rules as `==`)
- `self.assertTrue(complex condition, 'message')` - whether a more complex condition is true
- `self.assertIn(elem, structure, "message")` - whether `elem in structure` is true. This is particularly useful for testing GraphQL responses.
- `self.assertRaises(Exception, 'message')` - tests whether something will raise the specified error. This is used with a context provider.

Of course, there are many others. Check the [official docs](https://docs.python.org/3/library/unittest.html).


## An Example - Testing an Addition Function
Let's walk through testing a simple addition function. 

`embed:code/v1-add.py`

Our tests should cover the behaviours that we want from our function:
1. Return a number
2. Work correctly for `int`s and `float`s
3. Fail on anything else

To test these, create a file `test_some_functions.py` in the same directory as `add.py`.

`embed:code/v1-test_some_functions.py`

To run the tests, type the following:
`embed:code/v1-output.txt`

 Note that in the output for `unittest`, a passing test is indicated with a full stop and a failing one with an `F`. In the even that an unhandled error is thrown during a test, it will be indicated with an `E`.
 
 Oh no! There are two failing tests! Note the information present in the output. The two failing tests indicate two problems - one with the actual function under test, and one with the tests themselves.
 
 The first problem is that our function doesn't actually raise a `TypeError` when it should! Note that due to the way that we wrote the test, we don't actually know which of the inputs that we passed in failed to raise the error - that would be a perfect place to output more information in the `message` parameter to our assertions. This should be easy enough to fix by adding some type checking to our function:
 
 `embed:code/v2-add.py`
 
 The other problem is actually with our tests. The tests correctly indicated that `0.3 != 0.30...04`. However, this is actually a problem with performing binary arithmetic, *not* with our addition function per se. Since we are going to be generally tolerant of this type of error, we should change our test to use the `assertAlmostEqual` assertion. This tests whether two numbers are close to each other - by default, whether they match to seven decimal places.
 
 `embed:code/v2-test_some_functions.py`
 
 Now that we have (hopefully) fixed our problems, let's run the tests again. This time, we're going to pass in the `--verbose` flag to get a little more information about the tests that we're running.
 
 `embed:code/v2-output.txt`

And there we have it! Our function works the way that we expect, and we can prove it with these tests!



## Sources

- [Official Documentation](https://docs.python.org/3/library/unittest.html)
- [Real Python - Getting Started with Testing in Python](https://realpython.com/python-testing/)
- [Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/tests/)
