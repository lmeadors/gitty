# gitty - a simple alternative to git flow with less rigidity

This project provides an easy way to deal with git branches in an environment with multiple parallel development streams.

![downloads this month] 
(https://img.shields.io/pypi/dm/gitty)

Some assumptions:

- the `master` branch is the cutting edge of new development
- release stabilization branches are created for each major and minor release
- semantic versioning will be used to track where we are
- projects are using either maven or nodejs 

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

To see some useful info about your project, you can just run the gitty script.

> NOTE: I made a symlink to `gitty.py` on my path and called it just `gitty`, so that's what the example will show.

```shell script
% gitty
command: help
available commands on branch "master" are:
  release     - create a new release stabilization branch and release candidate
  task [name] - create a new task branch named "tasks/[name]"
{
    'current_branch': 'master', 'branch_parts': ['master'], 'task_prefix': 'tasks/', 'command': 'help', 
    'project_file': 'package.json', 'current_version': '1.0.0', 'release_version': '1.0.0', 
    'new_stabilization_branch': '1.0/master', 'new_release_branch': '1.0/release',  
    'next_master_version': '1.1.0'
}
```

This is telling you what gitty think the state of your project is.

# new release stabilization branch

Let's say that we're ready to snap a 1.0.0 release of our project. Here's how to do that:

> PROTIP: The "release" and "task" commands can be abbreviated to just "r" and "t", like this...

```shell script
% gitty r
command: r
command: release_from_master
$ git checkout -b 1.0/master
Switched to a new branch '1.0/master'
$ git checkout -b 1.0/release
Switched to a new branch '1.0/release'
bump version to 1.0.0
$ git add package.json
$ git commit -m "bumped version to 1.0.0"
$ git tag 1.0.0
$ git checkout 1.0/master
Switched to branch '1.0/master'
$ git merge --strategy=ours 1.0/release
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

```
% git branch
  1.0/master
  1.0/release
* master
```

Those branches have purpose.

The `1.0/master` branch is used to stabilize the 1.0 release; The `1.0/release` branch is used to give us a stable point of reference in the future for things like hot fixes, etc.

There's also a new tag:

```
% git tag
1.0.0
```

That is on the release branch, and specifically, on the commit where the release candidate should be built from.

# new task for forward development

This is a common thing - so it's pretty simple:

```
% gcm
% gitty t some_new_thing_here
command: t
make a new task branch
command: task_from_master
$ git checkout -b tasks/some_new_thing_here
```

Chuck some code here and commit it and push it - eventually, you'll merge it back to `master` and it'll be real code. Yay.

# new task for release stabilization branch

Yeah, this doesn't sound like a great idea, but sometimes, it's needed.

```
% gco 1.0/master
Switched to branch '1.0/master'
% gitty t some_new_task_for_10
command: t
make a new task branch
command: task_from_point
$ git checkout -b 1.0/tasks/some_new_task_for_10
Switched to a new branch '1.0/tasks/some_new_task_for_10'
```

Now, you've created a branch from the `1.0/master` branch named `1.0/tasks/some_new_task_for_10` - the naming indicates where it will end up (although eventually, you'll most likely want to merge it to `master` too, for now, we'll just work on 1.0).

# new release candidate for 1.0

To make a new RC for the stabilization branch, do this:

```
% gco 1.0/master
Switched to branch '1.0/master'
% gitty r
command: r
command: release_from_point
$ git checkout 1.0/release
Switched to branch '1.0/release'
$ git merge 1.0/master
bump version to 1.0.1
$ git add package.json
$ git commit -m "bumped version to 1.0.1"
b'On branch 1.0/release\nnothing to commit, working tree clean\n'
$ git tag 1.0.1
$ git checkout 1.0/master
Switched to branch '1.0/master'
$ git merge 1.0/release
bump version to 1.0.2
$ git add package.json
$ git commit -m "bumped version to 1.0.2"
```

Again, that's a lot of output...but it's what's happening.

> NOTE: if you want less (or more) output, you have the code. Look in the `def execute_command(command):` function 
> for where most of the above output comes from.

Now, the `1.0/master` branch got merged to `1.0/release`, we have a new tag for the release candidate (`1.0.1`), and the `1.0/master` project file reflects that we're now working toward `1.0.2` for the next release candidate.

> NOTE: Because we merge back to `1.0/master`, we have a single place to look for changes to be merged to version 1.1 (on `master`).

# wrapping up a release to prepare for the next one

Once release 1.0 has been released and we're ready to start on the road to 1.1 (and 1.2), we'll want to get all of the 1.0 changes merged back to `master` (where 1.1 lives). There's not much to do there, so we just use git:

```
% gcm
Switched to branch 'master'
% git merge 1.0/master
Auto-merging package.json
CONFLICT (content): Merge conflict in package.json
Automatic merge failed; fix conflicts and then commit the result.
% (do what you need to do to merge the conflicts here)
% git add package.json
% git commit
```

Creating the next release is exactly the same as before:

```
% gcm
% gitty r
```

You'll see a pile of output again, and at the end, there will be `1.1/master` and `1.1/release` branches and a new `1.1.0` tag for the release candidate.

