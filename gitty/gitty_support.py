from gitty.gitty_command import *


def setup(context):
    command_setup(context)
    return context


def command_handler(context):
    # show some minimal context info
    print('current branch:  {}'.format(Color.green(context['current_branch'])))
    print('project type:    {}'.format(Color.green(context['project_type'].get_name())))
    print('current version: {}'.format(Color.green(context.get('current_version', 'unknown'))))
    print('command name:    {}'.format(Color.green(context['command'])))

    # look for a command object for this command...
    for value in context["commands"]:
        if value.is_called(context):
            if value.is_available(context):
                # we found one that is available for this context - do it then return what it returns
                return value.do_it(context)
            else:
                print('command "{}" is not available in this context.'.format(Color.red_lt(value._title)))
