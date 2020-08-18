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
        if context['project_type_name'] == 'unknown':
            return False
        if context['current_branch'] is None:
            return False
        return not context['on_a_task']

    def do_it(self, context):
        if len(context['branch_parts']) > 1:
            if context['hotfix']:
                steps = self._steps_from_release
            else:
                steps = self._steps_from_release + self._steps_from_point
        else:
            steps = self._steps_from_master

        for step in steps:
            step.execute(context)

    def get_description(self, context):
        if len(context['branch_parts']) > 1:
            if context['hotfix']:
                steps = self._steps_from_release
            else:
                steps = self._steps_from_release + self._steps_from_point
        else:
            steps = self._steps_from_master

        description = []
        for step in steps:
            description += step.describe(context)

        return description

    def stabilize_from_point(self, context):
        # do these for a hotfix or any other stabilization ecosystem
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
            # these are skipped for a hotfix
            self.execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
            self.bump_version_to(context, context['next_stable_version'])
            self.execute_command(context, 'git add {}'.format(context['project_file']).split())
            self.execute_command(context, [
                'git',
                'commit',
                '-m',
                '"bumped version to {}"'.format(context['next_stable_version'])
            ])