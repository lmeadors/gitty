class GitAPI:

    def __init__(self, command_executor):
        self.command_executor = command_executor

    def executor(self, executor):
        if executor is None:
            return self.command_executor
        return executor

    def get_current_branch(self, context, quiet=False, executor=None):
        # this can throw an error - the caller is expected to deal with that appropriately
        current_branch = self.executor(executor).execute_immutable_command(
            context,
            'git rev-parse --abbrev-ref HEAD'.split(),
            quiet,
            raise_error=True
        )
        return current_branch

    def git_remote(self, context, quiet=False):
        return self.command_executor.execute_immutable_command(
            context,
            'git remote'.split(),
            quiet=quiet
        )

    def git_hash(self, context, quiet=False):
        return self.command_executor.execute_immutable_command(
            context,
            'git rev-parse --verify {}'.format(context['git_ref']).split(),
            quiet=quiet
        )

    def get_tags_on_commit(self, context, quiet=True):
        tags = self.command_executor.execute_immutable_command(
            context,
            'git tag --points-at HEAD'.split(),
            quiet
        )
        return tags.split()

    def commit(self, context, message, executor=None):
        command_parts = [
            'git',
            'commit',
            '-m',
            message
        ]
        return self.executor(executor).execute_command(context, command_parts, True)

    def status_is_clean(self, context, quiet=False):
        # print('git api - quiet:', quiet)
        status = self.command_executor.execute_immutable_command(context, 'git status -s'.split(), quiet)
        return status

    def get_merged_branch_names(self, context):
        merged_branches = self.command_executor.execute_immutable_command(
            context,
            'git branch --no-color --merged'.split(),
            True
        )
        return merged_branches.split()

    def get_unmerged_branch_names(self, context):
        unmerged_branches = self.command_executor.execute_immutable_command(
            context,
            'git branch -a --no-color --no-merged'.split(),
            True
        ).split()
        return unmerged_branches

    def remove_branch(self, context, branch_name):
        return self.command_executor.execute_command(
            context,
            'git branch -d {}'.format(branch_name).split(),
            True
        )

    def checkout_existing(self, context, branch_name, quiet, executor):
        return self.executor(executor).execute_command(context, 'git checkout {}'.format(branch_name).split(), quiet)

    def checkout_new(self, context, branch_name, quiet, executor):
        return self.executor(executor).execute_command(context, 'git checkout -b {}'.format(branch_name).split(), quiet)

    def merge(self, context, branch_to_merge):
        return self.command_executor.execute_command(
            context,
            'git merge {}'.format(branch_to_merge).split(),
            True
        )

    def merge_ours(self, context, branch_to_merge):
        return self.command_executor.execute_command(
            context,
            'git merge --strategy=ours {}'.format(branch_to_merge).split(),
            True
        )

    def tag(self, context, tag, quiet):
        return self.command_executor.execute_command(context, 'git tag {}'.format(tag).split(), quiet)

    def add(self, context, file_to_add, quiet):
        return self.command_executor.execute_command(context, 'git add {}'.format(file_to_add).split(), quiet)

    def fetch_and_prune(self, context, quiet):
        return self.command_executor.execute_command(context, 'git fetch --all --prune'.split(), quiet)

    def pull_and_rebase(self, context, quiet):
        return self.command_executor.execute_command(context, 'git pull --rebase'.split(), quiet)
