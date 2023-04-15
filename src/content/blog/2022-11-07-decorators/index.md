---
title: Decorators in Python
pubDate: 2022-11-07
description: Creating our own Python decorators
---

In this post, we're going to look at how we can create decorators - Python functions that themselves modify and return functions!

## Functions as First-Class Data Types

Most people who program in Python are familiar with the basic data types that Python offers: things like `int`, `str`, `list`, and others. They can easily write code that takes these values in and modifies them, and are very comfortable writing functions to make these operations a little easier. Less well-known and well-used is the fact that _functions themselves_ are first class data types! That means that we can pass them in as arguments to a function, modify them, and generally just treat them in the same way that we would, say, an integer.

Why would we do this? Throughout this post I hope to convince you that writing code that modifies functions can make your code mode readable, more efficient, and just generally better.

First, let's take a look at a simple example. Say we are writing a function to perform some sort of complex operation:

```python
def do_something():
    print("I am doing something complex")
```

Unfortunately, it's not being called when we expect. What we'd really like to do is to log when it runs, so that we can see what is going on. However, we really don't want to create a new function like `logged_do_something` and then go through our entire codebase replacing `do_something` with `logged_do_something` - that is wildly inefficient and just general bad practice. We could put the logging right into the body of the function, but what we'd really like to do is create something general-purpose which we can use with the next misbehaving function. So what can we do? Well, we could just replace the `do_something` function right where it is defined!

```python
def do_something():
    print("I am doing something complex")

def log_function(func):
    def function_with_logging():
        print(f"I am about to call function `{func.__name__}`")
        func()
        print(f"I just finished calling `{func.__name__}`")
    return function_with_logging

do_something = log_function(do_something) # replace the regular version with the logged version

do_something()
```

    I am about to call function `do_something`
    I am doing something complex
    I just finished calling `do_something`

So what exactly did we do here? We defined a new function, `log_function`, which takes in a _function_ and returns a new version of that function, with the additional logging behaviour that we want. We then called it on the original `do_something` function and replaced the original version with the logged version. Exactly what we wanted.

As it turns out, that pattern taking in a function and creating a new one from it with some new desired behaviour is exactly what decorators are for! In fact, we can take `log_function` and make it a decorator exactly as it is written:

```python
def log_function(func):
    def function_with_logging():
        print(f"I am about to call function `{func.__name__}`")
        func()
        print(f"I just finished calling `{func.__name__}`")
    return function_with_logging

@log_function
def do_something():
    print("I am doing something complex")

do_something()
```

    I am about to call function `do_something`
    I am doing something complex
    I just finished calling `do_something`

The `@` syntax _decorates_ the `do_something` function with `log_function`, automatically calling it and replacing the 'original' `do_something` with the decorated version. Simple, clean, and easy to understand!

## Return Values and Arguments

The way that we have it written right now has a few shortfalls - namely, it does not correctly deal with the return values of the decorated function, nor does it allow for arguments. We'll fix both of those.

### Return Values

The first issue is that the decorated version does not return any value! Let's see this in action:

```python
@log_function
def get_active_user():
    # some network call here
    return 7 # maybe this is the ID of the active user

id = get_active_user()
print(f"Returned id was {id}")
```

    I am about to call function `get_active_user`
    I just finished calling `get_active_user`
    Returned id was None

We get the ID, but don't store it! The issue is that in the inner function that we create in `log_function`, we _call_ the function, but never store or return the value! Luckily, that's an easy fix:

```python
def log_function(func):
    def function_with_logging():
        print(f"I am about to call function `{func.__name__}`")
        return_value = func() # now we store the original return value
        print(f"I just finished calling `{func.__name__}`")
        return return_value # and here we pass it back, as expected!
    return function_with_logging

@log_function
def get_active_user():
    # some network call here
    return 7 # maybe this is the ID of the active user

id = get_active_user()
print(f"Returned id was {id}")
```

    I am about to call function `get_active_user`
    I just finished calling `get_active_user`
    Returned id was 7

