import os
import pkg_resources  # part of setuptools

from gitty.gitty_command import *


def setup(context):

    # we'll actually do stuff, unless this is over-written
    if os.getenv('GITTY_DRY_RUN', False):
        context['dry_run'] = True
        print('*** DRY RUN - NOT ACTUALLY MAKING ANY CHANGES ***')
    else:
        context['dry_run'] = False

    context["handled"] = False

    command_setup(context)

    # add the current gitty version to the context
    context['gitty_version'] = pkg_resources.require("gitty")[0].version

    try:
        current_branch_output = subprocess.check_output('git rev-parse --abbrev-ref HEAD'.split())
        context['current_branch'] = current_branch_output.decode().strip()
        context['branch_parts'] = context['current_branch'].split("/")
        if len(context['branch_parts']) > 1 and context['branch_parts'][0] != 'tasks':
            context['task_prefix'] = context['branch_parts'][0] + '/tasks/'
        else:
            context['task_prefix'] = 'tasks/'

    except subprocess.CalledProcessError:
        print(Color.red_lt('current directory is not a git repository'))
        context['current_branch'] = None
        context['branch_parts'] = None
        context['task_prefix'] = None
        # be extra sure we don't change anything here...
        context['dry_run'] = True

    return context


def command_handler(context):

    # now that we know what kind of project we have, get the version info from it
    GittyCommand.get_version_info(context)

    print('command name:    {}'.format(Color.green(context['command'])))
    print('current version: {}'.format(Color.green(context.get('current_version', 'unknown'))))
    print('current branch:  {}'.format(Color.green(context['current_branch'])))
    print('project type:    {}'.format(Color.green(context['project_type'].get_name())))

    # look for a command object for this command...
    for value in context["commands"]:
        if value.is_called(context):
            if value.is_available(context):
                value.do_it(context)
                context["handled"] = True
            else:
                print('command "{}" is not available in this context.'.format(Color.red_lt(value._title)))
