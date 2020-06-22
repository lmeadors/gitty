from os import path
import pkg_resources  # part of setuptools
import subprocess
import sys

from gitty.gitty_support_maven import *
from gitty.gitty_support_node import *
from gitty.gitty_support_pip import *
from gitty.gitty_support_unknown import *


def help_cmd(context):
    get_version_info(context)
    print('current version is "{}"'.format(context['current_version']))
    print('current branch is "{}"'.format(context['current_branch']))

    if context['branch_parts'] is not None:
        if len(context['branch_parts']) > 1:
            # a release branch
            print('available commands on branch "{}" are:'.format(context['current_branch']))
            if not context['on_a_task']:
                print('  release')
                print('     - merge "{}" to "{}"'.format(context['current_branch'], context['current_release_branch']))
                print('     - set version to "{}" on branch "{}"'
                      .format(context['release_version'], context['current_release_branch']))
                print('     - create a new tagged release named "{}" on branch "{}"'
                      .format(context['release_version'], context['current_release_branch']))
                print('     - merge branch "{}" to "{}"'
                      .format(context['current_release_branch'], context['current_branch']))
                print('     - set version to "{}" on branch "{}"'
                      .format(context['next_stable_version'], context['current_branch']))

                print('  task [name] - create a new task branch named "{}[name]"'
                      .format(context['task_prefix']))

                if context['hotfix']:
                    print('  stabilize (hotfix)')
                else:
                    print('  stabilize')

                print('     - create a new release branch named "{}"'.format(context['new_release_branch']))
                print('     - create a new stabilization branch named "{}"'.format(context['new_stabilization_branch']))
                print('     - set version to "{}" on branch "{}"'.format(context['new_stabilization_version'], context['new_stabilization_branch']))

                if not context['hotfix']:
                    print('     - set version to "{}" on branch "{}"'.format(
                        context['next_stable_version'], context['current_branch'])
                    )

        else:
            # master
            print('available commands on branch "{}" are:'.format(context['current_branch']))
            print('  release')
            print('     - create a new stabilization branch named "{}"'.format(context['new_stabilization_branch']))
            print('     - create a new release branch named "{}"'.format(context['new_release_branch']))
            print('     - set version to "{}" on branch "{}"'
                  .format(context['release_version'], context['new_release_branch']))
            print('     - create a new tagged release named "{}" on branch "{}"'
                  .format(context['release_version'], context['new_release_branch']))
            print('     - merge branch "{}" to "{}"'
                  .format(context['new_release_branch'], context['new_stabilization_branch']))
            print('     - set version to "{}" on branch "{}"'
                  .format(context['next_stable_version'], context['new_stabilization_branch']))
            print('     - merge branch "{}" to "{}"'
                  .format(context['new_stabilization_branch'], context['current_branch']))
            print('     - set version to "{}" on branch "{}"'
                  .format(context['next_master_version'], context['current_branch']))
            print('  task [name]')
            print('     - create a new task branch named "{}[name]"'.format(context['task_prefix']))
            print('  stabilize')
            print('     - create a new stabilization branch named "{}"'.format(context['new_stabilization_branch']))
            print('     - create a new release branch named "{}"'.format(context['new_release_branch']))
            print('     - set version to "{}" on branch "{}"'
                  .format(context['next_master_version'], context['current_branch']))

        if not context['master']:
            print('  parent')
            print('     - checkout parent version branch "{}"'.format(context['parent_version_branch']))

        print('  cleanup')
        print('     - remove any local branches that have been merged to "{}"'.format(context['current_branch']))
        print('     - remove any refs to remote branches that have been removed')
        print('  version')
        print('     - show current gitty version ({})'.format(context['gitty_version']))

    # show(context)


def setup(context):

    # we'll actually do stuff, unless this is over-written
    context['dry_run'] = False

    # add the current gitty version to the context
    context['gitty_version'] = pkg_resources.require("gitty")[0].version

    try:
        current_branch_output = subprocess.check_output('git rev-parse --abbrev-ref HEAD'.split())
        context['current_branch'] = current_branch_output.decode().strip()
        context['branch_parts'] = context['current_branch'].split("/")
        if len(context['branch_parts']) > 1:
            context['task_prefix'] = context['branch_parts'][0] + '/tasks/'
        else:
            context['task_prefix'] = 'tasks/'

    except subprocess.CalledProcessError:
        print('current directory is not a git repository')
        context['current_branch'] = None
        context['branch_parts'] = None
        context['task_prefix'] = None
        context['dry_run'] = True

    if path.exists('package.json'):
        context['project_type'] = 'nodejs'
    elif path.exists('pom.xml'):
        context['project_type'] = 'maven'
    elif path.exists('setup.py'):
        context['project_type'] = 'pip'
    else:
        context['project_type'] = 'unknown'

    get_version_info(context)

    return context


