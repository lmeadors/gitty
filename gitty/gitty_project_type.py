from xml.etree import ElementTree
# noinspection PyUnresolvedReferences
# this is so distutils doesn't complain about being imported before setuptools...apparently that's frowned upon.
import setuptools


class GittyProjectType:

    def get_name(self):
        return 'None'

    def get_version_info(self, context):
        print('put version info into context')

    def is_in_use(self, context):
        print('does this project type fit the current directory?')

    def bump_version_to(self, context, new_version):
        print('bump version in project file to {}'.format(new_version))


class GittyUnknownProjectType(GittyProjectType):

    def get_name(self):
        return 'unknown'

    def is_in_use(self, context):
        context['project_type_name'] = self.get_name()
        context['project_file'] = None
        return True

    def get_version_info(self, context):
        from gitty import Color
        print(Color.red_lt('unable to get version info for unknown project type'))
        for key in [
            'current_release_branch',
            'current_version',
            'hotfix',
            'new_release_branch',
            'new_stabilization_branch',
            'new_stabilization_version',
            'next_master_version',
            'next_stable_version',
            'release_version',
        ]:
            context[key] = None

    def bump_version_to(self, context, new_version):
        from gitty import Color
        print(Color.red_lt('unable to set version for unknown project type'))


