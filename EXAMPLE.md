# Example use

This is a script that I use to demonstrate how to use this tool. I'm doing it here with maven, but the process is very 
similar with other supported project types.

I'll walk through all of these use cases:

- setting up a new project
- working on task branches
- stabilizing a project
- working on multiple parallel streams
- release candidate creation
- hot fixes


## Some terminology and explanations

First things first: This workflow may not be for you. That's OK, I won't judge you for that. But I will say that it
works really well for me and my team. It's very CI friendly, it helps us to manage multiple parallel development streams 
very easily, and it provides consistent naming and work flows across all of those versions and their releases.

For someone coming from using git-flow, this will seem both similar and different. I was a git-flow user for years, and 
there were some things that I really liked about it and other things that i really did not like about it. I've tried to 
bring the good parts along (consistent naming and work flows), while dropping the things that just didn't work well in 
the shops I have worked in.

With gitty, the leading edge of development is done on the master branch - this is the exact opposite of git-flow, but 
you will see why in a minute (it is easier), and it will make sense. Really. Be aware that the true "master" branch is a 
very fluid place - it is the wild west of your project.

Each version of your project that you work on will have its own ecosystem - which is comprised of a "master" branch and 
a "releases" branch - that seems a bit strange at first, but after a bit of explanation, it too will make sense.

Each release candidate of your project will be tagged in git, and every releases for every version of your project will 
come from one of the "releases" branches - this is to isolate them from ongoing development that may be happening in 
parallel with your release candidates being created. 

In this document, I'll refer to both "version" and "release" - those have different meanings:

- version: this is a stream of development - all 1.0.x work is part of the 1.0 version
- release: this is shorthand for a "release candidate" - a specific 1.0.1 build or commit, for example


## Setting up a new project

OK, this is really tricky. 

Kidding - there is literally no setup - nothing to configure, nothing to initialize except your git repository:

    git init
    
That's it, we've configured our new project to work with gitty. No extra branches, no mucking around.

This is why master is the leading edge of development. It is easier.

For this example, I'm going to use a vastly simplified maven pom:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<groupId>com.elmsoftware</groupId>
	<artifactId>test-project</artifactId>
	<version>1.0.0-SNAPSHOT</version>
	<packaging>jar</packaging>
</project>
```

We'll add that to git and be ready to start work:
```shell script
git add pom.xml
git commit -m "starting point"
```

## Working on tasks

Each unit of work being done is on a task branch - it's created from a master branch for a version.

Since this is a new project, we'll do the work directly from master, like this: 

    gitty task 123234_fix_bug_in_service

This creates a new branch from master with a name based on your provided task name:

```shell script
-> % git branch
  master
* tasks/123234_fix_bug_in_service
```

Let's create some fake work on it and then finish it up:

```shell script
touch ex_fix_for_1.0_service.txt
git add ex_fix_for_1.0_service.txt
git commit -m "fixing a bug on 1.0"
```

Now, we're ready to merge our sophisticated change back to our master branch:

```shell script
git checkout master
git merge tasks/123234_fix_bug_in_service
git branch -d tasks/123234_fix_bug_in_service
```

## Making a stabilization “ecosystem”

When you’re ready to stabilize for a release, you create a new "ecosystem" for that process - that consists of two new 
branches - one for releases and one for ongoing work. There may be tasks associated with this as well, but we will get 
to those in a bit. To make our stabilization ecosystem, we want to go to master then do this:

```shell script
gitty stabilize
```

This will do 3 things:

- create a new stabilization branch named "1.0/master"
- create a new release branch named "1.0/releases"
- set version to "1.1.0-SNAPSHOT" on branch "master"

The last step will vary slightly based on your project type - because mine is java+maven, it updates my pom.xml file.

At this point, the 1.1 version of my project will live on master, and the 1.0 version of my project (ongoing development 
and releases) will come from the 1.0 ecosystem. If we look at the branches now, they will look like this:

```shell script
-> % git branch
  1.0/master
  1.0/releases
* master
```

## Working on 1.0 tasks

Working on 1.1 tasks will be exactly like we saw above (since master is now 1.1), but what about 1.0 tasks?

It turns out they are the same, too - the only difference is where you do them from - the 1.0/master instead of master.

```shell script
git checkout 1.0/master
gitty task 234345_fix_a_bug
```

As before, this creates a task branch for us and leaves it checked out:

```shell script
-> % git branch
  1.0/master
  1.0/releases
* 1.0/tasks/234345_fix_a_bug
  master
