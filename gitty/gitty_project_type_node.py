import json
from os import path

from gitty import GittyProjectType


class GittyNode(GittyProjectType):

    def get_name(self):
        return 'node'

    def is_in_use(self, context):
        is_node = path.exists('package.json')
        if is_node:
            context['project_type_name'] = self.get_name()
            context['project_file'] = 'package.json'
        return is_node

    def get_version_info(self, context):
        # node project file...



        with open(context['project_file']) as package_json:
            data = json.load(package_json)
            current_version = data['version']
            context['hotfix'] = current_version in context['tags_on_commit']
            context['current_version'] = current_version
            context['release_version'] = current_version
            release_version_split = context['release_version'].split(".")

            if context['is_stable']:
                context['current_release_branch'] = '.'.join(release_version_split[:-1]) + '/releases'
                if context['a_task']:
                    context['new_release_branch'] = None
                    context['new_stabilization_branch'] = None
                    context['new_stabilization_version'] = None
                else:
                    context['new_release_branch'] = '.'.join(release_version_split) + '/releases'
                    context['new_stabilization_branch'] = '.'.join(release_version_split) + '/master'
                    context['new_stabilization_version'] = '.'.join(release_version_split) + '.0'
            else:
                context['current_release_branch'] = None
                if context['a_task']:
                    context['new_release_branch'] = None
                    context['new_stabilization_branch'] = None
                    context['new_stabilization_version'] = None
                else:
                    context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/releases'
                    context['new_stabilization_branch'] = '.'.join(release_version_split[:-1]) + '/master'
                    context['new_stabilization_version'] = '.'.join(release_version_split)

            # increment the patch
            next_min = str(int(release_version_split[1]) + 1)
            context['next_master_version'] = '.'.join([
                release_version_split[0],
                next_min,
                '0'
            ])
            # we want to increment the last number, regardless of how many there are...
            next_stable_version = release_version_split.copy()
            next_stable_version[-1] = str(int(next_stable_version[-1]) + 1)
            context['next_stable_version'] = '.'.join(next_stable_version)

    def bump_version_to(self, context, new_version):
        print('bump version to {}'.format(new_version))

        if not context['dry_run']:
            with open('package.json') as package_json:
                data = json.load(package_json)
                data['version'] = new_version
            with open('package.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)