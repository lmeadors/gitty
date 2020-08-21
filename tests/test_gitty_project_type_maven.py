import os
import tempfile
from shutil import copyfile
from unittest import TestCase

from gitty import GittyCommand
from gitty.gitty_project_type_maven import GittyMaven


class TestGittyMaven(TestCase):

    def test_is_not_in_use(self):
        gitty_maven = GittyMaven()
        cwd = os.getcwd()
        context = {}
        self.assertFalse(gitty_maven.is_in_use(context))
        os.chdir(cwd)
        self.assertEqual('lol, nope', context.get('project_type_name', 'lol, nope'))

    def test_is_in_use_and_get_name(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')
        maven = GittyMaven()
        context = {}
        self.assertTrue(maven.is_in_use(context))
        self.assertEqual(maven.get_name(), context['project_type_name'])

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_the_master(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')
        maven = GittyMaven()
        expected = {
            'current_branch': 'master',
            'is_stable': False,
            'branch_parts': ['master'],
            'project_file': 'pom.xml',
            'current_version': '1.0.0-SNAPSHOT',
            'hotfix': False,
            'release_version': '1.0.0',
            'new_stabilization_branch': '1.0/master',
            'new_release_branch': '1.0/releases',
            'new_stabilization_version': '1.0.0-SNAPSHOT',
            'next_stable_version': '1.0.1-SNAPSHOT',
            'next_master_version': '1.1.0-SNAPSHOT',
            'the_master': True,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'task_prefix': 'tasks/',
            'current_release_branch': None
        }

        # init the context
        context = {}
        # we'll act as if this is on the master branch
        GittyCommand.add_branch_info_to_context(context, 'master')
        # print(context)
        # add the project branch info
        maven.get_version_info(context)
        # print(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_master(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')
        maven = GittyMaven()
        expected = {
            'current_branch': '1.0/master',
            'is_stable': True,
            'branch_parts': ['1.0', 'master'],
            'project_file': 'pom.xml',
            'current_version': '1.0.0-SNAPSHOT',
            'hotfix': False,
            'release_version': '1.0.0',
            'new_stabilization_branch': '1.0.0/master',
            'new_release_branch': '1.0.0/releases',
            'new_stabilization_version': '1.0.0.0-SNAPSHOT',
            'next_stable_version': '1.0.1-SNAPSHOT',
            'next_master_version': '1.1.0-SNAPSHOT',
            'the_master': False,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'task_prefix': '1.0/tasks/',
            'current_release_branch': '1.0/releases'
        }

        # init the context
        context = {}
        # we'll act as if this is on the master branch
        GittyCommand.add_branch_info_to_context(context, '1.0/master')
        # print(context)
        # add the project branch info
        maven.get_version_info(context)
        # print(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_master_task(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')
        maven = GittyMaven()
        expected = {
            'current_branch': 'tasks/123_snapped_the_frame',
            'is_stable': False,
            'branch_parts': ['tasks', '123_snapped_the_frame'],
            'project_file': 'pom.xml',
            'current_version': '1.0.0-SNAPSHOT',
            'hotfix': False,
            'release_version': '1.0.0',
            'new_stabilization_branch': None,
            'new_release_branch': None,
            'new_stabilization_version': None,
            'next_stable_version': '1.0.1-SNAPSHOT',
            'next_master_version': '1.1.0-SNAPSHOT',
            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'task_prefix': None,
            'current_release_branch': None
        }

        # init the context
        context = {}
        # we'll act as if this is on the master branch
        GittyCommand.add_branch_info_to_context(context, 'tasks/123_snapped_the_frame')
        # print(context)
        # add the project branch info
        maven.get_version_info(context)
        # print(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_task(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')
        maven = GittyMaven()
        expected = {
            'current_branch': '1.0/tasks/123_snapped_the_frame',
            'is_stable': True,
            'branch_parts': ['1.0', 'tasks', '123_snapped_the_frame'],
            'project_file': 'pom.xml',
            'current_version': '1.0.0-SNAPSHOT',
            'hotfix': False,
            'release_version': '1.0.0',
            'new_stabilization_branch': None,
            'new_release_branch': None,
            'new_stabilization_version': None,
            'next_stable_version': '1.0.1-SNAPSHOT',
            'next_master_version': '1.1.0-SNAPSHOT',
            'the_master': False,
            'a_master': False,
            'a_task': True,
            'a_release': False,
            'task_prefix': None,
            'current_release_branch': '1.0/releases'
        }

        # init the context
        context = {}
        # we'll act as if this is on the master branch
        GittyCommand.add_branch_info_to_context(context, '1.0/tasks/123_snapped_the_frame')
        # print(context)
        # add the project branch info
        maven.get_version_info(context)
        # print(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_release_for_hotfix(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_release')
        maven = GittyMaven()
        expected = {
            'current_branch': '1.2/releases',
            'is_stable': True,
            'branch_parts': ['1.2', 'releases'],
            'project_file': 'pom.xml',
            'current_version': '1.2.3',
            'hotfix': True,
            'release_version': '1.2.3',
            'new_stabilization_branch': '1.2.3/master',
            'new_release_branch': '1.2.3/releases',
            'new_stabilization_version': '1.2.3.0-SNAPSHOT',
            'next_stable_version': '1.2.4-SNAPSHOT',
            'next_master_version': '1.3.0-SNAPSHOT',
            'the_master': False,
            'a_master': False,
            'a_task': False,
            'a_release': True,
            'task_prefix': None,
            'current_release_branch': '1.2/releases'
        }

        # init the context
        context = {}
        # we'll act as if this is on the master branch
        GittyCommand.add_branch_info_to_context(context, '1.2/releases')
        # print(context)
        # add the project branch info
        maven.get_version_info(context)
        # print(context)

        for key in context.keys():
            # print(key)
            self.assertEqual(expected[key], context[key], 'assertion on {} failed'.format(key))
        self.assertEqual(len(expected), len(context))

        # go back where we started
        os.chdir(cwd)

    def test_bump_version(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')

        # copy the pom to a temp location first
        temp_dir = tempfile.mkdtemp()
        print(temp_dir)
        pom_xml = 'pom.xml'
        destination = '/'.join([temp_dir, pom_xml])
        copyfile(pom_xml, destination)
        os.chdir(temp_dir)
        maven = GittyMaven()
        context = {
            'dry_run': False,
            'branch_parts': ['master'],
            'a_task': False,
            'is_stable': False,
        }
        new_version = '1.3.5-SNAPSHOT'
        maven.bump_version_to(context, new_version)
        maven.get_version_info(context)
        self.assertEqual(new_version, context['current_version'])
        os.remove(destination)

    def test_do_not_bump_version_if_dry_run(self):
        # where are we?
        cwd = os.path.dirname(__file__)
        # from here, this is where the pom is...
        os.chdir(cwd + '/maven_sample_snapshot')

        # copy the pom to a temp location first
        temp_dir = tempfile.mkdtemp()
        pom_xml = 'pom.xml'
        destination = '/'.join([temp_dir, pom_xml])
        copyfile(pom_xml, destination)
        os.chdir(temp_dir)
        maven = GittyMaven()
        context = {
            'dry_run': True,
            'branch_parts': ['master'],
            'a_task': False,
            'is_stable': False,
        }
        new_version = '1.3.5-SNAPSHOT'
        maven.bump_version_to(context, new_version)
        maven.get_version_info(context)
        self.assertEqual('1.0.0-SNAPSHOT', context['current_version'])
        os.remove(destination)
