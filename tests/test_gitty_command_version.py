from unittest import TestCase

from gitty.gitty_command_version import GittyVersion


class TestGittyVersion(TestCase):
    def test_get_description(self):
        cmd = GittyVersion()
        description = cmd.get_description({'gitty_version': 'foo'})
        self.assertEqual("show current gitty version (foo)", description[0])
        self.assertEqual(1, len(description))

    def test_is_always_available(self):
        cmd = GittyVersion()
        self.assertTrue(cmd.is_available({}))

    def test_should_do_it(self):
        cmd = GittyVersion()
        cmd.do_it({'gitty_version': 'foo'})
