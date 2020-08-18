from gitty import GittyCommand


class GittyParent(GittyCommand):
    _title = 'parent'
    _name = 'go to parent branch'
    _bindings = ['p', 'parent']

    def is_available(self, context):
        if context['current_branch'] is None:
            return False
        return not context['master']

    def do_it(self, context):
        self.execute_command(context, 'git checkout {}'.format(context['parent_version_branch']).split())

    def get_description(self, context):
        return ['{} ({})'.format(self._name, context['parent_version_branch'])]