### Dealing with Arguments

Our decorator also does not deal correctly with any arguments passed into the original function. Again, let's see this in action:

```python
@log_function
def create_user_password(user_id):
    """ Create a completely secure password for the user """
    return f"password_{user_id}"

print(f"Secure password for user with id 7 is {create_user_password(7)}")
```

    ---------------------------------------------------------------------------

    TypeError                                 Traceback (most recent call last)

    /tmp/ipykernel_1023/2828063107.py in <module>
          4     return f"password_{user_id}"
          5
    ----> 6 print(f"Secure password for user with id 7 is {create_user_password(7)}")


    TypeError: function_with_logging() takes 0 positional arguments but 1 was given

So in fact our logging function immediately breaks on invocation! Why is this the case? While the error message displayed here doesn't show the exact cause of the error, we can take a look at `log_function` to see what's happening:

```python
def log_function(func):
    def function_with_logging():
        print(f"I am about to call function `{func.__name__}`")
        return_value = func() # here's the problem!
        print(f"I just finished calling `{func.__name__}`")
        return return_value
    return function_with_logging
```

On the fourth line, we call `func` (whatever that is) with _no arguments_! However, the function that we're decorating, `create_user_password`, takes in an argument - namely the user's id. Now, a naive solution would be to modify the `log_function` to take in this id parameter:

```python
def log_function(func):
    def function_with_logging(user_id):
        print(f"I am about to call function `{func.__name__}`")
        return_value = func(user_id) # here's the problem!
        print(f"I just finished calling `{func.__name__}`")
        return return_value
    return function_with_logging

@log_function
def create_user_password(user_id):
    """ Create a completely secure password for the user """
    return f"password_{user_id}"

print(f"Secure password for user with id 7 is {create_user_password(7)}")
```

    I am about to call function `create_user_password`
    I just finished calling `create_user_password`
    Secure password for user with id 7 is password_7

This actually works, but what we've really done is just shift the problem. By manually specifying that the function to be decorated must take a single positional parameter, `user_id`, we've now restricted its use to only functions that match that call signature! No, what we need is a more general approach that allows any arguments whatsoever to be passed to the inner function. Luckily, thanks to the `*args` and `**kwargs` arguments, we can do exactly that!

```python
def log_function(func):
    def function_with_logging(*args, **kwargs):
        print(f"I am about to call function `{func.__name__}`")
        return_value = func(*args, **kwargs) # fixed - we now just pass down any arguments to the original!
        print(f"I just finished calling `{func.__name__}`")
        return return_value
    return function_with_logging
```

```python
@log_function
def get_active_user():
    # some network call here
    return 7 # maybe this is the ID of the active user

print(f"Got active user id {get_active_user()}")
```

    I am about to call function `get_active_user`
    I just finished calling `get_active_user`
    Got active user id 7

```python
@log_function
def create_user_password(user_id):
    """ Create a completely secure password for the user """
    return f"password_{user_id}"

print(f"Secure password for user is {create_user_password(7)}")
```

    I am about to call function `create_user_password`
    I just finished calling `create_user_password`
    Secure password for user is password_7

And so we can see that our logging function works with any function now, regardless of the number or type of its parameters!

In fact, this ability to check the arguments passed into a function is incredibly useful, and one that I use quite frequently to make sure that functions are being called with the arguments that I expect. A decorator that does that is as follows:

```python
def check_arguments(func):
    def new_func(*args, **kwargs):
        print(f"Function {func.__name__} called with {args=}, {kwargs=}")
        return func(*args, **kwargs)
    return new_func


@check_arguments
def some_activity(id, name, status):
    pass

some_activity("Bob", 7, status="FLIBBERTIGIBBET") # oh no, I mixed up name and id!
```

    Function some_activity called with args=('Bob', 7), kwargs={'status': 'FLIBBERTIGIBBET'}

## Decorators with Arguments

