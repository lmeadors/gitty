import os
import tempfile
from unittest import TestCase

from gitty.gitty_git_api import GitAPI
from gitty import DescribeExecutor, CommandExecutor


class TestGitAPI(TestCase):

    def __init__(self, test_name):
        super().__init__(test_name)
        self.executor = CommandExecutor()
        self.git = GitAPI(self.executor)

    def test_git_operations(self):
        context = {
            'dry_run': False
        }
        cwd = os.path.dirname(__file__)
        git_repo = self.create_new_git_repo()
        # git_repo = self.create_new_git_repo('/Users/lmeadors/projects/elm/git-api-test/test_repo')
        git = self.git

        # make a temp file in our repo and add it
        with open('file_to_add.txt', 'w+') as file_to_add:
            git.add(context, file_to_add.name, True)

        # commit that added file
        git.commit(context, 'this is a long message - neat, huh?')

        # make a tag - we'll use this later...
        init_commit_tag = 'init-commit-tag'
        git.tag(context, init_commit_tag, True)

        # what branch are we on?
        branch = git.get_current_branch(context)
        self.assertEqual('master', branch)

        # the repo should be clean now
        self.assertEqual('', git.status_is_clean(context))

        # make a new branch
        new_branch = "test_branch_01"
        git.checkout_new(context, new_branch, True, None)

        # make a temp file in our repo and add it to the new branch
        with open('file_to_add_on_branch.txt', 'w+') as file_to_add_2:
            git.add(context, file_to_add_2.name, True)

        # check our status - we are not clean now
        self.assertNotEqual('', git.status_is_clean(context))

        # commit the new file
        git.commit(context, 'this is a new file on our new {} branch'.format(new_branch))

        # check our status - we are not clean now
        self.assertEqual('', git.status_is_clean(context))

        # go back to master
        git.checkout_existing(context, 'master', True, None)

        # what branches are not merged here yet?
        self.assertTrue(new_branch in git.get_unmerged_branch_names(context))

        # merge the new branch back to master
        git.merge(context, new_branch)

        # what branches are not merged here yet?
        self.assertTrue(new_branch not in git.get_unmerged_branch_names(context))

        # what branches have been merged here?
        names = git.get_merged_branch_names(context)
        print('merged branches: {}'.format(names))
        self.assertTrue(new_branch in names)

        # remove the merged branch
        git.remove_branch(context, new_branch)

        # make sure it's gone
        self.assertTrue(new_branch not in git.get_merged_branch_names(context))
        self.assertTrue(new_branch not in git.get_unmerged_branch_names(context))

        # make a conflicting change on 2 branches and merge them using the "ours" strategy
        conflict_branch = 'conflict_branch'
        git.checkout_new(context, conflict_branch, True, None)

        git.checkout_existing(context, 'master', True, None)
        master_content = 'this is the file on the master branch - its contents should be preserved'
        with open('conflict.txt', 'w') as master_file:
            master_file.write(master_content)

        git.add(context, master_file.name, True)
        git.commit(context, master_content)

        git.checkout_existing(context, conflict_branch, True, None)
        branch_content = 'this is the file on the conflict branch - its contents should be discarded'
        with open('conflict.txt', 'w') as branch_file:
            branch_file.write(branch_content)

        git.add(context, branch_file.name, True)
        git.commit(context, branch_content)

        # go back to master and make sure the new branch appears to need to be merged
        git.checkout_existing(context, 'master', True, None)
        self.assertTrue(conflict_branch in git.get_unmerged_branch_names(context))

        # merge and verify the branch is merged
        git.merge_ours(context, conflict_branch)
        self.assertTrue(conflict_branch not in git.get_unmerged_branch_names(context))

        # now verify that our master version is what we expect
        with open('conflict.txt', 'r') as master_post_merge:
            lines = master_post_merge.readlines()
            self.assertTrue(master_content in lines)
            self.assertTrue(branch_content not in lines)

        # tag this commit a couple of times and verify that the tags exist
        tag0 = 'tag-1.1.0'
        git.tag(context, tag0, True)
        tag1 = 'tag-1.1.1'
        git.tag(context, tag1, True)
        tag_list = git.get_tags_on_commit(context)
        self.assertEqual(2, len(tag_list))
        self.assertTrue(tag0 in tag_list)
        self.assertTrue(tag1 in tag_list)
        self.assertFalse(init_commit_tag in tag_list)

    def test_should_use_custom_executor(self):
        context = {}
        executor = DescribeExecutor()
        self.git.get_current_branch(context, executor=executor)

    def create_new_git_repo(self, target=tempfile.mkdtemp()):
        # /Users/lmeadors/projects/elm/git-api-test

        os.chdir(target)
        print("pushd {}".format(target))
        self.executor.execute_command({}, 'git init'.split(), True)
        return target
