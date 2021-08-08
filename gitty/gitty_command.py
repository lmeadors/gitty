import pkg_resources  # part of setuptools
import subprocess
from .gitty_color import Color
from .gitty_executor import DescribeExecutor, CommandExecutor

from .gitty_project_type import *


def command_setup(context):

    # import these here to avoid circular references
    from .gitty_command_clean import GittyClean
    from .gitty_command_head import GittyHead
    from .gitty_command_help import GittyHelp
    from .gitty_command_parent import GittyParent
    from .gitty_command_plugins import GittyPlugins
    from .gitty_command_release import GittyRelease
    from .gitty_command_show import GittyShowContext
    # from .gitty_command_stabilize import GittyStabilize
    from .gitty_command_task import GittyTask
    from .gitty_command_version import GittyVersion
    from .gitty_git_api import GitAPI

    # set up the git API if it's missing
    if 'git_api' not in context:
        context['executor'] = CommandExecutor()
        context['git_api'] = GitAPI(context["executor"])

    # register the available commands
    context["commands"] = [
        # load this early, so it can add commands, executors, apis, etc
    ]
    context["commands"] += [
        GittyPlugins(context),
        GittyClean(),
        GittyTask(),
        GittyRelease(),
        # GittyStabilize(),
        GittyParent(),
        GittyVersion(),
        GittyShowContext(),
        GittyHelp(),
        GittyHead(),
    ]

    # import these here to avoid circular references
    # todo: add plugin support here - convert these to plugins?
    from .gitty_project_type_maven import GittyMaven
    from .gitty_project_type_node import GittyNode
    from .gitty_project_type_pip import GittyPip

    # figure out what kind of project we are using - we'll check in the order these
    # are listed and stop as soon as we find a match - the "unknown" type always
    # matches - so we check it last.
    # todo: include plugin types here

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

    GittyCommand.verify_context_has_project_type_info(context)

    try:
        current_branch = context['git_api'].get_current_branch(context)
        GittyCommand.add_branch_info_to_context(context, current_branch)

    except subprocess.CalledProcessError:

        # be extra sure we don't change anything here...
        context['dry_run'] = True

        print(Color.red_lt('current directory is not a git repository - set "dry_run=True"'))
        # set the git branch info all to "None"
        for key in [
            'current_branch',
            'current_release_branch',
            'new_release_branch',
            'new_stabilization_branch',
            'branch_parts',
            'task_prefix',
            'hotfix'
        ]:
            context[key] = None

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
    _bindings = ['base', 'b']

    # these are the steps needed to accomplish this command
    _steps = []

    def bindings_string(self):
        return self._bindings[0]


    @staticmethod
    def add_branch_info_to_context(context, current_branch):


        # what is the commit hash
        if 'git_ref' not in context:
            # by default, use the current HEAD
            context['git_ref'] = 'HEAD'

        git_api = context['git_api']

        context['git_hash'] = git_api.git_hash(context, quiet=True)
        context['git_remote'] = git_api.git_remote(context, quiet=True)

        # is this commit tagged? if so, this could be a hotfix
        context['tags_on_commit'] = git_api.get_tags_on_commit(context)

        # split the branch name into its components
        branch_parts = current_branch.split("/")

        # are we on THE master branch or any other master branch?
        the_master = current_branch == context['trunk']
        a_master = branch_parts[-1] == context['trunk']

        # are we on a task branch?
        a_task = context['task_prefix'] in branch_parts
        a_release = context['release_prefix'] in branch_parts

        if not a_task and not a_release:
            if the_master:
                task_prefix = context['task_prefix'] + '/'
            else:
                task_prefix = branch_parts[0] + '/' + context['task_prefix'] + '/'
        else:
            # we're on a task or release branch - we don't create task branches from those
            task_prefix = None

        # figure out if we're in a stabilization ecosystem
        part_count = len(branch_parts)
        if part_count > 2:
            # this is a task on a stabilization ecosystem
            is_stable = True
        elif the_master:
            # THE master is not a stabilization ecosystem
            is_stable = False
        elif a_release:
            # a release only comes from a stabilization ecosystem
            is_stable = True
        elif a_master:
            # a master that isn't THE master is in a stabilization ecosystem
            is_stable = True
        else:
            # task branches are not stable
            is_stable = False

        if the_master:
            # no release branch in this case - this is so the project types don't have to set this
            context['current_release_branch'] = None
            context['new_stabilization_version'] = None

        if a_task:
            # no release or stabilization from here - this is so the project types don't have to set this
            context['new_stabilization_branch'] = None
            context['new_stabilization_version'] = None
            context['new_release_branch'] = None
            context['current_release_branch'] = None

        # update the context with the additional branch info
        context['current_branch'] = current_branch
        context['the_master'] = the_master
        context['branch_parts'] = branch_parts
        context['a_master'] = a_master
        context['a_task'] = a_task
        context['a_release'] = a_release
        context['task_prefix'] = task_prefix
        context['is_stable'] = is_stable

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
            if context.get('continue', True):
                step.execute(context, quiet=True)

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

    def display_head(self, context):
        # print a blank line...
        print()
        # show the help for the command
        print('{}: {}'.format(
            self.title_format(self._title),
            self.bindings_format(self._bindings)
        ))

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
    def execute_command_safe(context, command):
        # this is to be used to run a command that is safe from the perspective of a "dry run"
        # show the command to be run
        print('$', ' '.join(command))

        try:
            return subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            print(Color.red_lt(str(e.output)))

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
        else:
            return bytes(0)

    @staticmethod
    def verify_context_has_version_info(context):
        expected_keys = [
            'current_release_branch',
            'current_version',
            'hotfix',
            'new_release_branch',
            'new_stabilization_branch',
            'new_stabilization_version',
            'next_master_version',
            'next_stable_version',
            'release_version',
        ]
        for key in expected_keys:
            if key not in context:
                print(Color.yellow(
                    'expected to find key "{}" in context, but it was not present - this can cause problems'.format(
                        key
                    )
                ))

    @staticmethod
    def verify_context_has_project_type_info(context):
        expected_keys = [
            'project_type',
            'project_type_name',
            'project_file',
        ]
        for key in expected_keys:
            if key not in context:
                print(Color.yellow(
                    'expected to find key "{}" in context, but it was not present - this can cause problems'.format(
                        key
                    )
                ))

    @staticmethod
    def get_version_info(context):

        context['project_type'].get_version_info(context)
        GittyCommand.verify_context_has_version_info(context)

        if context['current_branch'] is None:
            return context
        if context['current_version'] is None:
            return context

        context['current_version_parts'] = context['current_version'].split('.')

        if context['is_stable']:
            if context['a_task'] or context['a_release']:
                # we're on a task or release branch - the parent is different...
                context['parent_version_branch'] = context['branch_parts'][0] + '/' + context['trunk']
            else:
                if len(context['current_version_parts']) <= 4:
                    # parent is just master
                    context['parent_version_branch'] = context['trunk']
                else:
                    # parent is a shortened version
                    context['parent_version_branch'] = '.'.join(context['current_version_parts'][:-2]) + '/' + context['trunk']
        else:
            context['parent_version_branch'] = context['trunk']

        return context