If all decorators could do is what we have seen so far, they would be an incredibly powerful addition to the Python ecosystem. However, they are still more powerful! You can actually create decorators that themselves take arguments, allowing you to further customize their behaviour! First, let's see what this will look like, then we'll talk about exactly what needs to happen programmatically to do that, and then we'll actually do it.

Let's say that we wanted to be able to delay the call to any function. Maybe we're hitting a rate-limited API, or maybe we're just trying to trick the user into thinking that we're doing some sort of complex calculation when we're really not. Ideally, we would be able to specify the length of the delay. The function definition should look like this:

```python
@delay(seconds=1)
def make_api_call():
    pass
```

Notice that before, what followed the `@` of a decorator was the base function itself, not a function call like we're doing above. What this means is that we need to create a function `delay` that, when called, _returns a decorator_! The function will also create a [closure](<https://en.wikipedia.org/wiki/Closure_(computer_programming)>) containing the value that we passed in, allowing us to use it in the returned decorator.

```python
import time

def delay(seconds):
    # now we need to create and return a decorator
    def decorator(func):
        def modified_function(*args, **kwargs):
            print(f"About to sleep for {seconds} second{'s' if seconds > 1 else ''}") # this has access to the `seconds` variable - closure!
            time.sleep(seconds)
            print(f"Done sleeping")
            return func(*args, **kwargs)
        return modified_function
    return decorator

@delay(seconds=1)
def make_api_call():
    print("Just made an API call")

@delay(seconds=2)
def make_different_api_call():
    print("Just made a different API call")

make_api_call()
print('\n')
make_different_api_call()
```

    About to sleep for 1 second
    Done sleeping
    Just made an API call


    About to sleep for 2 seconds
    Done sleeping
    Just made a different API call

This certainly looks complicated! What we've done is create a function that defines a function which itself takes a function which then creates a modified function and returns it - even just typing it out makes it sound crazy! The key is to take it in steps. Again, our outer function (`delay`), creates a closure around the passed in value and uses that to create a decorator, which is then returned. The decorator has the same shape as all of the rest of the decorators that we've created - it takes in a function, creates a new one from that, and returns it.

## Decorators with Optional Arguments

Now let's add one additional layer of complexity: a decorator which can be called with or without arguments! As an example, let's say that we have some events that happen - maybe we're running a web server and the events are requests. We would like to give different departments in our company the ability to write their own event handlers independently and have them all stored in a registry of some sort. Most of the handlers are asynchronous (e.g. sending an email about the event) - it's not really important that they be run immediately. However, some event handlers are synchronous (like logging a failed payment) - it's extremely important that they be run immediately! We'll create a decorator that, when used with no arguments registers the function in the reqular registry, but when called with a `priority_handler=True` parameter registers it with the synchronous registry. Again, before writing the code let's imagine how this will look and talk about what we'll need to do.

```python
@register_event_handler
def regular_event_handler(event): # this one goes in the regular registry
    pass

@register_event_handler(priority_handler=True)
def important_event_handler(event): # this one goes in the synchronous registry
    pass
```

Knowing what we now know, it would be trivial to write a decorator that does either one of these things. In the first case (no arguments), we just create a regular decorator. In the second case (with arguments), we create a function which itself returns a decorator. How do we discriminate between these cases? Well, we can look at the arguments that get passed in! If we are calling it as a 'regular' decorator, then the function will be passed in. If we are calling it with arguments, then we'll get the `priority_handler` argument. We can use this to decide between our cases!

