import os
import tempfile
from unittest import TestCase

from gitty import GittyCommand
from gitty.gitty_project_type_pip import GittyPip
from tests.test_gitty_project_type_base_test import ProjectTypeTestCase


class TestGittyPip(ProjectTypeTestCase):

    def __init__(self, test_method_name):
        super().__init__(test_method_name)
        self.sample_dir = 'sample_files/pip'

    def test_is_not_in_use(self):
        cwd = self.go_to_temp_dir()
        context = {}
        project = GittyPip()
        self.assertFalse(project.is_in_use(context))
        self.assertEqual('lol, nope', context.get('project_type_name', 'lol, nope'))
        os.chdir(cwd)

    def test_is_in_use_and_get_name(self):
        cwd = self.go_to_sample_dir()
        project = GittyPip()
        context = {}
        self.assertTrue(project.is_in_use(context))
        self.assertEqual(project.get_name(), context['project_type_name'])

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_the_master(self):
        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'current_release_branch': None,
            'new_stabilization_version': None,
            'current_branch': 'master',
            'the_master': True,
            'branch_parts': ['master'],
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'task_prefix': 'tasks/',
            'is_stable': False,
            'project_file': 'setup.py',
            'hotfix': False,
            'current_version': '1.1.2',
            'release_version': '1.1.2',
            'new_stabilization_branch': '1.1/master',
            'new_release_branch': '1.1/releases',
            'next_master_version': '1.2.0',
            'next_stable_version': '1.1.3',
            'tags_on_commit': []
        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyPip(), 'master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_on_stable(self):
        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'current_release_branch': '1.1/releases',
            'new_stabilization_version': '1.1.2.0',
            'current_branch': '1.1/master',
            'the_master': False,
            'branch_parts': ['1.1', 'master'],
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'task_prefix': '1.1/tasks/',
            'is_stable': True,
            'project_file': 'setup.py',
            'hotfix': False,
            'current_version': '1.1.2',
            'release_version': '1.1.2',
            'new_stabilization_branch': '1.1.2/master',
            'new_release_branch': '1.1.2/releases',
            'next_master_version': '1.2.0',
            'next_stable_version': '1.1.3',
            'tags_on_commit': []
        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyPip(), '1.1/master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_master_task(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'project_file': 'setup.py',
            'current_branch': 'tasks/123_snapped_the_frame',
            'is_stable': False,
            'branch_parts': ['tasks', '123_snapped_the_frame'],
            'current_version': '1.1.2',
            'hotfix': False,
            'release_version': '1.1.2',
            'new_stabilization_branch': '1.1/master',
            'new_release_branch': '1.1/releases',
            'new_stabilization_version': None,
            'next_stable_version': '1.1.3',
            'next_master_version': '1.2.0',
            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'task_prefix': None,
            'current_release_branch': '1.1/releases',
            'tags_on_commit': []
        }

        self.check_project_type_version_info(expected, GittyPip(), 'tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_task(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'project_file': 'setup.py',
            'current_branch': '1.2/tasks/123_snapped_the_frame',
            'is_stable': True,
            'branch_parts': ['1.2', 'tasks', '123_snapped_the_frame'],
            'current_version': '1.1.2',
            'hotfix': False,
            'release_version': '1.1.2',
            'new_stabilization_branch': '1.1.2/master',
            'new_release_branch': '1.1.2/releases',
            'new_stabilization_version': '1.1.2.0',
            'next_stable_version': '1.1.3',
            'next_master_version': '1.2.0',
            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'task_prefix': None,
            'current_release_branch': '1.1/releases',
            'tags_on_commit': []
        }

        self.check_project_type_version_info(expected, GittyPip(), '1.2/tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_release_for_hotfix(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        tags = ['1.1.2']
        expected = {
            'current_branch': '1.1/releases',
            'is_stable': True,
            'branch_parts': ['1.1', 'releases'],
            'project_type_name': 'pip',
            'project_file': 'setup.py',
            'current_version': '1.1.2',
            'hotfix': True,
            'release_version': '1.1.2',
            'new_stabilization_branch': '1.1.2/master',
            'new_release_branch': '1.1.2/releases',
            'new_stabilization_version': '1.1.2.0',
            'next_stable_version': '1.1.3',
            'next_master_version': '1.2.0',
            'the_master': False,
            'a_master': False,
            'a_task': False,
            'a_release': True,
            'task_prefix': None,
            'current_release_branch': '1.1/releases',
            'tags_on_commit': tags
        }

        self.check_project_type_version_info(expected, GittyPip(), '1.1/releases', tags)

        # go back where we started
        os.chdir(cwd)
