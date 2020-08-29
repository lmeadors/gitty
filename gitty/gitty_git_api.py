import subprocess

from gitty import Color


class GitAPI:

    def __init__(self, command_executor):
        self.command_executor = command_executor

    def get_current_branch(self, context):
        # this can throw an error - the caller is expected to deal with that appropriately
        current_branch = self.command_executor.execute_immutable_command(
            context,
            'git rev-parse --abbrev-ref HEAD'.split(),
            raise_error=True
        )
        return current_branch.decode().strip()

    def get_tags_on_commit(self, context):
        tags = self.command_executor.execute_immutable_command(
            context,
            'git tag --points-at HEAD'.split()
        )
        return tags.decode().split()

    def commit(self, context, message):
        command_parts = [
            'git',
            'commit',
            '-m',
            message
        ]
        return self.command_executor.execute_command(context, command_parts)

    def status_is_clean(self, context):
        status = self.command_executor.execute_immutable_command(context, 'git status -s'.split()).decode()
        return status == ''

    def get_merged_branch_names(self, context):
        merged_branches = self.command_executor.execute_immutable_command(
            context,
            'git branch --no-color --merged'.split()
        ).decode()
        return merged_branches

    def get_unmerged_branch_names(self, context):
        unmerged_branches = self.command_executor.execute_immutable_command(
            context,
            'git branch --no-color --no-merged'.split()
        ).decode()
        return unmerged_branches

    def remove_branch(self, context, branch_name):
        return self.command_executor.execute_command(context, 'git branch -d {}'.format(branch_name).split())

    def checkout_existing(self, context, branch_name):
        return self.command_executor.execute_command(context, 'git checkout {}'.format(branch_name).split())

    def checkout_new(self, context, branch_name):
        return self.command_executor.execute_command(context, 'git checkout -b {}'.format(branch_name).split())

    def merge(self, context, branch_to_merge):
        return self.command_executor.execute_command(
            context,
            'git merge {}'.format(branch_to_merge).split()
        )

    def merge_ours(self, context, branch_to_merge):
        return self.command_executor.execute_command(
            context,
            'git merge --strategy=ours {}'.format(branch_to_merge).split()
        )

    def tag(self, context, tag):
        return self.command_executor.execute_command(context, 'git tag {}'.format(tag).split())

    def add(self, context, file_to_add):
        return self.command_executor.execute_command(context, 'git add {}'.format(file_to_add).split())

    def fetch_and_prune(self, context):
        return self.command_executor.execute_command(context, 'git fetch --all --prune'.split())

    def pull_and_rebase(self, context):
        return self.command_executor.execute_command(context, 'git pull --rebase'.split())


class CommandExecutor:

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def execute_command(self, context, command_parts, raise_error=False):
        # show the command to be run
        print('$', ' '.join(command_parts))

        if not self.dry_run:
            try:
                return subprocess.check_output(command_parts)
            except subprocess.CalledProcessError as e:
                print(Color.red_lt(e.output.decode()))
                if raise_error:
                    raise e

    # noinspection PyMethodMayBeStatic
    def execute_immutable_command(self, context, command_parts, raise_error=False):
        # show the command to be run
        print('$', ' '.join(command_parts))

        try:
            return subprocess.check_output(command_parts)
        except subprocess.CalledProcessError as e:
            print(Color.red_lt(e.output.decode()))
            if raise_error:
                raise e
