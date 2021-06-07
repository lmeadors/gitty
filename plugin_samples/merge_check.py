from gitty import *


def register(context):
    # we're installing a new command here - append it to the commands in the context
    context["commands"].append(GittyMergeCheckTask())


def describe(context):
    return 'merge-check - update a repository and look for unmerged branches'


class HubSyncTask(CommandStep):
    def describe(self, context):
        return [
            '$ hub sync'
        ]

    def execute(self, context, quiet=False):
        if 'git_remote' in context and context['git_remote'] != '':
            print('origin: "{0}"'.format(context['git_remote']))
            GittyCommand.execute_command(context, 'hub sync'.split())


class GittyMergeCheckTask(GittyCommand):
    _title = 'update a repository and look for unmerged branches'
    _name = 'merge check'
    _bindings = ['merge-check']
    _steps = [
        # CommentStep('merge branch %s', ['current_branch']),
        CommentStep('update all local branches (using hub sync)', []),
        # GitCommandStep('hub sync', []),
        HubSyncTask(),
        GitCleanStep(),
        CommentStep('go to master branch', []),
        GitCheckoutMasterCommand(),
        GitCleanStep(),
        GitShowUnmergedBranchesStep(),
    ]

    def get_description(self, context):
        description = []
        for step in self._steps:
            description += step.describe(context)
        return description

    def do_it(self, context):
        for step in self._steps:
            # print(step.__class__)
            step.execute(context, quiet=False)


original = '''
#!/usr/bin/env bash

# is this even a git repo?
# git status -s 2&>1 > /dev/null
git status -s &> /dev/null
IS_GIT_REPO=$?
if [[ ${IS_GIT_REPO} -ne 0 ]];
then
  CWD=`pwd`
  echo "current directory (${CWD}) is not a git repo"
  exit
fi

# it is a git repo! check to see if the repo is dirty - if it is, abort
DIRTY=`git status -s | wc -l`
if [[ ${DIRTY} -gt 0 ]];
then
    echo "***************************************************************************"
    echo "*** this repo has modified files - commit, stash or reset and try again ***"
    echo "***************************************************************************"
    git status
    echo "***************************************************************************"
    exit
fi

echo "### UPDATING ALL BRANCHES ###"
hub sync

echo "### SWITCHING TO MASTER BRANCH ###"
git checkout master

echo "### PULLING MASTER BRANCH AND  ###"
echo "### CLEANING OUT DEAD BRANCHES ###"
gitty c --no_color

echo "### LISTING UNMERGED BRANCHES  ###"
git unmerged
'''
