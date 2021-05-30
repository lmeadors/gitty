import os

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
            'project_file': 'setup.py',

            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',

            'current_version': '1.2.0.dev0',
            'release_version': '1.2.0',
            'next_stable_version': '1.2.1.dev0',
            'next_master_version': '1.3.0.dev0',

            'branch_parts': ['master'],
            'current_branch': 'master',
            'current_release_branch': None,
            'task_prefix': 'tasks/',

            'new_release_branch': '1.2/releases',
            'new_stabilization_branch': '1.2/master',
            'new_stabilization_version': '1.2.0.dev0',

            'the_master': True,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'is_stable': False,
            'hotfix': False,
            'tags_on_commit': [],

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
            'project_file': 'setup.py',

            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',

            'current_version': '1.2.0.dev0',
            'release_version': '1.2.0',
            'next_stable_version': '1.2.1.dev0',
            'next_master_version': '1.3.0.dev0',

            'branch_parts': ['1.2', 'master'],
            'current_branch': '1.2/master',
            'current_release_branch': '1.2/releases',
            'task_prefix': '1.2/tasks/',

            'new_release_branch': '1.2.0/releases',
            'new_stabilization_version': '1.2.0.0.dev0',
            'new_stabilization_branch': '1.2.0/master',

            'the_master': False,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'is_stable': True,
            'hotfix': False,
            'tags_on_commit': [],

        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyPip(), '1.2/master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_master_task(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'project_file': 'setup.py',

            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',
            'current_version': '1.2.0.dev0',
            'release_version': '1.2.0',
            'next_stable_version': '1.2.1.dev0',
            'next_master_version': '1.3.0.dev0',

            'branch_parts': ['tasks', '123_snapped_the_frame'],
            'current_branch': 'tasks/123_snapped_the_frame',
            'current_release_branch': '1.2/releases',
            'task_prefix': None,

            'new_release_branch': '1.2/releases',
            'new_stabilization_version': None,
            'new_stabilization_branch': '1.2/master',

            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'is_stable': False,
            'hotfix': False,
            'tags_on_commit': [],

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

            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',

            'current_version': '1.2.0.dev0',
            'release_version': '1.2.0',
            'next_stable_version': '1.2.1.dev0',
            'next_master_version': '1.3.0.dev0',

            'branch_parts': ['1.2', 'tasks', '123_snapped_the_frame'],
            'current_branch': '1.2/tasks/123_snapped_the_frame',
            'current_release_branch': '1.2/releases',
            'task_prefix': None,

            'new_release_branch': '1.2.0/releases',
            'new_stabilization_version': '1.2.0.0.dev0',
            'new_stabilization_branch': '1.2.0/master',

            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'is_stable': True,
            'hotfix': False,
            'tags_on_commit': [],

        }

        self.check_project_type_version_info(expected, GittyPip(), '1.2/tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_release_for_hotfix(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        tags = ['1.2.0.dev0']
        expected = {
            'project_type_name': 'pip',
            'project_file': 'setup.py',

            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',

            'current_version': '1.2.0.dev0',
            'release_version': '1.2.0',
            'next_stable_version': '1.2.1.dev0',
            'next_master_version': '1.3.0.dev0',

            'branch_parts': ['1.2', 'releases'],
            'current_branch': '1.2/releases',
            'current_release_branch': '1.2/releases',
            'task_prefix': None,

            'new_release_branch': '1.2.0/releases',
            'new_stabilization_version': '1.2.0.0.dev0',
            'new_stabilization_branch': '1.2.0/master',

            'the_master': False,
            'a_master': False,
            'a_task': False,
            'a_release': True,
            'is_stable': True,
            'hotfix': True,
            'tags_on_commit': tags

        }

        self.check_project_type_version_info(expected, GittyPip(), '1.2/releases', tags)

        # go back where we started
        os.chdir(cwd)
