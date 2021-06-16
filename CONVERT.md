# Converting from git flow

This is pretty easy - it's easier if you have a repository with no feature branches.

I'll walk through my current example (a real project I'm working on) and show the steps.

```shell
-> % git branch -a
* develop
  master
  remotes/origin/HEAD -> origin/master
  remotes/origin/develop
  remotes/origin/master
```

You need to know your current release version - in my case, I'm working a maven project, so I can ask gitty the 
current version:

```shell
-> % gitty
$ git rev-parse --abbrev-ref HEAD
current branch:            develop
project type / version:    maven / 1.0.5-SNAPSHOT
command name:              head
for help, try "gitty help"
```

I also need to know the current release version - with gitflow that's on master:

```shell
-> % gcm && gitty
Switched to branch 'master'
Your branch is up to date with 'origin/master'.
$ git rev-parse --abbrev-ref HEAD
current branch:            master (tags: ['1.0.4'])
project type / version:    maven / 1.0.4
command name:              head
for help, try "gitty help"
```

This is one of those weird situations in git-flow - how are version numbers to be handled? With gitty, both of these 
branches would exist under the 1.0 "ecosystem" and 1.1 would be master - so what we'll do is create the 1.0 ecosystem 
and put things where they belong, then create a new 1.1 ecosystem (as master).

| current branch    | version           | new branch 
|-------------------|-------------------|-------
| develop           | 1.0.5-SNAPSHOT    | 1.0/master
| master            | 1.0.4             | 1.0/releases
| [new branch]      | 1.1.0-SNAPSHOT    | master

This always seems scary, but it's not really - remember that a branch in git is really just a commit. 

We'll start by renaming the existing branches to match our goal. I'm on `master` which will become `1.0/releases`, so 
that's easy:

```shell
-> % git branch -m 1.0/releases
```

Next, the `develop` branch becomes `1.6/master`:
```shell
-> % git checkout develop
-> % git branch -m 1.0/master
```

Now, we need a new master branch (for 1.1) - this is where things get scary, but not...really. We'll start from the 
`1.0/master` branch, make a new master, then bump the `pom.xml` file there to reflect the new version. 

```shell
# we should still be on 1.0/master - we'll use that to create the new master...
git branch master
# now we'll check that out and update the pom
git checkout master
# ... edit the pom - set the version
git add pom.xml
git commit -m "bumped pom to 1.1"
```

Once that's done, it's time to start removing obsolete branches, pushing the changes, and updating the origin settings.

Start by deleting the `master` branch on origin - you have that locally now as the tip of the `1.0/releases` branch which 
we'll push up next with `git push --all`.

Odds are good that your default branch is `develop`, since we're deleting that branch, that setting is wrong - it'll 
be `master` when you're done. How you make that change varies by git provider.

Once all the branches are pushed, you'll also need to make that change locally:

```shell
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
```

At the end of it all, I ended up with this setup:

```shell
-> % git branch --all
  1.0/master
  1.0/releases
* master
  remotes/origin/1.0/master
  remotes/origin/1.0/releases
  remotes/origin/HEAD -> origin/master
  remotes/origin/master
```

Also, don't forget to update your CI/CD services to match the new branch names...
