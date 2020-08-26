from unittest import TestCase

from gitty import command_setup


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
            'current_branch': 'master'
        }
        command_setup(context)
        # print(context)
