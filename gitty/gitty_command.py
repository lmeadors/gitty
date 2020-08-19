import pkg_resources  # part of setuptools
import subprocess
from .gitty_color import Color

from .gitty_project_type import *


def command_setup(context):

    # import these here to avoid circular references
    from .gitty_command_clean import GittyClean
    from .gitty_command_help import GittyHelp
    from .gitty_command_parent import GittyParent
    from .gitty_command_release import GittyRelease
    from .gitty_command_show import GittyShowContext
    from .gitty_command_stabilize import GittyStabilize
    from .gitty_command_task import GittyTask
    from .gitty_command_version import GittyVersion

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

    # import these here to avoid circular references
    from .gitty_project_type_maven import GittyMaven
    from .gitty_project_type_node import GittyNode
    from .gitty_project_type_pip import GittyPip

    # figure out what kind of project we are using - we'll check in the order these
    # are listed and stop as soon as we find a match - the "unknown" type always
    # matches - so we check it last.
    for project_type in [
        GittyMaven(),
        GittyPip(),
        GittyNode(),
        GittyUnknownProjectType()
    ]:
        if project_type.is_in_use(context):
            context['project_type'] = project_type
            context['project_type_name'] = project_type.get_name()
            break

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

    # now that we know what kind of project we have, get the version info from it
    GittyCommand.get_version_info(context)

    # add the current gitty version to the context
    context['gitty_version'] = pkg_resources.require("gitty")[0].version


class GittyCommand:

    # the title of the command
    _title = 'base'

    # the descriptive name of this command
    _name = 'base command that all others extend'

    # these are the aliases for this command
    _bindings = ['b', 'base']

    # these are the steps needed to accomplish this command
    _steps = []

    @staticmethod
    def title_format(title):
        return Color.white_lt(title)

    @staticmethod
    def bindings_format(bindings):
        return Color.green(bindings)

    @staticmethod
    def description_format(line):
        return Color.blue_lt(line)

    @staticmethod
    def execute_steps(steps, context):
        for step in steps:
            step.execute(context)

    @staticmethod
    def describe_steps(steps, context):
        description = []
        for step in steps:
            description += step.describe(context)
        return description

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
        for step in self._steps:
            step.execute(context)

    @staticmethod
    def execute_command(context, command):
        # show the command to be run
        print('$', ' '.join(command))

        # if we aren't doing a dry run, do the command
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

        if context['current_branch'] is None:
            return context

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


# this class describes the API for a command step - a series of these in a list will be used to define a command
class CommandStep:
    def describe(self, context):
        return []

    def execute(self, context):
        return


class CommentStep(CommandStep):

    def __init__(self, comment, context_entry_names):
        self.comment = comment
        self.context_entry_names = context_entry_names

    def describe(self, context):
        param_values = []
        for name in self.context_entry_names:
            param_values.append(context[name])
        return [
            '# ' + self.comment % tuple(param_values)
        ]


class GitCommandStep(CommandStep):
    def __init__(self, cmd_template, context_entry_names):
        self.cmd_template = cmd_template
        self.context_entry_names = context_entry_names

    def describe(self, context):
        param_values = []
        for name in self.context_entry_names:
            # print('adding {} to param-values as {}'.format(name, context[name]))
            param_values.append(context[name])
        return [
            '$ ' + self.cmd_template % tuple(param_values)
        ]

    def execute(self, context):
        param_values = []
        for name in self.context_entry_names:
            # print('adding {} to param-values as {}'.format(name, context[name]))
            param_values.append(context[name])
        command = self.cmd_template % tuple(param_values)
        GittyCommand.execute_command(context, command.split())


# this one is a bit different - sometimes we need to specify the command as an array instead of just a string
class GitCommandBump(CommandStep):
    def __init__(self, version_name):
        self.version_name = version_name
        self.command_parts = [
            'git',
            'commit',
            '-m',
            '"bumped version to {}"'
        ]

    def describe(self, context):
        description = []
        for part in self.command_parts:
            if '{}' in part:
                description.append(part.format(context[self.version_name]))
            else:
                description.append(part)
        return ['$ ' + ' '.join(description)]

    def execute(self, context):
        parts = []
        for part in self.command_parts:
            if '{}' in part:
                parts.append(part.format(context[self.version_name]))
            else:
                parts.append(part)
        GittyCommand.execute_command(context, parts)


class BumpVersionStep(CommandStep):
    def __init__(self, new_version_name):
        self.new_version_name = new_version_name

    def describe(self, context):
        return [
            '# bump version to {}'.format(context[self.new_version_name]),
        ]

    def execute(self, context):
        context['project_type'].bump_version_to(context, context[self.new_version_name])
