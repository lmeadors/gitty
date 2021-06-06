from gitty import GittyCommand, Color, CommentStep, GitCheckoutExistingCommand, GitCommandStep


def register(context):
    # we're installing a new command here - append it to the commands in the context
    context["commands"].append(GittyFinishTask())


def describe(context):
    return 'finish - merge a branch to it''s parent'


class GittyFinishTask(GittyCommand):
    _title = 'finish / merge changes to parent branch'
    _name = 'finish task'
    _bindings = ['finish']
    _steps = [
        CommentStep('go to parent branch (%s)', ['parent_version_branch']),
        GitCheckoutExistingCommand('parent_version_branch'),
        CommentStep('merge branch %s', ['current_branch']),
        GitCommandStep('git merge %s', ['current_branch']),
        CommentStep('delete local branch %s', ['current_branch']),
        GitCommandStep('git branch -d %s', ['current_branch'])
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
