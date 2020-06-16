class GittyCommand:
    # the descriptive name of this command
    _name = 'base command'

    # these are the aliases for this command
    _bindings = ['b', 'base']

    def display_help(self, context):
        # show the help for the command
        print(' - {} ({})'.format(self._name, self._bindings))

    def is_available(self, context):
        # is this command available?
        return True

    def do_it(self, context):
        return


class GittyVersion(GittyCommand):
    _name = 'version'
    _bindings = ['v', 'version']

    def display_help(self, context):
        # show the help for the command
        print(' - {} ({})'.format(self._name, self._bindings))

    def is_available(self, context):
        # is this command available?
        return True

    def do_it(self, context):
        print('current gitty version: {}'.format(context['gitty_version']))
