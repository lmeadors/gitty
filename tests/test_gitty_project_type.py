from unittest import TestCase

from gitty import GittyProjectType, GittyUnknownProjectType


class TestGittyProjectType(TestCase):

    def test_base_type_should_not_do_much(self):
        project = GittyProjectType()
        self.assertEqual('None', project.get_name())
        context = {}
        project.get_version_info(context)
        project.is_in_use(context)
        project.bump_version_to(context, 'blah')
        self.assertEqual(0, len(context))

    def test_unknown_project_always_available_but_useless(self):
        project = GittyUnknownProjectType()
        context = {}
        self.assertTrue(project.is_in_use(context))
        self.assertEqual('unknown', project.get_name())

        project.get_version_info(context)
        self.assertIsNone(context['current_version'])
        self.assertIsNone(context['project_file'])

        project.bump_version_to(context, 'foo')
