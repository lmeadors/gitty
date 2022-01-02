from os import path
import plistlib
from gitty import GittyProjectType


class GittyXCode(GittyProjectType):

    def get_name(self):
        return 'xcode'

    def is_in_use(self, context):
        is_xcode = path.exists('gitty-test/Info.plist')
        if is_xcode:
            context['project_type_name'] = self.get_name()
            context['project_file'] = 'gitty-test/Info.plist'
        return is_xcode

    def get_version_info(self, context):
        with open(context['project_file'], 'rb') as f:
            plist_data = plistlib.load(f)
            major_minor = plist_data['CFBundleShortVersionString']
            patch = plist_data['CFBundleVersion']

        patch_split = patch.split('.')
        hotfix = len(patch_split) <= 1
        context['hotfix'] = hotfix

        major = int(major_minor.split('.')[0])
        minor = int(major_minor.split('.')[1])
        context['current_version'] = '.'.join([
            major_minor,
            patch
        ])
        context['release_version'] = '.'.join([
            major_minor,
            patch_split[0]
        ])

        context['new_release_branch'] = '/'.join([
            major_minor,
            context['release_prefix']
        ])
        context['new_stabilization_branch'] = '/'.join([
            major_minor,
            context['trunk']
        ])

        context['next_master_version'] = '.'.join([
            str(major),
            str(int(minor + 1)),
            '0',
            'dev'
        ])

        context['next_stable_version'] = '.'.join([
            str(major),
            str(int(minor)),
            str(int(patch_split[0]) + 1),
            'dev'
        ])

        # todo - this is sketchy at best...
        context['new_stabilization_version'] = context['next_stable_version']
        context['current_release_branch'] = context['new_release_branch']

    def bump_version_to(self, context, new_version):
        # print('todo: set version to {} in {}'.format(new_version, context['project_file']))

        hotfix = context['hotfix']
        new_version_split = new_version.split('.')
        short_version_string = '.'.join(new_version_split[0:2])
        bundle_version = '.'.join(new_version_split[2:])
        # print(
        #     'set version to {} / {} in {}'.format(
        #         short_version_string, bundle_version, context['project_file']))
        with open(context['project_file'], 'rb') as f:
            plist_data = plistlib.load(f)
            plist_data['CFBundleShortVersionString'] = short_version_string
            plist_data['CFBundleVersion'] = bundle_version

        if not context['dry_run']:
            with open(context['project_file'], 'wb') as output_file:
                plistlib.dump(plist_data, output_file)
