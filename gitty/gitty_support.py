import os
from pathlib import Path

from gitty.gitty_command import *
import sys


def setup(context):

    # look for .gittyrc files - they can live in 2 places:
    # - the user's home directory
    # - the current working directory (CWD)
    # if both exist and define overlapping values, the one in the CWD is used
    # these are the global defaults
    grc_config = {
        'trunk': 'master',
        'task_prefix': 'tasks',
        'release_prefix': 'releases'
    }
    home_config_location = os.path.join(Path.home(), ".gittyrc")
    local_config_location = ".gittyrc"
    if os.path.exists(home_config_location):
        with open(home_config_location) as f:
            for line in f:
                (key, val) = line.split("=")
                grc_config[key] = val.strip()

    if os.path.exists(local_config_location):
        with open(local_config_location) as f:
            for line in f:
                (key, val) = line.split("=")
                grc_config[key] = val.strip()

    # if len(grc_config) == 0:
    #     print(
    #         "no config files found at '{}' or '{}', using defaults.".format(
    #             home_config_location, local_config_location
    #         )
    #     )

    context.update(grc_config)
    # print(context)

    # get any CLI switches in the context:
    # look at any parameter that starts with '--', and if the NEXT parameter doesn't
    # start with '--', assume it's the value for this parameter
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

    # if there's no command set now, default it to 'head'
    context['command'] = context.get('command', 'head')

    if context.get('no_color', False):
        Color.disable_color()

    command_setup(context)

    return context


def command_handler(context):

    # if we get here and this isn't set yet, default it to False
    context['dry_run'] = context.get('dry_run', False)

    # show some minimal context info
    if len(context['tags_on_commit']) > 0:
        tags = '(tags: {})'.format(Color.green(context['tags_on_commit']))
    else:
        tags = ''
    print(
        'current branch:            {} {}'.format(
            Color.green(context['current_branch']),
            tags
        )
    )
    print(
        'project type / version:    {} / {}'.format(
            Color.green(context['project_type'].get_name()),
            Color.green(context.get('current_version', 'unknown'))
        )
    )

    if context['dry_run']:
        dry_run = (Color.red_lt('(dry run)'))
    else:
        dry_run = ''

    print(
        'command name:              {} {}'.format(
            Color.green(context['command']),
            dry_run
        )
    )

    # look for a command object for this command...
    for value in context["commands"]:
        if value.is_called(context):
            if value.is_available(context):
                # we found one that is available for this context - do it then return what it returns
                return value.do_it(context)
            else:
                print('command "{}" is not available in this context.'.format(Color.red_lt(value._title)))
