from unittest import TestCase

from gitty import command_setup


class MockGitApi:
    def get_current_branch(self, context):
        return 'master'

    def get_tags_on_commit(self, context):
        return []

    def git_hash(self, context, quiet):
        return 'hash-goes-here'

    def git_remote(self, context, quiet=False):
        return 'remote'


class TestCommand(TestCase):

    def test_setup(self):
        expected = {
            'current_branch': 'master',
            'project_type_name': 'unknown',
            'current_release_branch': None,
            'new_stabilization_version': None,
            'the_master': True,
            'branch_parts': ['master'],
            'a_master': True,
            'a_task': False,
            'a_release': False,
            'task_prefix': 'tasks/',
            'is_stable': False,
            'project_file': None,
            'current_version': 'unknown',
            'current_version_parts': ['unknown'],
            'parent_version_branch': 'master',
            'gitty_version': '1.1.2'
        }

        context = {
            'current_branch': 'master',
            'git_api': MockGitApi()
        }
        command_setup(context)
        # print(context)
