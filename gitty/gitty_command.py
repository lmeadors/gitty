import json
import subprocess
import sys

from .gitty_project_type import *


def command_setup(context):

    # register the available commands
    context["commands"] = [
        GittyClean(),
        GittyTask(),
        GittyRelease(),
        GittyStabilize(),
        GittyParent(),
        GittyVersion(),
        GittyShowContext(),
        GittyHelp(),
    ]

    # figure out what kind of project we are using
    for project_type in [GittyMaven(), GittyPip(), GittyUnknownProjectType()]:
        if project_type.is_in_use(context):
            context['project_type'] = project_type
            break


class GittyCommand:

    # the title of the command
    _title = 'base'

    # the descriptive name of this command
    _name = 'base command that all others extend'

    # these are the aliases for this command
    _bindings = ['b', 'base']

    @staticmethod
    def title_format(title):
        return Color.white_lt(title)

    @staticmethod
    def bindings_format(bindings):
        return Color.green(bindings)

    @staticmethod
    def description_format(line):
        return Color.blue_lt(line)

    def display_help(self, context):
        # print a blank line...
        print()
        # show the help for the command
        print('{}: {}'.format(
            self.title_format(self._title),
            self.bindings_format(self._bindings)
        ))
        for line in self.get_description(context):
            print('  {}'.format(self.description_format(line)))

    def get_description(self, context):
        return [self._name]

    def is_available(self, context):
        # is this command available?
        return True

    def is_called(self, context):
        command_name = context['command']
        return command_name in self._bindings

    def do_it(self, context):
        return

    @staticmethod
    def execute_command(context, command):
        print('$', ' '.join(command))

        if not context['dry_run']:
            try:
                return subprocess.check_output(command)
            except subprocess.CalledProcessError as e:
                print(Color.red_lt(str(e.output)))
            # finished = output.split('\n')
            # for line in finished:
            #     print(line)
            # return
            # output = subprocess.check_output(cmd)
            # print(output, '\n')

    @staticmethod
    def get_version_info(context):

        context['project_type'].get_version_info(context)

        context['master'] = True
        if context['branch_parts'] is not None:
            if len(context['branch_parts']) > 1:
                context['master'] = False

        if context['branch_parts'][0] == 'tasks' or context['branch_parts'][0] == 'master':
            context['stabilization'] = False
        else:
            context['stabilization'] = True

        context['on_a_task'] = context['current_branch'].startswith(context['task_prefix'])
        context['on_a_master'] = (context['branch_parts'][-1] == 'master')
        context['on_a_release'] = (context['branch_parts'][-1] == 'releases')

        context['current_version_parts'] = context['current_version'].split('.')

        if context['stabilization']:
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
        else:
            context['parent_version_branch'] = 'master'

        return context

    def bump_version_to(self, context, new_version):
        context['project_type'].bump_version_to(context, new_version)


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


class GittyShowContext(GittyCommand):
    _title = 'show'
    _name = 'show current context (useful for debugging)'
    _bindings = ['show']

    def is_available(self, context):
        return True

    def do_it(self, context):
        def without_keys(con):
            return {x: con[x] for x in con if x not in {
                # some context elements can't be represented as json - exclude them here
                'commands',
                'project_type'
            }}

        print('-- current context --')
        print(json.dumps(without_keys(context), indent=2))
        print('---------------------')


class GittyClean(GittyCommand):
    _title = 'cleanup'
    _name = 'freshen up around the place - pull changes (with rebase) and cleanup unused branches'
    _bindings = ['c', 'clean']

    def is_available(self, context):
        return True

    def do_it(self, context):
        response = self.execute_command(context, 'git status -s'.split())
        if response:
            # this repo isn't "clean", so don't continue...
            print(response.decode())
            print('aborting cleanup process - repository has outstanding changes')
            return
        self.execute_command(context, 'git fetch --all --prune'.split())
        self.execute_command(context, 'git pull --rebase'.split())
        command_output = self.execute_command(context, 'git branch --no-color --merged'.split())
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
                self.execute_command(context, 'git branch -d {}'.format(branch_name).split())
            else:
                print('leaving branch "{}" ({})'.format(branch_name, retain_reason))

    def get_description(self, context):
        return [
            '$ git fetch --all --prune',
            '$ git pull --rebase',
            '$ git branch --no-color --merged',
            '  (remove SOME merged LOCAL branches - leave masters and releases)'
        ]


