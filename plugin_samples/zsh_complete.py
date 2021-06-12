from gitty import GittyCommand, Color


def register(context):
    # we're installing a new command here - append it to the commands in the context
    context["commands"].append(GittyZshComplete())


def describe(context):
    return 'zsh - gives commands for zsh completion'


class GittyZshComplete(GittyCommand):
    _title = 'zsh completion'
    _name = 'zsh completion helper'
    _bindings = ['zsh']

    def get_description(self, context):
        return [
            '# list available command for zsh completion'
        ]

    def do_it(self, context):
        available_commands = ""
        for command in context["commands"]:
            if command.is_available(context):
                available_commands += command.bindings_string() + ' '
        print(available_commands)
