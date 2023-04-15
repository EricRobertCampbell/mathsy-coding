---
title: Some Counterintuitive Python `finally` Behaviour
pubDate: 2022-04-04
description: An explanation of some counterintuitive behaviour in a `finally` code block
---

## TL;DR

If you have a Python `try...except...finally` block and you return a value in the `try` or `catch`, that value will be ignored in favour of the value returned in the `finally` block.

## The Problem

I have recently been working on a semi-major refactoring of some of our core code. In particular, the shape of much of our data has been changing. Having these major changes has taught me a lot about our codebase, in particular areas where we need better test coverage!

However, as I was working on this, I came across a (to me) very counterintuitive piece of behaviour exhibited by a `try...except...finally` block, and so I thought that I would document it for posterity.

Here's the scenario. Imagine that you have some code representing a person, and you have some code which acts on it:

`embed:./resources/person1.py`

Obviously this is a bit dangerous (what if `get_id` throws an error?), so let's add some quick exception handling and print out a nice message:

`embed:./resources/diff12.diff`

Now here's where I ran into the problem. Imagine that you are now doing a refactor, because you realized that not everyone has a first and last name. You're also in a bit of a rush, so you forget to update that everywhere!

`embed:./resources/diff23.diff`

The problem is that if there's an exception, then `process_person` will enter the `except` block. Now, however, it will run into an issue - the `Person` object no longer has `first_name` or `last_name` attributes, and so another exception will be raised, this one unhandled. Now, instead of printing a nice error message and returning `None` (presumably to be dealt with by whatever is calling `process_person`), we have an exception being raised.

The insidious thing about this is that if everything goes well, you'll never even notice the issue - as long as `get_id` succeeds, the `except` block will never be entered and the new exception will never be raised. It's only when something goes wrong that it will go _really_ wrong!

So, fair enough - I messed up, so let's fix this. I want the actual id to be returned if possible, but if not, then no matter what happened, I want to return `None`.

`embed:./resources/diff34.diff`

This seems reasonable - if everything is good then return the id, if not then no matter what happens return `None`. However, the actual behaviour was that `None` was returned every time!

## The Solution

What is going on here? Well, it turns out that a `finally` block is, as you might expect, _always_ run - regardless of whether an error was thrown or not!

To be honest, as I write this out it seems obvious - of course a `finally` clause would run, regardless of whether there was an exception raised in the `try` - after all, the entire point of `finally` is that it does always run. Even the [Python documentation](https://docs.python.org/3/tutorial/errors.html) is explicit about this behaviour:

> [...] The finally clause runs whether or not the try statement produces an exception. [...]
>
> -   If the try statement reaches a break, continue or return statement, the finally clause will execute just prior to the break, continue or return statement’s execution.

So, how should I structure this? The solution that I used is to set the default value (taken on if there's an exception) before the `try...except...finally` block, and have the only `return` statement in the `finally` block.

`embed:./resources/diff45.diff`

## Conclusion

As the saying goes, "hours of debugging can save you minutes of reading the documentation". Hopefully this saves you some frustration if you ever run into a similar issue!
