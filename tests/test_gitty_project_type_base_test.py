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
        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)
        cwd = os.getcwd()

    def check_project_type_version_info(self, expected, project, current_branch):
        context = {}
        self.assertTrue(project.is_in_use(context))
        # act as if this is on the master branch
        GittyCommand.add_branch_info_to_context(context, current_branch)
        # add the project branch info
        project.get_version_info(context)
        # verify that the actual results match what we expected
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
