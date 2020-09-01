class GitAPI:

    def __init__(self, command_executor):
        self.command_executor = command_executor

    def executor(self, executor):
        if executor is None:
            return self.command_executor
        return executor

    def get_current_branch(self, context, executor=None):
        # this can throw an error - the caller is expected to deal with that appropriately
        current_branch = self.executor(executor).execute_immutable_command(
            context,
            'git rev-parse --abbrev-ref HEAD'.split(),
            raise_error=True
        )
        return current_branch

    def get_tags_on_commit(self, context):
        tags = self.command_executor.execute_immutable_command(
            context,
            'git tag --points-at HEAD'.split()
        )
        return tags.split()

    def commit(self, context, message, executor=None):
        command_parts = [
            'git',
            'commit',
            '-m',
            message
        ]
        return self.executor(executor).execute_command(context, command_parts)

    def status_is_clean(self, context):
        status = self.command_executor.execute_immutable_command(context, 'git status -s'.split())
        return status == ''

    def get_merged_branch_names(self, context):
        merged_branches = self.command_executor.execute_immutable_command(
            context,
            'git branch --no-color --merged'.split()
        )
        return merged_branches.split()

    def get_unmerged_branch_names(self, context):
        unmerged_branches = self.command_executor.execute_immutable_command(
            context,
            'git branch --no-color --no-merged'.split()
        )
        return unmerged_branches

    def remove_branch(self, context, branch_name):
        return self.command_executor.execute_command(context, 'git branch -d {}'.format(branch_name).split())

    def checkout_existing(self, context, branch_name, executor=None):
        return self.executor(executor).execute_command(context, 'git checkout {}'.format(branch_name).split())

    def checkout_new(self, context, branch_name, executor=None):
        return self.executor(executor).execute_command(context, 'git checkout -b {}'.format(branch_name).split())

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


