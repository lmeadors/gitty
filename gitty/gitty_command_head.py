from gitty import GittyCommand, Color


class GittyHead(GittyCommand):
    _title = 'head'
    _name = 'basic project info'
    _bindings = ['head']

    def do_it(self, context):
        # print('available commands on branch "{}" are:'.format(Color.white_lt(context['current_branch'])))
        # commands = context["commands"]
        # for command in commands:
        #     if command.is_available(context):
        #         command.display_head(context)
        # print a blank line...
        print('for help, try "gitty help"')
