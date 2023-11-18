---
title: Introduction to Sorting in Python
description: Quick introduction to sorting, along with how to sort by multiple criteria
pubDate: 2023-11-18
---

This last week, I came across an interesting problem which proved more difficult to solve with Python than I had initially thought, so this post will outline the steps that I took for posterity. Essentially, the problem boiled down to sorting a list by multiple criteria in Python.

For my work, we use a Python-based ORM for the backend and a React frontend. This setup means that I have not so far had to actually sort anything in Python; if something needed to be sorted we generally did it either at the database layer (if the ordering was inherent to the subject) or at the frontend level (if the ordering depended on some choice of the user's). However, I came across an issue where the ordering done needed to be at the backend level but was too complex for the database to handle. Hence, this post!

My problem was analogous to the following. Imagine that you want users to select a country. You know that 90% of your users will be from Canada, the US, and Great Britain. Hence, you want those countries at the top. Thereafter, you want the rest of the countries listed alphabetically. How can you achieve this? I'm going to go through a quick introduction to sorting in Python and then give the solution I came up with.

## Basics of Sorting

When sorting in Python, there are two main functions that you can use. There is the list method `.sort`, which sorts the list in place, and the built-in `sorted` function which returns a copy of the sorted iterable. Note that the `sorted` function is more general, since it can operate on any iterable, not just a list.

By default, both of these sort in ascending order (smallest first).

```python
to_sort = [1, 5, 7, 2, 3]
to_sort.sort()
to_sort
```

    [1, 2, 3, 5, 7]

```python
to_sort = [1, 5, 7, 2, 3]
sorted(to_sort)
```

    [1, 2, 3, 5, 7]

Both of these functions also take a `reverse` key to sort in _descending_ order instead.

```python
to_sort = [1, 5, 7, 2, 3]
sorted(to_sort, reverse=True)
```

    [7, 5, 3, 2, 1]

(From now on I'll be sticking to just using the `sorted` function, since almost always I want a copy of the list rather than the original one, but sorted).

While this is great, it quickly becomes apparent that when doing anything more complicated than just putting basic data types into their natural order, you need a way to specify that way that the different elements are compared. Luckily, there is the `key` attribute! You provide this attribute with a function, and when sorting that function will be run on each of the elements and the results will be compared. For example, if we had a class of students we might want to sort by their name, their age, or their average grade.

```python
from collections import namedtuple

Student = namedtuple("Student", ['name', 'average', 'age'])

class_list = [
    Student("Bob", 83, 37),
    Student("Clara", 98, 32),
    Student("Alice", 94, 35),
]

# sorting by name
print(sorted(class_list, key=lambda student: student.name))
# sorting by age
print(sorted(class_list, key=lambda student: student.age))
# sorting by average grade
print(sorted(class_list, key=lambda student: student.average))
```

    [Student(name='Alice', average=94, age=35), Student(name='Bob', average=83, age=37), Student(name='Clara', average=98, age=32)]
    [Student(name='Clara', average=98, age=32), Student(name='Alice', average=94, age=35), Student(name='Bob', average=83, age=37)]
    [Student(name='Bob', average=83, age=37), Student(name='Alice', average=94, age=35), Student(name='Clara', average=98, age=32)]

In fact, this pattern is so common that there is a special helper function to get attributes of an object: `attrgetter` from the `operator` module. For instance, we could re-write sorting by name as follows:

```python
from operator import attrgetter

sorted(class_list, key=attrgetter('name'))
```

    [Student(name='Alice', average=94, age=35),
     Student(name='Bob', average=83, age=37),
     Student(name='Clara', average=98, age=32)]

Of course, the `reverse` key is still respected with a custom `key`.

```python
sorted(class_list, key=attrgetter('name'), reverse=True)
```

    [Student(name='Clara', average=98, age=32),
     Student(name='Bob', average=83, age=37),
     Student(name='Alice', average=94, age=35)]

## Sorting by Multiple Criteria

If you read the (clearly explained and excellent) [Python sorting documentation](https://docs.python.org/3/howto/sorting.html), you will see that for sorting on multiple criteria, they advocate taking advantage of the fact that the sorting function used is _stable_: that is, when two elements have the same 'score', their original order will be preserved. This means that if you want to sort based on e.g. first the grade and then the name, you can first sort by the name and then the grade, preserving the order.

However, in my example above this wouldn't work, since in essence we are sorting the same property (country name) twice, by two slightly overlapping criteria. I had to find another way.

The solution I found was quite simple: have the `key` attribute return a tuple representing each of the criteria! In Python, tuples are compared elementwise, so this allows us to compare the elements of the original list by multiple criteria at once.

```python
# a list of all countries in some random order
countries = [
    "Canada",
    "United States of America",
    "Great Britain",
    "Mexico",
    "Uruguay",
    "Bolivia",
]

# what we want the first elements of the final list to look like
desired_top_country_order = [
    "Canada",
    "Great Britain",
    "United States of America",
]

def sort_by_position_then_name(country):
    return (
        desired_top_country_order.index(country) if country in desired_top_country_order else len(desired_top_country_order),
        country,
    )

sorted(countries, key=sort_by_position_then_name)
```

    ['Canada',
     'Great Britain',
     'United States of America',
     'Bolivia',
     'Mexico',
     'Uruguay']

To see why this happens, let's see what the function returns for some countries.

```python
print(sort_by_position_then_name("Canada"))
print(sort_by_position_then_name("Great Britain"))
```

    (0, 'Canada')
    (1, 'Great Britain')

Here, since both countries are in the list of desired top countries, their index in that list is used as the first element of the sorting tuple, meaning they are compared by that.

```python
print(sort_by_position_then_name("Canada"))
print(sort_by_position_then_name("Mexico"))
```

    (0, 'Canada')
    (3, 'Mexico')

Since Canada is in the list of countries we want at the top of the list, the first element in its tuple is 0. Since Mexico isn't we set that value to the length of the desired order, automatically placing it _behind_ all of the countries in the desired order list. When comparing the tuples, since $0 < 3$ (traditionally), Canada will come before Mexico.

```python
print(sort_by_position_then_name("Uruguay"))
print(sort_by_position_then_name("Mexico"))
```

    (3, 'Uruguay')
    (3, 'Mexico')

Here, neither of the countries is in the list of desired top countries; hence, both of their first elements is 3. Since that comparison doesn't yield a clear answer, the next element of the tuple is compared: their names. This yields the alphabetical order.

## Conclusion

And there you have it: a way of sorting a Python iterable by several criteria at once.

I will be the first to admit: while this solution did solve my problem, it does lack generality. You have to be very careful crafting the key comparison function to ensure that you're getting the right order. An ideal solution would be something like [what I did with JavaScript sorting](/blog/2021-09-05-sorting/), where you just provide a list of sorting functions and the final sorter is generated automatically. However, that sounds like a project for a different time!
