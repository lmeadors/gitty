from gitty import GittyCommand


class GittyRelease(GittyCommand):
    _title = 'release'
    _name = 'snap a new release from here'
    _bindings = ['r', 'release']

    def is_available(self, context):
        if context['project_type_name'] == 'unknown':
            return False
        if context['current_branch'] is None:
            return False
        return not context['on_a_task']

    def get_description(self, context):
        point_release = len(context['branch_parts']) > 1

        steps = []

        if point_release:
            # this is a point release
            steps += [
                '{} - {}'.format(self._name, 'this is already in a stabilization ecosystem'),
                '$ git checkout {}'.format(context['current_release_branch']),
                '$ git merge {}'.format(context['current_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['release_version'], context['project_file'], context['current_release_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['release_version']),
                '$ git tag {}'.format(context['release_version']),
                '$ git checkout {}'.format(context['current_branch']),
                '$ git merge {}'.format(context['current_release_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['next_stable_version'], context['project_file'], context['current_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['next_stable_version']),
            ]
        else:
            # this is a new release from master - there are extra steps here
            steps += [
                '{} - {}'.format(self._name, 'this will create a new stabilization ecosystem'),
                '$ git checkout -b ' + context['new_stabilization_branch'],
                '$ git checkout -b ' + context['new_release_branch'],
                '  (bump version to {} in {} on {} branch)'.format(
                    context['release_version'], context['project_file'], context['new_release_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['release_version']),
                '$ git tag {}'.format(context['release_version']),
                '$ git checkout {}'.format(context['new_stabilization_branch']),
                # this is a transient branch/merge, so we won't actually merge, we'll just mark it as merged
                '$ git merge --strategy=ours {}'.format(context['new_release_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['next_stable_version'], context['project_file'], context['new_stabilization_branch']
                ),
                '$ git add {}'.format(context['project_file']),
                '$ git commit -m "bumped version to {}"'.format(context['next_stable_version']),
                '$ git checkout master',
                '$ git merge --strategy=ours {}'.format(context['new_stabilization_branch']),
                '  (bump version to {} in {} on {} branch)'.format(
                    context['next_master_version'], context['project_file'], 'master'
                ),
                '$ git add {}'.format(context['project_file']),
                # this has spaces in a parameter, so it's different...
                '$ git commit -m "bumped version to {}"'.format(context['next_master_version'])
            ]

        return steps

    def do_it(self, context):
        if len(context['branch_parts']) > 1:
            self.release_from_point(context)
        else:
            self.release_from_master(context)

    def release_from_master(self, context):
        self.execute_command(context, ('git checkout -b ' + context['new_stabilization_branch']).split())
        self.execute_command(context, ('git checkout -b ' + context['new_release_branch']).split())
        self.bump_version_to(context, context['release_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['release_version'] + '"'
        ])
        self.execute_command(context, 'git tag {}'.format(context['release_version']).split())
        self.execute_command(context, 'git checkout {}'.format(context['new_stabilization_branch']).split())
        # this is a transient branch/merge, so we won't actually merge, we'll just mark it as merged
        self.execute_command(context, 'git merge --strategy=ours {}'.format(context['new_release_branch']).split())
        self.bump_version_to(context, context['next_stable_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['next_stable_version'] + '"'
        ])
        self.execute_command(context, 'git checkout master'.split())
        self.execute_command(context, 'git merge --strategy=ours {}'.format(context['new_stabilization_branch']).split())
        self.bump_version_to(context, context['next_master_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['next_master_version'] + '"'
        ])

    def release_from_point(self, context):
        self.execute_command(context, 'git checkout {}'.format(context['current_release_branch']).split())
        self.execute_command(context, 'git merge {}'.format(context['current_branch']).split())
        self.bump_version_to(context, context['release_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['release_version'] + '"'
        ])
        self.execute_command(context, 'git tag {}'.format(context['release_version']).split())
        self.execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
        self.execute_command(context, 'git merge {}'.format(context['current_release_branch']).split())
        self.bump_version_to(context, context['next_stable_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        # this has spaces in a parameter, so it's different...
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to ' + context['next_stable_version'] + '"'
        ])