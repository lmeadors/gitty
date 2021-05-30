import os

from gitty import GittyCommand
from gitty.gitty_project_type_node import GittyNode
from tests.test_gitty_project_type_base_test import ProjectTypeTestCase


class TestGittyNode(ProjectTypeTestCase):

    def __init__(self, test_method_name):
        super().__init__(test_method_name)
        self.sample_dir = 'sample_files/node'

    def test_is_not_in_use(self):
        cwd = self.go_to_temp_dir()
        context = {}
        project = GittyNode()
        self.assertFalse(project.is_in_use(context))
        self.assertEqual('lol, nope', context.get('project_type_name', 'lol, nope'))
        os.chdir(cwd)

    def test_is_in_use_and_get_name(self):
        cwd = self.go_to_sample_dir()

        project = GittyNode()
        context = {}
        self.assertTrue(project.is_in_use(context))
        self.assertEqual(project.get_name(), context['project_type_name'])

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_the_master(self):
        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',
            'project_type_name': 'node',
            'project_file': 'package.json',

            'current_version': '1.2.4',
            'release_version': '1.2.4',
            'next_stable_version': '1.2.5',
            'next_master_version': '1.3.0',

            'branch_parts': ['master'],
            'current_branch': 'master',
            'current_release_branch': None,
            'task_prefix': 'tasks/',

            'new_release_branch': '1.2/releases',
            'new_stabilization_branch': '1.2/master',
            'new_stabilization_version': '1.2.4',

            'the_master': True,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'is_stable': False,
            'hotfix': False,
            'tags_on_commit': [],

        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyNode(), 'master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_master(self):

        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
            'tags_on_commit': [],
            'release_version': '1.2.4',
            'current_branch': '1.2/master',
            'branch_parts': ['1.2', 'master'],
            'current_release_branch': '1.2/releases',
            'task_prefix': '1.2/tasks/',
            'new_stabilization_version': '1.2.4.0',
            'new_stabilization_branch': '1.2.4/master',
            'new_release_branch': '1.2.4/releases',
            'next_master_version': '1.3.0',
            'next_stable_version': '1.2.5',
            'the_master': False,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'is_stable': True,
            'hotfix': False,
        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyNode(), '1.2/master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_master_task(self):

        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        expected = {
            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',
            'project_type_name': 'node',
            'project_file': 'package.json',
            'tags_on_commit': [],
            'current_version': '1.2.4',
            'current_branch': 'tasks/123_snapped_the_frame',
            'is_stable': False,
            'branch_parts': ['tasks', '123_snapped_the_frame'],
            'hotfix': False,
            'release_version': '1.2.4',
            'new_stabilization_branch': None,
            'new_release_branch': None,
            'new_stabilization_version': None,
            'next_stable_version': '1.2.5',
            'next_master_version': '1.3.0',
            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'task_prefix': None,
            'current_release_branch': None
        }

        self.check_project_type_version_info(expected, GittyNode(), 'tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_task(self):

        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        expected = {
            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',
            'current_branch': '1.2/tasks/123_snapped_the_frame',
            'is_stable': True,
            'branch_parts': ['1.2', 'tasks', '123_snapped_the_frame'],
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
            'tags_on_commit': [],
            'hotfix': False,
            'release_version': '1.2.4',
            'new_stabilization_branch': None,
            'new_release_branch': None,
            'new_stabilization_version': None,
            'next_stable_version': '1.2.5',
            'next_master_version': '1.3.0',
            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'task_prefix': None,
            'current_release_branch': '1.2/releases'
        }

        self.check_project_type_version_info(expected, GittyNode(), '1.2/tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_release_for_hotfix(self):

        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        tags = ['1.2.4']
        expected = {
            'git_ref': 'HEAD',
            'git_hash': 'git_hash_here',
            'git_remote': 'git_remote_here',
            'current_branch': '1.2/releases',
            'is_stable': True,
            'branch_parts': ['1.2', 'releases'],
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
            'tags_on_commit': tags,
            'hotfix': True,
            'release_version': '1.2.4',
            'new_stabilization_branch': '1.2.4/master',
            'new_release_branch': '1.2.4/releases',
            'new_stabilization_version': '1.2.4.0',
            'next_stable_version': '1.2.5',
            'next_master_version': '1.3.0',
            'the_master': False,
            'a_master': False,
            'a_task': False,
            'a_release': True,
            'task_prefix': None,
            'current_release_branch': '1.2/releases'
        }

        self.check_project_type_version_info(expected, GittyNode(), '1.2/releases', tags)

        # go back where we started
        os.chdir(cwd)

    def test_bump_version(self):

        # go to the sample directory
        cwd = self.go_to_sample_dir()

        # copy the pom to a temp location (and go there)
        destination = self.copy_sample_to_temp_dir('package.json')

        context = {
            'project_file': 'package.json',
            'dry_run': False,
            'branch_parts': ['master'],
            'a_task': False,
            'is_stable': False,
            'tags_on_commit': [],
        }
        new_version = '1.3.5'

        project = GittyNode()

        # pre-check the version
        project.get_version_info(context)
        self.assertEqual('1.2.4', context['current_version'])

        # update the version
        project.bump_version_to(context, new_version)

        # check the version after we bump it
        project.get_version_info(context)
        self.assertEqual(new_version, context['current_version'])

        # remove the copied project file
        os.remove(destination)

        # go back where we started
        os.chdir(cwd)

    def test_do_not_bump_version_if_dry_run(self):

        cwd = self.go_to_sample_dir()

        # copy the pom to a temp location first
        destination = self.copy_sample_to_temp_dir('package.json')

        context = {
            'project_file': 'package.json',
            'dry_run': True,
            'branch_parts': ['master'],
            'a_task': False,
            'is_stable': False,
            'tags_on_commit': [],
        }

        project = GittyNode()

        # pre-check the version
        project.get_version_info(context)
        self.assertEqual('1.2.4', context['current_version'])

        # set it...but not really - just a dry run...
        new_version = '1.3.5'
        project.bump_version_to(context, new_version)

        # verify it did not change
        project.get_version_info(context)
        self.assertEqual('1.2.4', context['current_version'])

        # clean up the mess
        os.remove(destination)

        # go back where we started
        os.chdir(cwd)