def command_handler(context):
    switcher = {
        'help': help_cmd,
        # release commands and handlers
        'release': release,
        'r': release,
        'release_from_master': release_from_master,
        'release_from_point': release_from_point,
        # tsk commands and handlers
        'task': task,
        't': task,
        'task_from_master': task_from_master,
        'task_from_point': task_from_point,
        # stable
        's': stabilize,
        'stabilize': stabilize,
        'stabilize_from_master': stabilize_from_master,
        'stabilize_from_point': stabilize_from_point,
        'v': version,
        'version': version,
        'p': parent,
        'parent': parent,
        'c': cleanup,
        'clean': cleanup
    }
    print("command:", context['command'])
    switcher.get(context['command'])(context)


def cleanup(context):
    # show(context)
    # git branch --no-color --merged
    execute_command(context, 'git fetch --all --prune'.split())
    command_output = execute_command(context, 'git branch --no-color --merged'.split())
    output_decoded = command_output.decode('utf-8')
    output_lines = output_decoded.splitlines()
    for line in output_lines:
        branch_name = line.split()[-1]

        retain_reason = ''
        if branch_name.endswith('/master') or branch_name == 'master':
            retain_reason = 'master branches are preserved'
        if branch_name.endswith('/releases'):
            retain_reason = 'release branches are preserved'
        if branch_name == context['current_branch']:
            retain_reason = 'current branch is preserved'

        if not retain_reason:
            execute_command(context, 'git branch -d {}'.format(branch_name).split())
        else:
            print('leaving branch "{}" ({})'.format(branch_name, retain_reason))
    return


def parent(context):
    execute_command(context, 'git checkout {}'.format(context['parent_version_branch']).split())


def version(context):
    print('current gitty version: {}'.format(context['gitty_version']))


def stabilize(context):
    get_version_info(context)
    if len(context['branch_parts']) > 1:
        context['command'] = 'stabilize_from_point'
    else:
        context['command'] = 'stabilize_from_master'
    show(context)
    command_handler(context)
    return


def stabilize_from_master(context):
    execute_command(context, 'git checkout -b {}'.format(context['new_stabilization_branch']).split())
    execute_command(context, 'git checkout -b {}'.format(context['new_release_branch']).split())
    execute_command(context, 'git checkout master'.split())
    # execute_command(context, 'git merge --strategy ours {}'.format(context['new_stabilization_branch']).split())
    # print('(bump project version to {})'.format(context['next_master_version']))
    bump_version_to(context, context['next_master_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to {}"'.format(context['next_master_version'])
    ])
    return


def stabilize_from_point(context):
    execute_command(context, 'git checkout -b {}'.format(context['new_release_branch']).split())
    execute_command(context, 'git checkout -b {}'.format(context['new_stabilization_branch']).split())
    bump_version_to(context, context['new_stabilization_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to {}"'.format(context['new_stabilization_version'])
    ])
    if not context['hotfix']:
        execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
        bump_version_to(context, context['next_stable_version'])
        execute_command(context, 'git add {}'.format(context['project_file']).split())
        execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to {}"'.format(context['next_stable_version'])
        ])
    return


