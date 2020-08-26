import os

from gitty import GittyCommand
from gitty.gitty_project_type_node import GittyNode
from tests.test_gitty_project_type_base_test import ProjectTypeTestCase


class TestGittyNode(ProjectTypeTestCase):

    def __init__(self, test_method_name):
        super().__init__(test_method_name)
        self.sample_dir = 'sample_files/node'

    def test_is_not_in_use(self):
        self.go_to_temp_dir()
        context = {}
        pip = GittyNode()
        self.assertFalse(pip.is_in_use(context))
        self.assertEqual('lol, nope', context.get('project_type_name', 'lol, nope'))

    def test_is_in_use_and_get_name(self):
        cwd = self.go_to_sample_dir()
        pip = GittyNode()
        context = {}
        self.assertTrue(pip.is_in_use(context))
        self.assertEqual(pip.get_name(), context['project_type_name'])

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_the_master(self):
        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'node',
            'current_release_branch': None,
            'new_stabilization_version': '1.2.4',
            'current_branch': 'master',
            'the_master': True,
            'branch_parts': ['master'],
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'task_prefix': 'tasks/',
            'is_stable': False,
            'project_file': 'package.json',
            'hotfix': True,
            'current_version': '1.2.4',
            'release_version': '1.2.4',
            'new_stabilization_branch': '1.2/master',
            'new_release_branch': '1.2/releases',
            'next_master_version': '1.3.0',
            'next_stable_version': '1.2.5'
        }

        context = {}
        pip = GittyNode()
        pip.is_in_use(context)
        GittyCommand.add_branch_info_to_context(context, 'master')
        pip.get_version_info(context)
        # print(context)
        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_master(self):

        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
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
            'hotfix': True,
        }

        context = {}
        pip = GittyNode()
        pip.is_in_use(context)
        GittyCommand.add_branch_info_to_context(context, '1.2/master')
        pip.get_version_info(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_master_task(self):

        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
            'current_branch': 'tasks/123_snapped_the_frame',
            'is_stable': False,
            'branch_parts': ['tasks', '123_snapped_the_frame'],
            'hotfix': True,
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
            'current_branch': '1.2/tasks/123_snapped_the_frame',
            'is_stable': True,
            'branch_parts': ['1.2', 'tasks', '123_snapped_the_frame'],
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
            'hotfix': True,
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

        expected = {
            'current_branch': '1.2/releases',
            'is_stable': True,
            'branch_parts': ['1.2', 'releases'],
            'project_type_name': 'node',
            'project_file': 'package.json',
            'current_version': '1.2.4',
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

        self.check_project_type_version_info(expected, GittyNode(), '1.2/releases')

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
