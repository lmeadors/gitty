from gitty import GittyCommand, Color


def register(context):
	# we're installing a new command here - append it to the commands in the context
	context["commands"].append(GittyNewPullRequest())


def describe(context):
	return 'pr - create a new AWS CodeCommit pull request'


class GittyNewPullRequest(GittyCommand):
	_title = 'new pull request'
	_name = 'create a new pull request'
	_bindings = ['pull-request', 'pr']

	def get_description(self, context):
		return [
			'# create a new pull request (PR) for AWS Code Commit, using the AWS CLI',
			'# - source branch:     {}'.format(context['current_branch']),
			'# - destination branch {}'.format(context['parent_version_branch'])
		]

	def do_it(self, context):

		cmd_for_remote_url = 'git remote get-url {0}'.format(context['git_remote'])
		# this comes back as "ssh://mwt-git-codecommit/v1/repos/my_url_name", but we just want "my_url_name"
		repo_url = GittyCommand.execute_command_safe(context, cmd_for_remote_url.split(' ')).decode('utf-8')
		# we just want the last bit of this, and it ends with a LF, so we strip it
		repo_name = repo_url.split("/")[-1].strip()

		options = '--targets repositoryName={0},sourceReference={1},destinationReference={2}'.format(
			repo_name,
			context['current_branch'],
			context['parent_version_branch']
		)

		pr_command = 'aws codecommit create-pull-request --no-cli-pager --title {0} {1} --query pullRequest.pullRequestId'.format(
			context['branch_parts'][-1], options)
		# print(pr_command)

		# RESPONSE=`eval "${CMD}"`
		pr_result = GittyCommand.execute_command(context, pr_command.split(' ')).decode('utf-8')
		# RESPONSE="${RESPONSE%\"}"
		# RESPONSE="${RESPONSE#\"}"
		pr_id = pr_result.replace('"', '').strip()
		# echo "${RESPONSE}"
		print() # a blank line to break this up
		print("pull request created here:")
		print(
			'https://console.aws.amazon.com/codesuite/codecommit/repositories/{0}/pull-requests/{1}/details?region=us-east-1'.format(
				repo_name, pr_id))
		# echo "https://console.aws.amazon.com/codesuite/codecommit/repositories/${REPO}/pull-requests/${RESPONSE}/details?region=us-east-1"
