import json

from gitty import GittyCommand


class GittyShowContext(GittyCommand):
    _title = 'show'
    _name = 'show current context (useful for debugging)'
    _bindings = ['show']

    def is_available(self, context):
        return True

    def do_it(self, context):
        def without_keys(con):
            return {x: con[x] for x in con if x not in {
                # some context elements can't be represented as json - exclude them here
                'commands',
                'project_type'
            }}

        print('-- current context --')
        print(json.dumps(without_keys(context), indent=2))
        print('---------------------')