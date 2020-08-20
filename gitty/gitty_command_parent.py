from gitty import GittyCommand, GitCommandStep, CommentStep


class GittyParent(GittyCommand):
    _title = 'parent'
    _name = 'go to parent branch'
    _bindings = ['p', 'parent']
    _steps = [
        CommentStep('go to parent branch (%s)', ['parent_version_branch']),
        GitCommandStep('git checkout %s', ['parent_version_branch'])
    ]

    def is_available(self, context):
        if context['current_branch'] is None:
            return False
        return not context['master']

    def do_it(self, context):
        for step in self._steps:
            step.execute(context)

    def get_description(self, context):
        description = []
        for step in self._steps:
            description += step.describe(context)

        return description
