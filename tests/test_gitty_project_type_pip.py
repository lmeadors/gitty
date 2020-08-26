import os
import tempfile
from unittest import TestCase

from gitty import GittyCommand
from gitty.gitty_project_type_pip import GittyPip


class TestGittyPip(TestCase):

    def test_is_not_in_use(self):
        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)
        cwd = os.getcwd()
        # print('cwd: ' + cwd)
        context = {}
        pip = GittyPip()
        self.assertFalse(pip.is_in_use(context))
        os.chdir(cwd)
        self.assertEqual('lol, nope', context.get('project_type_name', 'lol, nope'))

    def test_is_in_use(self):
        cwd = self.go_to_sample_dir()
        pip = GittyPip()
        context = {}
        self.assertTrue(pip.is_in_use(context))
        self.assertEqual(pip.get_name(), context['project_type_name'])

        # go back where we started
        os.chdir(cwd)

    def go_to_sample_dir(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/sample_files/pip')
        return cwd

    def test_get_version_info_on_the_master(self):
        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'current_release_branch': None,
            'new_stabilization_version': 'unknown',
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
            'next_stable_version': '1.1.3'
        }

        context = {}
        pip = GittyPip()
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

    def test_get_version_info_on_stable(self):

        # go to the sample directory
        cwd = self.go_to_sample_dir()

        expected = {
            'project_type_name': 'pip',
            'current_release_branch': '1.1/releases',
            'new_stabilization_version': 'unknown',
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
            'new_stabilization_branch': '1.1/master',
            'new_release_branch': '1.1/releases',
            'next_master_version': '1.2.0',
            'next_stable_version': '1.1.3'
        }

        context = {}
        pip = GittyPip()
        pip.is_in_use(context)
        GittyCommand.add_branch_info_to_context(context, '1.1/master')
        pip.get_version_info(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)
