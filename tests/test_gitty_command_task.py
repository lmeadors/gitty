import sys
from unittest import TestCase

from gitty import DescribeExecutor
from gitty.gitty_command_task import GittyTask
from gitty.gitty_git_api import GitAPI


class TestGittyTask(TestCase):
    def test_get_description(self):
        expected = [
            '# start a new task branch (name is required)',
            '# for example: if you said "gitty t 123234_sample_task_here", then you would get this:',
            'git checkout -b 1.1/tasks/123234_sample_task_here',
        ]
        cmd = GittyTask()
        context = {
            'task_prefix': 'blah/',
            'task_name': '123_foo',
            'git_api': GitAPI(DescribeExecutor()),
        }
        description = cmd.get_description(context)
        for i in range(len(description)):
            self.assertEqual(expected[1], description[1])
        self.assertEqual(len(expected), len(description))

    def test_should_not_make_a_task_outside_of_a_git_repo(self):
        cmd = GittyTask()
        context = {'current_branch': None}
        self.assertFalse(cmd.is_available(context))

    def test_should_not_make_a_task_in_a_git_repo_on_a_task(self):
        cmd = GittyTask()
        context = {
            'current_branch': 'some_task_branch',
            'a_task': True
        }
        self.assertFalse(cmd.is_available(context))

    def test_should_make_a_task_in_a_git_repo_not_on_a_task(self):
        cmd = GittyTask()
        context = {
            'current_branch': 'some_branch',
            'a_task': False
        }
        self.assertTrue(cmd.is_available(context))

    def test_should_really_do_it(self):
        sys.argv = ['gitty', 't', 'task_name']
        context = {
            'task_prefix': 'blah/',
            'task_name': '123_foo',
            'git_api': GitAPI(DescribeExecutor()),
        }
        cmd = GittyTask()
        cmd.do_it(context)
