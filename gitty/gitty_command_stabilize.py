from gitty import GittyCommand, GitCommandStep, BumpVersionStep, GitCommandBump, CommentStep


class GittyStabilize(GittyCommand):
    _title = 'stabilize'
    _name = 'create stabilization ecosystem'
    _bindings = ['s', 'stabilize']

    # this is what we do for a hotfix
    _steps_from_release = [
        # self.execute_command(context, 'git checkout -b {}'.format(context['new_release_branch']).split())
        GitCommandStep('git checkout -b %s', ['new_release_branch']),
        # self.execute_command(context, 'git checkout -b {}'.format(context['new_stabilization_branch']).split())
        GitCommandStep('git checkout -b %s', ['new_stabilization_branch']),
        # self.bump_version_to(context, context['new_stabilization_version'])
        BumpVersionStep('new_stabilization_version'),
        # self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        GitCommandStep('git add %s', ['project_file']),
        # self.execute_command(context, [
        #     'git',
        #     'commit',
        #     '-m',
        #     '"bumped version to {}"'.format(context['new_stabilization_version'])
        # ])
        GitCommandBump('new_stabilization_version')
    ]

    # we do the steps above AND these for a normal stabilization ecosystem
    _steps_from_point = [
        GitCommandStep('git checkout %s', ['current_branch']),
        BumpVersionStep('next_stable_version'),
        GitCommandStep('git add %s', ['project_file']),
        GitCommandBump('next_stable_version'),
    ]

    _steps_from_master = [
        # '$ git checkout -b {}'.format(context['new_stabilization_branch']),
        GitCommandStep('git checkout -b %s', ['new_stabilization_branch']),

        # '$ git checkout -b {}'.format(context['new_release_branch']),
        GitCommandStep('git checkout -b %s', ['new_release_branch']),

        # '$ git checkout master',
        GitCommandStep('git checkout %s', ['current_branch']),

        # '  (bump version to {})'.format(context['next_master_version']),
        BumpVersionStep('next_master_version'),

        # '$ git add {}'.format(context['project_file']),
        GitCommandStep('git add %s', ['project_file']),

        # '$ git commit -m "bumped version to {}"'.format(context['next_master_version'])
        GitCommandBump('next_master_version'),
    ]

    def is_available(self, context):

        # we need a known project type
        if context['project_type_name'] == 'unknown':
            return False

        # we need to be in a git repo
        if context['current_branch'] is None:
            return False

        # don't create a stabilization ecosystem from a task
        return not context['a_task']

    def do_it(self, context):
        if len(context['branch_parts']) > 1:
            if context['hotfix']:
                GittyCommand.execute_steps(self._steps_from_release, context)
            else:
                GittyCommand.execute_steps(self._steps_from_release + self._steps_from_point, context)
        else:
            GittyCommand.execute_steps(self._steps_from_master, context)

    def get_description(self, context):
        if len(context['branch_parts']) > 1:
            if context['hotfix']:
                return GittyCommand.describe_steps(self._steps_from_release, context)
            else:
                return GittyCommand.describe_steps(self._steps_from_release + self._steps_from_point, context)
        else:
            return GittyCommand.describe_steps(self._steps_from_master, context)
