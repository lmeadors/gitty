from gitty import GittyCommand, CommentStep, GitCommandStep, CommandStep, Color, GitCleanStep, GitStatusCheckStep


class GittyClean(GittyCommand):
    _title = 'cleanup'
    _name = 'freshen up around the place - pull changes (with rebase) and cleanup unused branches'
    _bindings = ['clean', 'c']
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
