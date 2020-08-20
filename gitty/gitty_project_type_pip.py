from distutils.core import run_setup
from os import path

from gitty import GittyProjectType


class GittyPip(GittyProjectType):

    def get_name(self):
        return 'pip'

    def get_version_info(self, context):
        context['project_file'] = 'setup.py'
        setup = run_setup(context['project_file'], stop_after='config')

        current_version = setup.metadata.version

        context['hotfix'] = False
        context['current_version'] = current_version
        context['release_version'] = current_version

        current_version_split = current_version.split(".")
        stable_branch_version = '.'.join(
            current_version_split[:-1]
        )
        context['new_stabilization_branch'] = stable_branch_version + '/master'
        context['new_release_branch'] = stable_branch_version + '/releases'

        next_master_version = '.'.join([
            current_version_split[0],
            str(int(current_version_split[1]) + 1),
            current_version_split[2]
        ])
        context['next_master_version'] = next_master_version

        next_stable_version = '.'.join([
            current_version_split[0],
            current_version_split[1],
            str(int(current_version_split[2]) + 1)
        ])
        context['next_stable_version'] = next_stable_version

        if len(context['branch_parts']) > 1:
            context['current_release_branch'] = stable_branch_version + '/releases'
        else:
            context['current_release_branch'] = 'n/a'

        context['new_stabilization_version'] = 'unknown'

    def is_in_use(self, context):
        return path.exists('setup.py')

    def bump_version_to(self, context, new_version):
        # we need to read in the setup.py file and replace the
        print('set version to {} in {}'.format(new_version, context['project_file']))

        if not context['dry_run']:

            with open(context['project_file'], 'r') as setup_file:
                lines = setup_file.readlines()

            new_lines = []
            for line in lines:
                if line.strip().startswith('version='):
                    new_lines.append('    version="{}",'.format(new_version))
                else:
                    new_lines.append(line.rstrip())

            with open(context['project_file'], 'w') as setup_file:
                for line in new_lines:
                    setup_file.write(line + "\n")