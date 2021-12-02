---
title: Automatic Versioning of JavaScript Projects
date: 2021-12-05
description: How to create an automatic versioning system for JavaScript projects using Github Actions
---

## Introduction

As software projects become more complex, it becomes more and more useful to have a consistent way to version them. Of course, if you are creating a library or some other piece of software that other developers use, then it becomes indispensable! In this post, I will go through a way of:

-   Ensuring useful and consistent commit messages using commitlint and husky
-   Creating local versions using standard-version
-   Setting up an automatic, language agnositc versioning solution using Github Actions
-   Extending that solution to the case where you have a protected branch

## Setting up commitlint and husky

The first thing that we want to do when setting up our project to use a consistent versioning system is to ensure that our commits follow the [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) standard. This is a way of formatting our commit messages so that the purpose and what they accomplish is both immediately evident to any reader and, perhaps even more importantly for our goal of automatic versioning, easily parsed. The basic format is:

```
type(optional scope): short description

Extended body (optional)

Footer (optional)
```

The type can be one of about a dozen different keywords, and represent what sort of commit it is. For instance, you might use `fix` to denote that the commit is a bugfix or `feat` to denote that it is a feature. I would recommend taking a look at the above conventional commits website - they do an excellent job explaining the format quickly and concisely.

We could rely on ourselves (or the other developers that we are working with) to alwaysuse this type of commit, but even when working by myself I know that I can't always be trusted. Thus, we will set up some tools to make this process automatic!

The first thing that we will do is to create a small sample project.

```bash
mkdir versioning-sample-project
cd versioning-sample-project
npm init
```

At that point `npm` will ask a series of questions; for our purposes the defaults are just fine. At this point you should have a small project with a simple `package.json` file and nothing else.

While we're at it we might as well set this up as a `git` repository and commit our `package.json`:

```bash
git init
git commit -am 'Initial commit'
```

Great! Now we are all set up to install [husky](https://github.com/typicode/husky) and [commitlint](https://github.com/conventional-changelog/commitlint). Husky is a package to make the use of pre-commit hooks easier, and commitlint is a linter for commit messages. We will use them together to ensure that our commits match the conventional commit format.

## Setting up a versioning system on github actions

## dealing with protected branches

## Resources and Further Reading
