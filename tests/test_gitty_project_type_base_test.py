import os
import tempfile
from shutil import copyfile
from unittest.case import TestCase

from gitty import GittyCommand


class ProjectTypeTestCase(TestCase):

    def __init__(self, test_method_name):
        super().__init__(test_method_name)
        self.sample_dir = None

    def go_to_sample_dir(self, sample_dir=None):
        # where are we?
        cwd = os.path.dirname(__file__)

        # from here, this is where the sample files are...
        if sample_dir is None:
            os.chdir('/'.join([cwd, self.sample_dir]))
        else:
            os.chdir('/'.join([cwd, sample_dir]))

        return cwd

    def go_to_temp_dir(self):
        cwd = os.path.dirname(__file__)
        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)
        return cwd

    def check_project_type_version_info(self, expected, project, current_branch, tags=[]):
        class TestGitApi:

            def get_tags_on_commit(self, context):
                return tags

            def git_hash(self, context, quiet):
                return 'git_hash_here'

            def git_remote(self, context, quiet):
                return 'git_remote_here'

        context = {
            'git_api': TestGitApi()
        }
        self.assertTrue(project.is_in_use(context), 'expected to be using project type {}'.format(project.get_name()))

        GittyCommand.add_branch_info_to_context(context, current_branch)

        # add the project branch info
        project.get_version_info(context)

        # verify that the actual results match what we expected - less the git api we added
        del context['git_api']
        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

    def copy_sample_to_temp_dir(self, project_file):
        temp_dir = tempfile.mkdtemp()
        destination = '/'.join([temp_dir, project_file])
        copyfile(project_file, destination)
        os.chdir(temp_dir)
        return destination
