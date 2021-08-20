---
title: Sorting By Multiple Criteria in JavaScript
date:
description: A function to sort by multiple simultaneous criteria in JavaScript
---

Sorting a collection of data, whether they be primitives like a list of string or more complex ones like a list of objects, is a very common task. I present here a solution to a problem which I had which involved quickly and easily generating a sorting function to sort a list of objects based on multiple different attributes.

## TL;DR

`embed:resources/final.js`

## Basic Sorting

To sort an array in JavaScript, you usually use the `.sort` method of the array itself. This function sorts the elements of the array into ascending order ('smallest' items first). It also sorts them in place; that is, it modifies the array itself. By default, it will compare each of the elements (as a string), which can lead to some counterintuitive results:

`embed:resources/functionlessSort.js`

However, it is much more useful to provide a sorting function as the argument to `.sort()`. This function has the signature `(a, b) => Number`. This provides a way of comparing any two elements, and then sorting them based on the returned value as follows:

1. `a` before `b`: returned value is negative (_less_ than zero)
2. `a` after `b`: returned value is positive (_greater_ than zero)
3. `a` == `b`: returned value is 0

This allows us to sort in a more general fashion. For instance, imagine that we have a data structure representing a student. The student might have many different fields which describe them, as follows:

`embed:resources/student.js`

Then if we have a whole class full of students, we can sort them in various ways, just by providing a different function to the `.sort()` function:

`embed:resources/differentSorts.js`

The last one probably deserves a bit more of an explanation. There are a few things going on here. First of all, we actually want to sort this in a _descending_ order - we want the person with the higher average at the front. So what happens if we have two students and compare their averages using this function? Let's say that Alice and Bob are `a` and `b` respectively. Then Alice.average = 88.5 and Bob.average = 97.6. Bob should be in front of Alice, and the result of the function is 97.6 - 88.5 > 0, which does put Bob in front, as he should be.

## Sorting Based on Multiple Criteria

Now let's look at a slightly more complex case: when we can to sort by several different criteria. For instance, imagine that we wanted to generate a class list. In that case, we want to sort first by their last name, and then, if those are identical, sort by the first name, and if those are the same throw our hands up in the air and decide that those students are functionally identical (at least as far as class list generation goes). To make this more concrete, let's write out our functions for the first and last name.

`embed:resources/firstLastName.js`

Let's think carefully about our combined sorting function. For our two students `a` and `b`, we want to first check their last names. If that gives us a definite answer as to their relative position (returns a negative or a positive number), then great! We'll use that. However, if that returns 0 (indicating that as far as last names go, they are the same), then we want to sort them based on first name. As a sorting function, here's what that looks like.

`embed:resources/multipleCriteria.js`

## Tying It All Up: The Function

This is all fine and good if we have only two functions, but imagine the case where we had many different criteria - maybe we wanted to sort on date of brith, then first and last name, then average (ascending), then mother's maiden name. And further, imagine that at some later date, we wanted to sort these same students using the same criteria, but in a different order: now we want to start with mother's maiden name, then date of birth, then average, then first and last name! Clearly, writing out each of these would be tedious in the extreme. What we'd like is a function which, when passed in a list of sorting functions, returns a combined sorting function which evaluates each of the individual functions in order of precedence, returning the first non-zero result (or zero if they all return 0). Here is that function!

`embed:resources/final.js`

Again, let's explain this in some more detail. The `generateSorter` function is a higher-order function (a function which returns a function). In this case, its only argument is `listOfSorters`, which is an array of sorting functions in order of precedence. The function which is returned has the same signature as any of the other sorting functions: it takes in two elements (`a` and `b`) and returns a number indicating their relative position. 

We then have a `for` loop which goes through each of the individual sorting functions and sees what it returns for that particular `a` and `b`. If it gives a definite result, then that result is returned. If not, then it continues to the next function (iterates through the loop). If it reaches the end of the loop without finding a definite answer, then as far as we care the two elements are the same, and so we return 0.

This function allows us to re-write our earlier compound sorter (based on first and last name). Here is what that looks like.

`embed:resources/re-written.js`

This function allows us to quickly and easily combine different sorting functions and sort on multiple different criteria.