```

You'll notice though that it is not exactly the same - now the task is created as a part of the 1.0 ecosystem. This 
makes it clear where the task is intended to be merged back to.

We'll leave that branch as it is for now, and do some other things, so we can see what the repository starts to look 
like as work continues.

## More ongoing work...

For illustration, we can make another 1.1 task, and move some of the branches ahead so we can see what is happening.
 
We will add a file to each of the branches then commit them and look at how we would merge those forward to get them in 
the correct 1.0 and 1.1 master branches. 

I am still on the 1.0/tasks/234345_fix_a_bug branch, so I will start there and make some messes that we will clean up 
later.

```shell script
touch ex_some_file_for_1.0_release.txt
git add ex_some_file_for_1.0_release.txt
git commit -m "fixing a 1.0 bug"
git checkout master
gitty t 345456_fix_another_bug
touch ex_another_fix_for_1.1_release.txt
git add ex_another_fix_for_1.1_release.txt
git commit -m "fixing a new bug on 1.1"
git checkout master
touch ex_some_cowboy_1.1_change.txt
git add ex_some_cowboy_1.1_change.txt
git commit -m "fixing something minor on 1.1"
```

> NOTE: Did you see that `gitty t` in there? nobody likes lots of typing, so t=task, r=release, and s=stabilize - easy.

OK, now we have added several new files on different branches for 2 different releases. What fun!

We will start on the most important stuff - the stabilization branch needs to get cleaned up so we can make a release. 
Here is what it looks like now:

```shell script
-> % gco 1.0/master
Switched to branch '1.0/master'
-> % git unmerged
  1.0/tasks/234345_fix_a_bug
  master
  tasks/345456_fix_another_bug
```

There are 3 branches that haven't been merged to our 1.0/master, but we only care about the 1.0 branches...so only the
1.0/tasks/234345_fix_a_bug branch matters to us - so we can get that merged and ready to go:

```shell script
git merge 1.0/tasks/234345_fix_a_bug
git branch -d 1.0/tasks/234345_fix_a_bug
```

OK, now our 1.0 branch has the fix, but 1.1 does not - we need to get that resolved:

```shell script
gcm
git merge 1.0/master
```

Now, from master, things look like this:

```shell script
-> % git branch
  1.0/master
  1.0/releases
* master
  tasks/345456_fix_another_bug
-> % git unmerged
  tasks/345456_fix_another_bug
```

Our master branch has moved ahead, and our tasks/345456_fix_another_bug branch also needs that change (and the cowboy 
change, too!) - so we'll go over there and update it, too:

```shell script
gco tasks/345456_fix_another_bug
git merge master
```

Now, everything is in a pretty happy place - master has everything from 1.0, so we shouldn't have regression bugs; 
the 1.1 task branch also has all of the changes to 1.1 - generally speaking, things are pretty tidy.

Now we need a 1.0 release candidate!

## Making a release candidate for 1.0

Making a release from a stabilization branch is pretty simple:
```shell script
$ gco 1.0/master
$ gitty release
```

This will do a few things for you:

- merge "1.0/master" to "1.0/releases"
- set version to "1.0.0" on branch "1.0/releases"
- create a new tagged release named "1.0.0" on branch "1.0/releases"
- merge branch "1.0/releases" to "1.0/master"
- set version to "1.0.1-SNAPSHOT" on branch "1.0/master"

Just to tidy things up here, we'll want to merge that to our 1.1 ecosystem:

- merge 1.0/master to master
- merge master to any /tasks/* branches

## Making a release candidate from master for 1.1

OK, we can pretend now that 1.0 has been blessed and released to production - we have one task left for 1.1, then we 
think it will ber feature complete...so we can get that ready to go like this:

```shell script
gcm
git merge tasks/345456_fix_another_bug
git branch -d tasks/345456_fix_another_bug
```

Now we are ready for a release candidate:

```shell script
gitty r
```

This will do several things for us:

- create a new stabilization branch named "1.1/master"
- create a new release branch named "1.1/releases"
- set version to "1.1.0" on branch "1.1/releases"
- create a new tagged release named "1.1.0" on branch "1.1/releases"
- merge branch "1.1/releases" to "1.1/master"
- set version to "1.1.1-SNAPSHOT" on branch "1.1/master"
- merge branch "1.1/master" to "master"
- set version to "1.2.0-SNAPSHOT" on branch "master"

At this point, master now represents our 1.2 version, 1.1/master is our 1.1 version, and 1.0/master is our 1.0 version.

Unfortunately, there is a bug in production. We need a hot fix for our 1.0 version. Bummer.

## Making a hot fix

We want to get the latest 1.0 release candidate - so we do this:

```shell script
gco 1.0/releases
gitty s
```

This will do a few things for us:

- create a new release branch named "1.0.0/releases"
- create a new stabilization branch named "1.0.0/master"
- set version to "1.0.0.0-SNAPSHOT" on branch "1.0.0/master"

> NOTE: We could have just created a new 1.0.x release here, but since i wanted to show how to make a sub-release, I 
> didn't.

Now, we make changes either on the new 1.0.0/master branch or using task branches created from it - once we're happy 
with the state of the 1.0.0/master branch, we can create a release based on it using the exact same work flow used to 
create releases anywhere else. Consistency is nice.

Once that release is created, the merge mania is the same - 1.0.0 to 1.0, then 1.0 to 1.1, then 1.1 to master (1.2).

Hot fixes are always somewhat messy, but hopefully the consistency here makes them a bit less painful.