class GittyParent(GittyCommand):
    _title = 'parent'
    _name = 'go to parent branch'
    _bindings = ['p', 'parent']

    def is_available(self, context):
        return not context['master']

    def do_it(self, context):
        self.execute_command(context, 'git checkout {}'.format(context['parent_version_branch']).split())

    def get_description(self, context):
        return ['{} ({})'.format(self._name, context['parent_version_branch'])]


class GittyStabilize(GittyCommand):
    _title = 'stabilize'
    _name = 'create stabilization ecosystem'
    _bindings = ['s', 'stabilize']

    def is_available(self, context):
        return not context['on_a_task']

    def do_it(self, context):
        if len(context['branch_parts']) > 1:
            self.stabilize_from_point(context)
        else:
            self.stabilize_from_master(context)
        return

    def get_description(self, context):
        # stab from master
        return [
            '$ git checkout -b {}'.format(context['new_stabilization_branch']),
            '$ git checkout -b {}'.format(context['new_release_branch']),
            '$ git checkout master',
            '  (bump version to {})'.format(context['next_master_version']),
            '$ git add {}'.format(context['project_file']),
            '$ git commit -m "bumped version to {}"'.format(context['next_master_version'])
        ]

    def stabilize_from_master(self, context):
        self.execute_command(context, 'git checkout -b {}'.format(context['new_stabilization_branch']).split())
        self.execute_command(context, 'git checkout -b {}'.format(context['new_release_branch']).split())
        self.execute_command(context, 'git checkout master'.split())
        self.bump_version_to(context, context['next_master_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to {}"'.format(context['next_master_version'])
        ])
        return

    def stabilize_from_point(self, context):
        self.execute_command(context, 'git checkout -b {}'.format(context['new_release_branch']).split())
        self.execute_command(context, 'git checkout -b {}'.format(context['new_stabilization_branch']).split())
        self.bump_version_to(context, context['new_stabilization_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to {}"'.format(context['new_stabilization_version'])
        ])
        if not context['hotfix']:
            self.execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
            self.bump_version_to(context, context['next_stable_version'])
            self.execute_command(context, 'git add {}'.format(context['project_file']).split())
            self.execute_command(context, [
                'git',
                'commit',
                '-m',
                '"bumped version to {}"'.format(context['next_stable_version'])
            ])


class GittyHelp(GittyCommand):
    _title = 'help'
    _name = 'what am i even doing here?'
    _bindings = ['h', 'help']

    def do_it(self, context):
        print('available commands on branch "{}" are:'.format(Color.white_lt(context['current_branch'])))
        commands = context["commands"]
        for command in commands:
            if command.is_available(context):
                command.display_help(context)
        # print a blank line...
        print()


class GittyTask(GittyCommand):
    _title = 'task'
    _name = 'start a new task branch (name is required)'
    _bindings = ['t', 'task']

    def is_available(self, context):
        return not context['on_a_task']

    def do_it(self, context):
        # we need a task name - like 123234_some_task_name
        if len(sys.argv) > 2:
            context['task_name'] = sys.argv[2]
            git_command = 'git checkout -b {}{}'.format(context['task_prefix'], context['task_name'])
            if len(context['branch_parts']) > 1:
                self.execute_command(context, git_command.split())
            else:
                self.execute_command(context, git_command.split())

    def get_description(self, context):
        sample_task_name = '123234_your_task_here'
        return [
            "{}, so if you said 'gitty {} {}', then you'd get this:".format(
                self._name, self._bindings[0], sample_task_name
            ),
            '$ git checkout -b {}{}'.format(context['task_prefix'], sample_task_name)
        ]


