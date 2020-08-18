from gitty import GittyCommand, CommentStep, GitCommandStep, BumpVersionStep, GitCommandBump


class GittyRelease(GittyCommand):
    _title = 'release'
    _name = 'snap a new release from here'
    _bindings = ['r', 'release']
    _steps_from_point = [

        CommentStep('{} - {}'.format(_name, 'this is already in a stabilization ecosystem'), []),

        GitCommandStep('git checkout %s', ['current_release_branch']),
        GitCommandStep('git merge %s', ['current_branch']),

        BumpVersionStep('release_version'),
        GitCommandStep('git add %s', ['project_file']),
        GitCommandBump('release_version'),
        GitCommandStep('git tag %s', ['release_version']),
        GitCommandStep('git checkout %s', ['current_branch']),
        GitCommandStep('git merge %s', ['current_release_branch']),

        BumpVersionStep('next_stable_version'),
        GitCommandStep('git add %s', ['project_file']),
        GitCommandBump('next_stable_version'),

    ]

    _steps_from_master = [

        CommentStep('{} - {}'.format(_name, 'this will create a new stabilization ecosystem'), []),

        GitCommandStep('git checkout -b %s', ['new_stabilization_branch']),
        GitCommandStep('git checkout -b %s', ['new_release_branch']),

        BumpVersionStep('release_version'),
        GitCommandStep('git add %s', ['project_file']),
        GitCommandBump('release_version'),
        GitCommandStep('git tag %s', ['release_version']),

        GitCommandStep('git checkout %s', ['new_stabilization_branch']),
        GitCommandStep('$ git merge --strategy=ours %s', ['new_release_branch']),
        BumpVersionStep('next_stable_version'),
        GitCommandStep('git add %s', ['project_file']),
        GitCommandBump('next_stable_version'),

        GitCommandStep('git checkout %s', ['parent_version_branch']),
        GitCommandStep('$ git merge --strategy=ours %s', ['new_stabilization_branch']),
        BumpVersionStep('next_master_version'),
        GitCommandStep('git add %s', ['project_file']),
        GitCommandBump('next_master_version'),

    ]

    def is_available(self, context):
        if context['project_type_name'] == 'unknown':
            return False
        if context['current_branch'] is None:
            return False
        return not context['on_a_task']

    def get_description(self, context):

        if len(context['branch_parts']) > 1:
            steps = self._steps_from_point
        else:
            steps = self._steps_from_master

        description = []
        for step in steps:
            description += step.describe(context)

        return description

    def do_it(self, context):

        if len(context['branch_parts']) > 1:
            steps = self._steps_from_point
        else:
            steps = self._steps_from_master

        for step in steps:
            step.execute(context)
