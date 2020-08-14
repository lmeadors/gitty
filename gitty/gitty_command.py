import json
import subprocess


def command_setup(context):
    context["commands"] = [
        GittyVersion(),
        GittyShowContext(),
        GittyClean()
    ]
    return


class GittyCommand:
    # the descriptive name of this command
    _name = 'base command'

    # these are the aliases for this command
    _bindings = ['b', 'base']

    def display_help(self, context):
        # show the help for the command
        print(' - bindings: {} \n   - description: {}'.format(self._bindings, self._name))

    def is_available(self, context):
        # is this command available?
        return True

    def is_called(self, context):
        command_name = context['command']
        return command_name in self._bindings

    def do_it(self, context):
        return

    def execute_command(self, context, command):
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


class GittyVersion(GittyCommand):
    _name = 'show current gitty version'
    _bindings = ['v', 'version']

    def display_help(self, context):
        # show the help for the command
        print(' - bindings: {} \n   - description: {} ({})'.format(self._bindings, self._name, context['gitty_version']))

    def is_available(self, context):
        # is this command available?
        return True

    def do_it(self, context):
        print('current gitty version: {}'.format(context['gitty_version']))


class GittyShowContext(GittyCommand):
    _name = "show current context"
    _bindings = ['show']

    def is_available(self, context):
        return True

    def do_it(self, context):
        def without_keys(con):
            return {x: con[x] for x in con if x not in {'commands'}}
        print('-- current context --')
        print(json.dumps(without_keys(context), indent=2))
        print('---------------------')


class GittyClean(GittyCommand):
    _name = "cleanup repository"
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