# this class describes the API for a command step - a series of these in a list will be used to define a command
class CommandStep:
    def describe(self, context):
        return []

    def execute(self, context, quiet):
        return


class CommentStep(CommandStep):

    def __init__(self, comment, context_entry_names):
        self.comment = comment
        self.context_entry_names = context_entry_names

    def describe(self, context, quiet=False):
        param_values = []
        for name in self.context_entry_names:
            param_values.append(context[name])
        return [
            '# ' + self.comment % tuple(param_values)
        ]

    def execute(self, context, quiet=True):
        # do nothing
        return []


class GitCommandStep(CommandStep):
    # todo: migrate this to use the new git api in the context
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

    def execute(self, context, quiet=False):
        param_values = []
        for name in self.context_entry_names:
            # print('adding {} to param-values as {}'.format(name, context[name]))
            param_values.append(context[name])
        command = self.cmd_template % tuple(param_values)
        GittyCommand.execute_command(context, command.split())


class GitCheckoutNewCommand(CommandStep):
    def __init__(self, branch_key_name):
        self.branch_key_name = branch_key_name

    def describe(self, context):
        executor = DescribeExecutor()
        return context['git_api'].checkout_new(context, context[self.branch_key_name], False, executor)

    def execute(self, context, quiet):
        return context['git_api'].checkout_new(context, context[self.branch_key_name], quiet, None)


