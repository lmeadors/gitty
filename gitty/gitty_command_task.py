import sys

from gitty import GittyCommand, CommentStep, GitCheckoutNewCommand


class GittyTask(GittyCommand):
    _title = 'task'
    _name = 'start a new task branch (name is required)'
    _bindings = ['task', 't']
    _steps = [
        CommentStep(_name, []),
        CommentStep(
            'for example: if you said "gitty {} %s", then you would get this:'.format(_bindings[0]),
            ['task_name']
        ),
        GitCheckoutNewCommand('task_branch_name'),
    ]

    def is_available(self, context):

        # can't make a task unless you're in a git repo...
        if context['current_branch'] is None:
            return False

        # don't make a task from a task.
        return not context['a_task']

    def do_it(self, context):
        # we need a task name - like 123234_some_task_name
        # argv = [script name, command name, task name, other parameters...]
        if len(sys.argv) > 2:
            context['task_name'] = sys.argv[2]
            context['task_branch_name'] = '{}{}'.format(context['task_prefix'], context['task_name'])
            GittyCommand.execute_steps(self._steps, context)

    def get_description(self, context):
        # set a sample task name here so we can demonstrate the behavior
        context['task_name'] = '123234_sample_task_here'
        context['task_branch_name'] = '{}{}'.format(context['task_prefix'], context['task_name'])
        return GittyCommand.describe_steps(self._steps, context)
