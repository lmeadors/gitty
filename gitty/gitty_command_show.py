import json

from gitty import GittyCommand, CommandStep


class ShowStep(CommandStep):
    def __init__(self, description):
        self.description = description

    def describe(self, context):
        return [self.description]

    def execute(self, context, **kwargs):
        def without_keys(con):
            return {x: con[x] for x in con if x not in {
                # some context elements can't be represented as json - exclude them here
                'commands',
                'executor',
                'git_api',
                'project_type'
            }}

        print('-- current context --')
        print(json.dumps(without_keys(context), indent=2))
        print('---------------------')


class GittyShowContext(GittyCommand):
    _title = 'show'
    _name = 'show current context (useful for debugging)'
    _bindings = ['show']
    _steps = [
        ShowStep(_name)
    ]

    def is_available(self, context):
        return True

    def do_it(self, context):
        GittyCommand.execute_steps(self._steps, context)

    def get_description(self, context):
        return GittyCommand.describe_steps(self._steps, context)