class GittyRelease(GittyCommand):
    _title = 'release'
    _name = 'snap a new release from here'
    _bindings = ['r', 'release']

    def is_available(self, context):
        return not context['on_a_task']

    def get_description(self, context):
        point_release = len(context['branch_parts']) > 1

        steps = []

        if point_release:
            # this is a point release
            steps += [
                '{} - {}'.format(self._name, 'this is already in a stabilization ecosystem'),
                '$ git checkout {}'.format(context['current_release_branch']),
                '$ git merge {}'.format(context['current_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['release_version'], context['project_file'], context['current_release_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['release_version']),
                '$ git tag {}'.format(context['release_version']),
                '$ git checkout {}'.format(context['current_branch']),
                '$ git merge {}'.format(context['current_release_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['next_stable_version'], context['project_file'], context['current_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['next_stable_version']),
            ]
        else:
            # this is a new release from master - there are extra steps here
            steps += [
                '{} - {}'.format(self._name, 'this will create a new stabilization ecosystem'),
                '$ git checkout -b ' + context['new_stabilization_branch'],
                '$ git checkout -b ' + context['new_release_branch'],
                '  (bump version to {} in {} on {} branch)'.format(
                    context['release_version'], context['project_file'], context['new_release_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['release_version']),
                '$ git tag {}'.format(context['release_version']),
                '$ git checkout {}'.format(context['new_stabilization_branch']),
                # this is a transient branch/merge, so we won't actually merge, we'll just mark it as merged
                '$ git merge --strategy=ours {}'.format(context['new_release_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['next_stable_version'], context['project_file'], context['new_stabilization_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['next_stable_version']),
                '$ git checkout master',
                '$ git merge --strategy=ours {}'.format(context['new_stabilization_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['next_master_version'], context['project_file'], 'master'
                ),
                '$ git add {}'.format(context['project_file']),
                # this has spaces in a parameter, so it's different...
                '$ git commit -m "bumped version to {}"'.format(context['next_master_version'])
            ]

        return steps

    def do_it(self, context):
        if len(context['branch_parts']) > 1:
            self.release_from_point(context)
        else:
            self.release_from_master(context)

    def release_from_master(self, context):
        self.execute_command(context, ('git checkout -b ' + context['new_stabilization_branch']).split())
        self.execute_command(context, ('git checkout -b ' + context['new_release_branch']).split())
        self.bump_version_to(context, context['release_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['release_version'] + '"'
        ])
        self.execute_command(context, 'git tag {}'.format(context['release_version']).split())
        self.execute_command(context, 'git checkout {}'.format(context['new_stabilization_branch']).split())
        # this is a transient branch/merge, so we won't actually merge, we'll just mark it as merged
        self.execute_command(context, 'git merge --strategy=ours {}'.format(context['new_release_branch']).split())
        self.bump_version_to(context, context['next_stable_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['next_stable_version'] + '"'
        ])
        self.execute_command(context, 'git checkout master'.split())
        self.execute_command(context, 'git merge --strategy=ours {}'.format(context['new_stabilization_branch']).split())
        self.bump_version_to(context, context['next_master_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['next_master_version'] + '"'
        ])

    def release_from_point(self, context):
        self.execute_command(context, 'git checkout {}'.format(context['current_release_branch']).split())
        self.execute_command(context, 'git merge {}'.format(context['current_branch']).split())
        self.bump_version_to(context, context['release_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['release_version'] + '"'
        ])
        self.execute_command(context, 'git tag {}'.format(context['release_version']).split())
        self.execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
        self.execute_command(context, 'git merge {}'.format(context['current_release_branch']).split())
        self.bump_version_to(context, context['next_stable_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['next_stable_version'] + '"'
        ])


class Color:
    _black = '\u001b[30m'
    _black_lt = '\u001b[30;1m'
    _red = '\u001b[31m'
    _red_lt = '\u001b[31;1m'
    _green = '\u001b[32m'
    _green_lt = '\u001b[32;1m'
    _yellow = '\u001b[33m'
    _yellow_lt = '\u001b[33;1m'
    _blue = '\u001b[34m'
    _blue_lt = '\u001b[34;1m'
    _magenta = '\u001b[35m'
    _magenta_lt = '\u001b[35;1m'
    _cyan = '\u001b[36m'
    _cyan_lt = '\u001b[36;1m'
    _white = '\u001b[37m'
    _white_lt = '\u001b[37;1m'
    _reset = '\u001b[0m'

    @staticmethod
    def white_lt(text):
        return '{}{}{}'.format(Color._white_lt, text, Color._reset)

    @staticmethod
    def red(text):
        return '{}{}{}'.format(Color._red, text, Color._reset)

    @staticmethod
    def red_lt(text):
        return '{}{}{}'.format(Color._red_lt, text, Color._reset)

    @staticmethod
    def green(text):
        return '{}{}{}'.format(Color._green, text, Color._reset)

    @staticmethod
    def yellow(text):
        return '{}{}{}'.format(Color._yellow, text, Color._reset)

    @staticmethod
    def blue(text):
        return '{}{}{}'.format(Color._blue, text, Color._reset)

    @staticmethod
    def blue_lt(text):
        return '{}{}{}'.format(Color._blue_lt, text, Color._reset)
