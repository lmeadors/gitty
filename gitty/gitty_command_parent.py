from gitty import GittyCommand, GitCommandStep


class GittyParent(GittyCommand):
    _title = 'parent'
    _name = 'go to parent branch'
    _bindings = ['p', 'parent']
    _steps = [
        GitCommandStep('git checkout %s', ['parent_version_branch'])
    ]

    def is_available(self, context):
        if context['current_branch'] is None:
            return False
        return not context['master']

    def do_it(self, context):
        for step in self._steps:
            step.execute(context)
            # self.execute_command(context, 'git checkout {}'.format(context['parent_version_branch']).split())

    def get_description(self, context):
        description = [
            '# {} ({})'.format(self._name, context['parent_version_branch'])
        ]
        for step in self._steps:
            description += step.describe(context)

        return description
