import sys

from gitty import GittyCommand


class GittyTask(GittyCommand):
    _title = 'task'
    _name = 'start a new task branch (name is required)'
    _bindings = ['t', 'task']

    def is_available(self, context):
        if context['current_branch'] is None:
            return False
        return not context['on_a_task']

    def do_it(self, context):
        # we need a task name - like 123234_some_task_name
        if len(sys.argv) > 2:
            context['task_name'] = sys.argv[2]
            git_command = 'git checkout -b {}{}'.format(context['task_prefix'], context['task_name'])
            if len(context['branch_parts']) > 1:
                self.execute_command(context, git_command.split())
            else:
                self.execute_command(context, git_command.split())

    def get_description(self, context):
        sample_task_name = '123234_your_task_here'
        return [
            "{}, so if you said 'gitty {} {}', then you'd get this:".format(
                self._name, self._bindings[0], sample_task_name
            ),
            '$ git checkout -b {}{}'.format(context['task_prefix'], sample_task_name)
        ]