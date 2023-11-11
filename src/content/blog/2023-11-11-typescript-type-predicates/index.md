---
title: Type Predicates in TypeScript
description: Using type predicates in TypeScript with type guards
pubDate: 2023-11-11
---

I use TypeScript in my day-today coding, and generally, I love it. It lets me be more explicit about exactly what I want a function / variable to do and helps me to avoid bugs by warning me when variable, functions, &c. might have the wrong type. In general, it has made my programming faster and more efficient.

However.

There are definitely some time when I curse TypeScript for its behaviour. Some of the behaviours it has frustrate me to no end. I'd like to share one of those, along with the solution.

## The Backstory - `.filter`

I had a function which got a list of users by id. However, sometimes the data was stale (perhaps the user was removed by a different user in the system between when the page loaded and when the user asked for the list), and so the function would get _either_ a valid user or undefined if it didn't exist. Obviously I wanted a list only a list of the valid users, so I filtered the returned list to get rid of the `undefined` elements.

```typescript
const getUsers = (ids: Array<string>): Array<User | undefined> => {
    // code here to get the users from the backend
};

// get the users and filter out the undefined ones
const relevantUsers = getUsers(relevantIds).filter(
    potentialUser => !!potentialUser
);

const names = relevantUsers.map(user => user.name);
```

Much to my surprise, that didn't work! Despite my filtering out the `undefined` elements in the array, TypeScript continued to complain that the elements of `relevantUsers` could be `undefined`!

![The code above, showing an error 'user could be undefined'](/2023-11-11/typescript1.png)

## The Solution - Type Predicates

There are definitely a few quick and dirty solutions that I would like to avoid (but, in all honesty, have used when under pressure to meet deadlines). The first is to just ignore it. I know that the array is made up of only `Users`, so I just throw a quick `@ts-expect-error` above the line. Another option is to use the `as` operator to assert that the returned array is of type `Array<User>`. However, both of these options are dangerous; they could very well lead to further errors downstream. I really would like a better solution.

After some research, it turns out that I needed to provide a custom function to narrow the type, and the custom function needed to use a [type predicate](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates) to essentially tell the TypeScript compiler what the type if the input value is. A type guard using a predicate has the following form:

```typescript
function guard(value): value is Type {
    // code to test the type
}
```

For the situation above, we don't want to assert that the potential user _is_ a type, we want to assert that it _isn't_. Thus, we can use the following function:

```typescript
const isNotUndefined = <T>(input: T | undefined): input is T => {
    return input !== undefined;
};
```

And so our code would look as follows:

```typescript
const isNotUndefined = <T>(value: T | undefined): value is T => {
    return value !== undefined;
};

const relevantUsers = getUsers(relevantIds).filter(isNotUndefined);

const names = relevantUsers.map(user => user.name);
```

And now the compiler is happy with `relevantUsers` correctly being an array of `Users` with no `undefined` elements. This solution is better in a variety of ways. It plays nicely with TypeScript; I'm no longer forcing a type on a variable or ignoring errors, so if I later make changes (maybe `getUsers` is changed later to reurn a list of `User`, `undefined`, or `UserError`) these will be reflected in the type of the `relevantUser` variables. Also, the function is testable. I often include an `isWhatever` function on custom classes that I write, and add tests for the type guards into the test suite.

Hopefully this saves you some headaches in the future! I would recommend reading the [TypeScript docs](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates) on type predicates as they are explained very clearly.
