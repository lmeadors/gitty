# gitty - a simple alternative to git flow with less rigidity


This project provides an easy way to deal with git branches in an environment with multiple parallel development streams.

View download stats here: https://pypistats.org/packages/gitty

<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/gitty">

### Some assumptions:

- the `master` branch is the cutting edge of new development
- release stabilization branches are created for each major and minor release
- semantic versioning will be used to track where we are
- projects are using either maven, python, or nodejs 

# Some sample work flows...

To get started, we'll make a new empty project using node. 

Next, we'll walk through some common scenarios and see how to use this thing.

```shell script
% mkdir test-project
% cd test-project
% npm init --yes
% git init
% git add package.json
% git commit -m "initial commit"
```

Now, we have a blank project with a package.json file in it and nothing else.

# current state of affairs (and some help)

To see some useful info about your project, you can just run the gitty command.

> I'm assuming that you installed gitty using pip from [https://pypi.org/project/gitty/](https://pypi.org/project/gitty/)

```shell script
-> % gitty
$ git rev-parse --abbrev-ref HEAD
current branch:  master
project type:    node
current version: 1.0.0
command name:    help
available commands on branch "master" are:

cleanup: ['c', 'clean']
  # tidy up the local repository - remove obsolete branches
  # make sure the git repo has no outstanding changes
  $ git fetch --all --prune
  $ git pull --rebase
  # remove select local branches that have been merged to master
...and a LOT more output here...
```

This is telling you what gitty thinks the state of your project is, and what you can do.

# new release stabilization branch

Let's say that we're ready to snap a 1.0.0 release of our project. From the output above, you can see the "release" 
command and it can be run using either `gitty release` or just `gitty r`:

```shell script
-> % gitty r
$ git rev-parse --abbrev-ref HEAD
current branch:  master
project type:    node
current version: 1.0.0
command name:    r
$ git checkout -b 1.0/master
Switched to a new branch '1.0/master'
$ git checkout -b 1.0/releases
Switched to a new branch '1.0/releases'
bump version to 1.0.0
$ git add package.json
$ git commit -m "bumped version to 1.0.0"
b'On branch 1.0/releases\nnothing to commit, working tree clean\n'
$ git tag 1.0.0
$ git checkout 1.0/master
Switched to branch '1.0/master'
$ git merge --strategy=ours 1.0/releases
bump version to 1.0.1
$ git add package.json
$ git commit -m "bumped version to 1.0.1"
$ git checkout master
Switched to branch 'master'
$ git merge --strategy=ours 1.0/master
bump version to 1.1.0
$ git add package.json
$ git commit -m "bumped version to 1.1.0"
```

Wow, that's a lot of crap.

That's showing you what's happening when you create a release - why all that stuff? I'll fill in more details later, but for now: Because.

At the end of that, you'll be back on `master` and there will be 2 new branches:

```shell script
-> % git branch
  1.0/master
  1.0/releases
* master
```

Those branches have purpose.

The `1.0/master` branch is used to stabilize the 1.0 release; The `1.0/releases` branch is used to give us a stable 
point of reference in the future for things like hot fixes, etc.

There's also a new tag:

```shell script
-> % git tag
1.0.0
```

That is on the releases branch, and specifically, on the commit where the release candidate should be built from.

# new task for forward development

This is a common thing - so it's pretty simple:

```shell script
-> % gitty t some_new_thing_here
$ git rev-parse --abbrev-ref HEAD
current branch:  master
project type:    node
current version: 1.1.0
command name:    t
$ git checkout -b tasks/some_new_thing_here
Switched to a new branch 'tasks/some_new_thing_here'
```

Chuck some code here and commit it and push it - eventually, you'll merge it back to `master` and it'll be real code. Yay.

# new task for release stabilization branch

Yeah, this doesn't sound like a great idea, but sometimes, it's needed.

```shell script
-> % gco 1.0/master
Switched to branch '1.0/master'
-> % gitty t some_new_task_for_10
$ git rev-parse --abbrev-ref HEAD
current branch:  1.0/master
project type:    node
current version: 1.0.1
command name:    t
$ git checkout -b 1.0/tasks/some_new_task_for_10
Switched to a new branch '1.0/tasks/some_new_task_for_10'
```

Now, you've created a branch from the `1.0/master` branch named `1.0/tasks/some_new_task_for_10` - the naming indicates 
where it will end up (although eventually, you'll most likely want to merge it to `master` too, for now, we'll just work on 1.0).

# new release candidate for 1.0

To make a new RC for the stabilization branch, do this:

```shell script
% gco 1.0/master
-> % gitty r
$ git rev-parse --abbrev-ref HEAD
current branch:  1.0/master
project type:    node
current version: 1.0.1
command name:    r
$ git checkout 1.0/releases
Switched to branch '1.0/releases'
$ git merge 1.0/master
bump version to 1.0.1
$ git add package.json
$ git commit -m "bumped version to 1.0.1"
b'On branch 1.0/releases\nnothing to commit, working tree clean\n'
$ git tag 1.0.1
$ git checkout 1.0/master
Switched to branch '1.0/master'
$ git merge 1.0/releases
bump version to 1.0.2
$ git add package.json
$ git commit -m "bumped version to 1.0.2"
```

Again, that's a lot of output...but it's what's happening.

Now, the `1.0/master` branch got merged to `1.0/release`, we have a new tag for the release candidate (`1.0.1`), and 
the `1.0/master` project file reflects that we're now working toward `1.0.2` for the next release candidate.

> NOTE: Because we merge back to `1.0/master`, we have a single place to look for changes to be merged to version 1.1 (on `master`).

# wrapping up a release to prepare for the next one

Once release 1.0 has been released and we're ready to start on the road to 1.1 (and 1.2), we'll want to get all of the 1.0 changes merged back to `master` (where 1.1 lives). There's not much to do there, so we just use git:

```shell script
% git merge 1.0/master
Auto-merging package.json
CONFLICT (content): Merge conflict in package.json
Automatic merge failed; fix conflicts and then commit the result.
% (do what you need to do to merge the conflicts here)
% git add package.json
% git commit
```

Creating the next release is exactly the same as before:

```shell script
% gcm
% gitty r
```

You'll see a pile of output again, and at the end, there will be `1.1/master` and `1.1/release` branches and a new `1.1.0` tag for the release candidate.

# Versioning for python projects (i.e., eating my own dog food)

I'm using this tool to manage the git repository for this tool, so its versioning approach is the one that it supports.

The versioning scheme is based on [semver 2.0.0](https://semver.org/spec/v2.0.0.html), and will use a suffix of "dev0" 
to indicate that a version is not a release (and partly because of how setuptools behaves).

For this project, non-release builds will not be deployed to pypi - only actual releases will be deployed.

This versioning will start as of version 1.2.0.dev0 (currently master).