```python
# register_event_handler.py

regular_registry = []
priority_registry = []

def register_event_handler(_func=None, *, priority_handler=False):
    def decorator(func):
        def inner_function(*args, **kwargs):
            return func(*args, **kwargs)
        return inner_function

    # if _func is None, then it was called with arguments - we should return the decorator
    if _func == None:
        actual_function = decorator
    else: # called with no arguments - return the inner function
        actual_function = decorator(_func)

    # when the function is defined, add it to the appropriate registry
    if priority_handler == True:
        priority_registry.append(actual_function)
    else:
        regular_registry.append(actual_function)

    return actual_function

@register_event_handler
def regular_handler(event):
    pass

print(f"After registering `regular_handler`: \n{regular_registry=}\n{priority_registry=}")

@register_event_handler(priority_handler=True)
def priority_handler(event):
    pass
print(f"\nAfter registering `priority_handler`:\n{regular_registry=}\n{priority_registry=}")
```

    After registering `regular_handler`:
    regular_registry=[<function register_event_handler.<locals>.decorator.<locals>.inner_function at 0x7f082c221b80>]
    priority_registry=[]

    After registering `priority_handler`:
    regular_registry=[<function register_event_handler.<locals>.decorator.<locals>.inner_function at 0x7f082c221b80>]
    priority_registry=[<function register_event_handler.<locals>.decorator at 0x7f082c2555e0>]

Some important notes:

-   Our `register_event_handler` function has all optional arguments - without this, we have trouble distinguishing between the different cases
-   The _only_ positional argument is (possible) the function. We enforce this with the special '\*' argument, which ensures that all subsequent arguments are obligate keyword arguments.

## Making Your Life Easier with `functools`

One thing you may have noticed from the previous example is that the names for the decorated functions are not at all descriptive! In fact, it gets worse than that - the docstring from the decorated function is not the same as what we wrote, the name is different, and a few other helpful things are missing. For instance:

```python
def some_decorator(func):
    """ I am the decorator """
    def inner(*args, **kwargs):
        """ I am an inner function"""
        return func(*args, **kwargs)
    return inner

@some_decorator
def some_function():
    """ I am the function which we care about """
    pass

print(f"Name: {some_function.__name__}")
help(some_function)
```

    Name: inner
    Help on function inner in module __main__:

    inner(*args, **kwargs)
        I am an inner function

While it is technically true that the actual function we are calling is the inner one that we define in the decorator, that's not really what we care about. We'd really like to see the docstrings (&c.) from the function as we defined it. Although we could manually set these as part of the decorator, there's a far easier solution - using the `wraps` decorator from the excellent and tragically underused `functools` library! This decorator is applied to the inner function (the one that you return), and applies all of the ancillary pieces of information to this new function so that it behaves the way that we'd expect.

```python
from functools import wraps

def some_decorator(func):
    """ I am the decorator """
    @wraps(func) # this moves all of the information over!
    def inner(*args, **kwargs):
        """ I am an inner function"""
        return func(*args, **kwargs)
    return inner

@some_decorator
def some_function():
    """ I am the function which we care about """
    pass

print(f"Name: {some_function.__name__}")
help(some_function)
```

    Name: some_function
    Help on function some_function in module __main__:

    some_function()
        I am the function which we care about

And as you can see, the wrapped function now behaves in the way that we expect with regards to documentation and whatnot. There is something delightful about the solution to this problem with decorators itself being the further application of decorators!

## Conclusion

In this post, we've taken a look at some of the ways that we can define and use decorators for a variety of uses. Although I found them quite opaque to begin with, I've now fallen slightly in love with the ability to easily and reusably modify the behaviour of functions. In fact, this idea of treating functions like any other piece of data that we can modify and pass around goes far beyond decorators. For those interested, reading through a listing of the functions available in the `functools` library can be an excellent source or further ideas. Good luck!

## Sources and Additional Reading

-   [`functools` Library Documentation](https://docs.python.org/3/library/functools.html)
    -   Documentation for the `functools` library (part of the standard library). An excellent source of ideas!
-   [PEP 318 - Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
    -   The original PEP for decorators. Provides good explanations of the rationale behind decorators, as well as some very interesting examples.
-   [RealPython - Primer on Decorators](https://realpython.com/primer-on-python-decorators/)
    -   Probably the clearest and most readable explanation of Python decorators that I have found
-   [Wikipedia - Closures](<https://en.wikipedia.org/wiki/Closure_(computer_programming)>)
    -   Brief explanation of closures
