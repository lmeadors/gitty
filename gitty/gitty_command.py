import json


def command_setup(context):
    context["commands"] = [
        GittyVersion(),
        GittyShowContext()
    ]
    return


class GittyCommand:
    # the descriptive name of this command
    _name = 'base command'

    # these are the aliases for this command
    _bindings = ['b', 'base']

    def display_help(self, context):
        # show the help for the command
        print(' - {} \n   - {}'.format(self._bindings, self._name))

    def is_available(self, context):
        # is this command available?
        return True

    def is_called(self, context):
        command_name = context['command']
        return command_name in self._bindings

    def do_it(self, context):
        return


class GittyVersion(GittyCommand):
    _name = 'show current gitty version'
    _bindings = ['v', 'version']

    def display_help(self, context):
        # show the help for the command
        print(' - {} \n   - {} ({})'.format(self._bindings, self._name, context['gitty_version']))

    def is_available(self, context):
        # is this command available?
        return True

    def do_it(self, context):
        print('current gitty version: {}'.format(context['gitty_version']))


class GittyShowContext(GittyCommand):
    _name = "show current context"
    _bindings = ['show']

    def is_available(self, context):
        return True

    def do_it(self, context):
        def without_keys(con):
            return {x: con[x] for x in con if x not in {'commands'}}
        print('-- current context --')
        print(json.dumps(without_keys(context), indent=2))
        print('---------------------')
