from gitty import GittyCommand


class GittyVersion(GittyCommand):
    _title = 'version'
    _name = 'show current gitty version'
    _bindings = ['v', 'version']

    def get_description(self, context):
        return ['{} ({})'.format(self._name, context['gitty_version'])]

    def is_available(self, context):
        # is this command available?
        return True

    def do_it(self, context):
        print('current gitty version: {}'.format(context['gitty_version']))