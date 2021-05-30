import os
import tempfile
from shutil import copyfile
from gitty.gitty_project_type_maven import GittyMaven
from tests.test_gitty_project_type_base_test import ProjectTypeTestCase


class TestGittyMaven(ProjectTypeTestCase):

    def __init__(self, test_method_name):
        super().__init__(test_method_name)
        self.sample_dir = 'sample_files/maven_snapshot'

    def test_is_not_in_use(self):
        cwd = self.go_to_temp_dir()
        context = {}
        project = GittyMaven()
        self.assertFalse(project.is_in_use(context))
        self.assertEqual('lol, nope', context.get('project_type_name', 'lol, nope'))
        os.chdir(cwd)

    def test_is_in_use_and_get_name(self):
        cwd = self.go_to_sample_dir('sample_files/maven_snapshot')

        project = GittyMaven()
        context = {}
        self.assertTrue(project.is_in_use(context))
        self.assertEqual(project.get_name(), context['project_type_name'])

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_the_master(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir('sample_files/maven_snapshot')

        expected = {
            'project_type_name': 'maven',
            'project_file': 'pom.xml',

            'current_version': '1.0.0-SNAPSHOT',
            'release_version': '1.0.0',
            'next_stable_version': '1.0.1-SNAPSHOT',
            'next_master_version': '1.1.0-SNAPSHOT',

            'branch_parts': ['master'],
            'current_branch': 'master',
            'current_release_branch': None,
            'task_prefix': 'tasks/',

            'new_release_branch': '1.0/releases',
            'new_stabilization_branch': '1.0/master',
            'new_stabilization_version': '1.0.0-SNAPSHOT',

            'the_master': True,
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'is_stable': False,
            'hotfix': False,
            'tags_on_commit': [],

            'git_ref': 'HEAD',
            'git_remote': 'git_remote_here',
            'git_hash': 'git_hash_here',

        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyMaven(), 'master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_master(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir('sample_files/maven_snapshot')

        expected = {
            'current_branch': '1.0/master',
            'is_stable': True,
            'tags_on_commit': [],
            'branch_parts': ['1.0', 'master'],
            'project_file': 'pom.xml',
            'project_type_name': 'maven',
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
            'current_release_branch': '1.0/releases',
            'git_ref': 'HEAD',
            'git_remote': 'git_remote_here',
            'git_hash': 'git_hash_here'
        }

        # create the project and verify it is setting the context up as expected
        self.check_project_type_version_info(expected, GittyMaven(), '1.0/master')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_master_task(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir('sample_files/maven_snapshot')

        expected = {
            'project_type_name': 'maven',
            'current_branch': 'tasks/123_snapped_the_frame',
            'tags_on_commit': [],
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
            'current_release_branch': None,
            'git_ref': 'HEAD',
            'git_remote': 'git_remote_here',
            'git_hash': 'git_hash_here'
        }

        self.check_project_type_version_info(expected, GittyMaven(), 'tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_stable_task(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir('sample_files/maven_snapshot')

        expected = {
            'current_branch': '1.0/tasks/123_snapped_the_frame',
            'is_stable': True,
            'tags_on_commit': [],
            'branch_parts': ['1.0', 'tasks', '123_snapped_the_frame'],
            'project_type_name': 'maven',
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
            'current_release_branch': '1.0/releases',
            'git_ref': 'HEAD',
            'git_remote': 'git_remote_here',
            'git_hash': 'git_hash_here'
        }

        self.check_project_type_version_info(expected, GittyMaven(), '1.0/tasks/123_snapped_the_frame')

        # go back where we started
        os.chdir(cwd)

    def test_get_version_info_from_release_for_hotfix(self):
        # save our location and go to the sample dir we need
        cwd = self.go_to_sample_dir('sample_files/maven_release')

        tags = ['1.2.3']
        expected = {
            'current_branch': '1.2/releases',
            'is_stable': True,
            'tags_on_commit': tags,
            'branch_parts': ['1.2', 'releases'],
            'project_type_name': 'maven',
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
            'current_release_branch': '1.2/releases',
            'git_ref': 'HEAD',
            'git_remote': 'git_remote_here',
            'git_hash': 'git_hash_here'
        }

        self.check_project_type_version_info(expected, GittyMaven(), '1.2/releases', tags)

        # go back where we started
        os.chdir(cwd)

    def test_bump_version(self):
        # go to the sample directory
        cwd = self.go_to_sample_dir()

        # copy the pom to a temp location (and go there)
        destination = self.copy_sample_to_temp_dir('pom.xml')

        context = {
            'dry_run': False,
            'branch_parts': ['master'],
            'a_task': False,
            'is_stable': False,
            'tags_on_commit': [],
        }
        new_version = '1.3.5-SNAPSHOT'

        maven = GittyMaven()

        # pre-check the version
        maven.get_version_info(context)
        self.assertEqual('1.0.0-SNAPSHOT', context['current_version'])

        # update the version
        maven.bump_version_to(context, new_version)

        # check the version after we bump it
        maven.get_version_info(context)
        self.assertEqual(new_version, context['current_version'])

        # remove the copied project file
        os.remove(destination)

        # go back where we started
        os.chdir(cwd)

    def test_do_not_bump_version_if_dry_run(self):
        cwd = self.go_to_sample_dir()

        # copy the pom to a temp location first
        destination = self.copy_sample_to_temp_dir('pom.xml')

        context = {
            'dry_run': True,
            'branch_parts': ['master'],
            'a_task': False,
            'is_stable': False,
            'tags_on_commit': [],
        }

        maven = GittyMaven()

        # pre-check the version
        maven.get_version_info(context)
        self.assertEqual('1.0.0-SNAPSHOT', context['current_version'])

        # set it...but not really - just a dry run...
        new_version = '1.3.5-SNAPSHOT'
        maven.bump_version_to(context, new_version)

        # verify it did not change
        maven.get_version_info(context)
        self.assertEqual('1.0.0-SNAPSHOT', context['current_version'])

        # clean up the mess
        os.remove(destination)

        # go back where we started
        os.chdir(cwd)
