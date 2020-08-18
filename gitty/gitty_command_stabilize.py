from gitty import GittyCommand


class GittyStabilize(GittyCommand):
    _title = 'stabilize'
    _name = 'create stabilization ecosystem'
    _bindings = ['s', 'stabilize']

    def is_available(self, context):
        if context['project_type_name'] == 'unknown':
            return False
        if context['current_branch'] is None:
            return False
        return not context['on_a_task']

    def do_it(self, context):
        if len(context['branch_parts']) > 1:
            self.stabilize_from_point(context)
        else:
            self.stabilize_from_master(context)
        return

    def get_description(self, context):
        # stab from master
        return [
            '$ git checkout -b {}'.format(context['new_stabilization_branch']),
            '$ git checkout -b {}'.format(context['new_release_branch']),
            '$ git checkout master',
            '  (bump version to {})'.format(context['next_master_version']),
            '$ git add {}'.format(context['project_file']),
            '$ git commit -m "bumped version to {}"'.format(context['next_master_version'])
        ]

    def stabilize_from_master(self, context):
        self.execute_command(context, 'git checkout -b {}'.format(context['new_stabilization_branch']).split())
        self.execute_command(context, 'git checkout -b {}'.format(context['new_release_branch']).split())
        self.execute_command(context, 'git checkout master'.split())
        self.bump_version_to(context, context['next_master_version'])
        self.execute_command(context, 'git add {}'.format(context['project_file']).split())
        self.execute_command(context, [
            'git',
            'commit',
            '-m',
            '"bumped version to {}"'.format(context['next_master_version'])
        ])
        return

    def stabilize_from_point(self, context):
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
            self.execute_command(context, 'git checkout {}'.format(context['current_branch']).split())
            self.bump_version_to(context, context['next_stable_version'])
            self.execute_command(context, 'git add {}'.format(context['project_file']).split())
            self.execute_command(context, [
                'git',
                'commit',
                '-m',
                '"bumped version to {}"'.format(context['next_stable_version'])
            ])