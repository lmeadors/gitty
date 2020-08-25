from gitty.gitty_command import *
import sys


def setup(context):

    # get any CLI switches in the context - experimental...
    argc = len(sys.argv)
    for i in range(argc):
        param = sys.argv[i]
        if param.startswith('--'):
            param = param[2:]
            if i + 1 < argc:
                next_value = sys.argv[i + 1]
                if next_value.startswith('--'):
                    value = True
                else:
                    value = next_value
            else:
                value = True
            # print('{} = {}'.format(param, value))
            context[param] = value

    if len(sys.argv) > 1:
        # figure out the command - find the first value that does not start with '--' and isn't after one that does...
        i = 1
        while i < len(sys.argv) and 'command' not in context:
            if not sys.argv[i].startswith('--'):
                context['command'] = sys.argv[i]
                i += 1
            else:
                # this one started with '--', so skip it AND the following value
                i += 2

    # if there's no command set now, default it to 'help'
    context['command'] = context.get('command', 'help')

    if context.get('no_color', False):
        Color.disable_color()

    command_setup(context)

    return context


def command_handler(context):

    # if we get here and this isn't set yet, default it to False
    context['dry_run'] = context.get('dry_run', False)

    # show some minimal context info
    print('current branch:  {}'.format(Color.green(context['current_branch'])))
    print('project type:    {}'.format(Color.green(context['project_type'].get_name())))
    print('current version: {}'.format(Color.green(context.get('current_version', 'unknown'))))
    print('command name:    {}'.format(Color.green(context['command'])))
    if context['dry_run']:
        print('dry run:         {}'.format(Color.red_lt(context['dry_run'])))

    # look for a command object for this command...
    for value in context["commands"]:
        if value.is_called(context):
            if value.is_available(context):
                # we found one that is available for this context - do it then return what it returns
                return value.do_it(context)
            else:
                print('command "{}" is not available in this context.'.format(Color.red_lt(value._title)))
