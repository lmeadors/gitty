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
        self.command_executor.execute_command(context, command_parts)
        return

    def status_is_clean(self):
        return

    def get_merged_branch_names(self):
        return []

    def remove_branch(self):
        return

    def fetch_and_prune(self):
        return

    def pull_and_rebase(self):
        return

    def checkout_existing(self):
        return

    def checkout_new(self):
        return

    def merge(self):
        return

    def merge_ours(self):
        return

    def tag(self):
        return

    def add(self):
        return

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
