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
        return True

    def get_version_info(self, context):
        print('unable to get version info for unknown project type')
        context['project_file'] = None
        context['current_version'] = 'unknown'

    def bump_version_to(self, context, new_version):
        print('unable to set version for unknown project type')