class GitCheckoutExistingCommand(CommandStep):
    def __init__(self, branch_key_name):
        self.branch_key_name = branch_key_name

    def describe(self, context):
        executor = DescribeExecutor()
        return context['git_api'].checkout_existing(context, context[self.branch_key_name], False, executor)

    def execute(self, context, quiet):
        return context['git_api'].checkout_existing(context, context[self.branch_key_name], quiet, None)


class GitStatusCheckStep(CommandStep):
    def describe(self, context):
        return ['# make sure the git repo has no outstanding changes']

    def execute(self, context, quiet):
        response = context['git_api'].status_is_clean(context, quiet)
        # response = GittyCommand.execute_command_safe(context, 'git status -s'.split())
        if response:
            # this repo isn't "clean", so don't continue...
            print(Color.red(response))
            print(Color.red_lt('aborting cleanup process - repository has outstanding changes'))
            # set context['continue'] = False if we don't want to continue
            context['continue'] = False


class GitCheckoutMasterCommand(CommandStep):

    def describe(self, context):
        executor = DescribeExecutor()
        return context['git_api'].checkout_existing(context, context['trunk'], False, executor)

    def execute(self, context, quiet):
        return context['git_api'].checkout_existing(context, context['trunk'], quiet, None)


class GitShowUnmergedBranchesStep(CommandStep):

    def describe(self, context):
        return ['git branch -a --no-color --no-merged']

    def execute(self, context, quiet):
        print("Unmerged branches")
        print("-----------------")
        unmerged_branch_names = context['git_api'].get_unmerged_branch_names(context)
        for name in unmerged_branch_names:
            print(' - {0}'.format(name))
        return []


class GitCleanStep(CommandStep):

    def describe(self, context):

        description = [
            '# remove select LOCAL branches that have been merged to current branch ({})'.format(context['current_branch'])
        ]

        if 'git_remote' in context:
            description.append('# (use --remote to also remote REMOTE branches from {})'.format(context['git_remote']))

        return description

    def execute(self, context, quiet):
        # todo: migrate this to use the new git api in the context: get_merged_branch_names()
        command_output = GittyCommand.execute_command_safe(context, 'git branch --no-color --merged'.split())
        output_decoded = command_output.decode('utf-8')
        output_lines = output_decoded.splitlines()
        for line in output_lines:
            branch_name = line.split()[-1]

            retain_reason = ''
            if branch_name.endswith('/'+context['trunk']) or branch_name == context['trunk']:
                retain_reason = context['trunk'] + ' branches are preserved'
            if branch_name.endswith('/' + context['release_prefix']):
                retain_reason = 'release branches are preserved'
            if branch_name == context['current_branch']:
                retain_reason = 'current branch is preserved'

            if not retain_reason:
                # todo: migrate this to use the new git api in the context: remove_branch()
                GittyCommand.execute_command(context, 'git branch -d {}'.format(branch_name).split())
                if 'remote' in context and 'git_remote' in context:
                    if context['remote']:
                        GittyCommand.execute_command(
                            context,
                            'git push --delete {} {}'.format(context['git_remote'], branch_name).split()
                        )
            else:
                print('leaving branch "{}" ({})'.format(branch_name, retain_reason))


class GitCommandBumpNew(CommandStep):
    def __init__(self, version_name):
        self.version_name = version_name

    def describe(self, context):
        executor = DescribeExecutor()
        return context['git_api'].commit('bumped version to {}'.format(context[self.version_name]), executor)

    def execute(self, context, quiet):
        return context['git_api'].commit('bumped version to {}'.format(context[self.version_name]))


class GitCommandBump(CommandStep):
    # this one is a bit different - sometimes we need to specify the command as an array instead of just a string
    # todo: migrate this to use the new git api in the context
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

    def execute(self, context, quiet):
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

    def execute(self, context, quiet):
        context['project_type'].bump_version_to(context, context[self.new_version_name])

