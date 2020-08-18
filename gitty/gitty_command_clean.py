from gitty import GittyCommand


class GittyClean(GittyCommand):
    _title = 'cleanup'
    _name = 'freshen up around the place - pull changes (with rebase) and cleanup unused branches'
    _bindings = ['c', 'clean']

    def is_available(self, context):
        return context['current_branch'] is not None

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