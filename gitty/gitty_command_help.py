from gitty import GittyCommand, Color


class GittyHelp(GittyCommand):
    _title = 'help'
    _name = 'what am i even doing here?'
    _bindings = ['help', 'h']

    def do_it(self, context):
        print('available commands on branch "{}" are:'.format(Color.white_lt(context['current_branch'])))
        commands = context["commands"]
        for command in commands:
            if command.is_available(context):
                command.display_help(context)
        # print a blank line...
        print()
