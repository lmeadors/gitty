from gitty.gitty_command import *


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
