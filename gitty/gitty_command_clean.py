from gitty import GittyCommand, CommentStep, GitCommandStep, CommandStep, Color


class GitStatusCheckStep(CommandStep):
    def describe(self, context):
        return ['# make sure the git repo has no outstanding changes']

    def execute(self, context, quiet):
        response = context['git_api'].status_is_clean(context, quiet)
        # response = GittyCommand.execute_command_safe(context, 'git status -s'.split())
        if response:
            # this repo isn't "clean", so don't continue...
            print(Color.red(response))
            print(Color.red_lt('aborting cleanup process - repository has outstanding changes'))
            # set context['continue'] = False if we don't want to continue
            context['continue'] = False


class GitCleanStep(CommandStep):

    def describe(self, context):
        return ['# remove select local branches that have been merged to {}'.format(context['current_branch'])]

    def execute(self, context, quiet):
        # todo: migrate this to use the new git api in the context: get_merged_branch_names()
        command_output = GittyCommand.execute_command_safe(context, 'git branch --no-color --merged'.split())
        output_decoded = command_output.decode('utf-8')
        output_lines = output_decoded.splitlines()
        for line in output_lines:
            branch_name = line.split()[-1]

            retain_reason = ''
            if branch_name.endswith('/master') or branch_name == 'master':
                retain_reason = 'master branches are preserved'
            if branch_name.endswith('/releases'):
                retain_reason = 'release branches are preserved'
            if branch_name == context['current_branch']:
                retain_reason = 'current branch is preserved'

            if not retain_reason:
                # todo: migrate this to use the new git api in the context: remove_branch()
                GittyCommand.execute_command(context, 'git branch -d {}'.format(branch_name).split())
            else:
                print('leaving branch "{}" ({})'.format(branch_name, retain_reason))


class GittyClean(GittyCommand):
    _title = 'cleanup'
    _name = 'freshen up around the place - pull changes (with rebase) and cleanup unused branches'
    _bindings = ['c', 'clean']
    _steps = [
        CommentStep('tidy up the local repository - remove obsolete branches', []),
        GitStatusCheckStep(),
        # todo: migrate this to use the new git api in the context: fetch_and_prune()
        GitCommandStep('git fetch --all --prune', []),
        # todo: migrate this to use the new git api in the context: pull_and_rebase()
        GitCommandStep('git pull --rebase', []),
        GitCleanStep()
    ]

    def is_available(self, context):
        if context['git_api'].status_is_clean(context, quiet=True):
            return False
        else:
            return context['current_branch'] is not None

    def do_it(self, context):
        GittyCommand.execute_steps(self._steps, context)

    def get_description(self, context):
        return GittyCommand.describe_steps(self._steps, context)