def release_from_master(context):
    # print('make a new release from master:', context)
    get_version_info(context)
    # show(context)
    # current_branch_cmd = ['git', 'checkout', '-b', context['new_stab_branch']]
    # current_branch_output = subprocess.check_output(current_branch_cmd)

    # print('branch from master to', context['new_stabilization_branch'])
    execute_command(context, ('git checkout -b ' + context['new_stabilization_branch']).split())
    # print('branch from', context['new_stabilization_branch'], 'to', context['new_release_branch'])
    execute_command(context, ('git checkout -b ' + context['new_release_branch']).split())
    # print('set pom.xml on', context['new_release_branch'], 'to', context['release_version'], "(non snapshot)")
    bump_version_to(context, context['release_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    # this has spaces in a parameter, so it's different...
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['release_version'] + '"'
    ])
    # print('tag as', context['release_version'])
    execute_command(context, 'git tag {}'.format(context['release_version']).split())
    execute_command(context, 'git checkout {}'.format(context['new_stabilization_branch']).split())
    # this is a transient branch/merge, so we won't actually merge, we'll just mark it as merged
    execute_command(context, 'git merge --strategy=ours {}'.format(context['new_release_branch']).split())
    bump_version_to(context, context['next_stable_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    # this has spaces in a parameter, so it's different...
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['next_stable_version'] + '"'
    ])
    execute_command(context, 'git checkout master'.split())
    execute_command(context, 'git merge --strategy=ours {}'.format(context['new_stabilization_branch']).split())
    bump_version_to(context, context['next_master_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['next_master_version'] + '"'
    ])


def execute_command(context, command):
    print('$', ' '.join(command))

    if not context['dry_run']:
        try:
            return subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            print(str(e.output))
        # finished = output.split('\n')
        # for line in finished:
        #     print(line)
        # return
        # output = subprocess.check_output(cmd)
        # print(output, '\n')


def release_from_point(context):
    get_version_info(context)
    execute_command(context, 'git checkout {}'.format(context['current_release_branch']).split())
    execute_command(context, 'git merge {}'.format(context['current_branch']).split())
    bump_version_to(context, context['release_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['release_version'] + '"'
    ])
    execute_command(context, 'git tag {}'.format(context['release_version']).split())
    execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
    # merge changes, but not really.
    execute_command(context, 'git merge {}'.format(context['current_release_branch']).split())
    bump_version_to(context, context['next_stable_version'])
    execute_command(context, 'git add {}'.format(context['project_file']).split())
    execute_command(context, [
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['next_stable_version'] + '"'
    ])


def show(context):
    print('-- current context --')
    print(json.dumps(context, indent=2))
    print('---------------------')


def task_from_master(context):
    execute_command(context, 'git checkout -b {}{}'.format(context['task_prefix'], context['task_name']).split())


def task_from_point(context):
    execute_command(context, 'git checkout -b {}{}'.format(context['task_prefix'], context['task_name']).split())


def task(context):
    print('make a new task branch')
    # we need a task name - like 123234_some_task_name
    if len(sys.argv) > 2:
        context['task_name'] = sys.argv[2]
        if len(context['branch_parts']) > 1:
            context['command'] = 'task_from_point'
        else:
            context['command'] = 'task_from_master'
    else:
        context['command'] = 'help'

    # print('release command:', context['command'])
    command_handler(context)


def release(context):
    if len(context['branch_parts']) > 1:
        context['command'] = 'release_from_point'
    else:
        context['command'] = 'release_from_master'
    command_handler(context)


def get_version_info(context):
    switcher = {
        'maven': get_version_info_maven,
        'nodejs': get_version_info_node,
        'pip': get_version_info_pip,
        'unknown': get_version_info_unknown
    }
    switcher.get(context['project_type'])(context)
    context['master'] = True
    if context['branch_parts'] is not None:
        if len(context['branch_parts']) > 1:
            context['master'] = False
    context['on_a_task'] = context['current_branch'].startswith(context['task_prefix'])
    context['on_a_master'] = (context['branch_parts'][-1] == 'master')
    context['on_a_release'] = (context['branch_parts'][-1] == 'releases')

    context['current_version_parts'] = context['current_version'].split('.')

    if context['on_a_task'] or context['on_a_release']:
        # we're working a task - the parent is different...
        context['parent_version_branch'] = context['branch_parts'][0] + '/master'
    else:
        if len(context['current_version_parts']) < 4:
            # parent is just master
            context['parent_version_branch'] = 'master'
        else:
            # parent is a shortened version
            context['parent_version_branch'] = '.'.join(context['current_version_parts'][:-2]) + '/master'

    return context


def bump_version_to(context, new_version):
    switcher = {
        'maven': bump_maven_version_to,
        'nodejs': bump_node_version_to,
        'pip': bump_pip_version_to,
        'unknown': bump_unknown_version_to
    }
    return switcher.get(context['project_type'])(context, new_version)
