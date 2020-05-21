import subprocess
import sys
from xml.etree import ElementTree


def setup(context):
    current_branch_output = subprocess.check_output('git rev-parse -abbrev-ref HEAD'.split())
    context['current_branch'] = current_branch_output.decode().strip()
    context['branch_parts'] = context['current_branch'].split("/")
    if len(context['branch_parts']) > 1:
        context['task_prefix'] = context['branch_parts'][0] + '/tasks/'
    else:
        context['task_prefix'] = 'tasks/'

    return context


def command_handler(context):
    switcher = {
        'help': help_cmd,
        'release': release,
        'r': release,
        't': task,
        'release_from_master': release_from_master,
        'release_from_point': release_from_point,
        'task': task,
        'task_from_master': task_from_master,
        'task_from_point': task_from_point
    }
    print("command:", context['command'])
    switcher.get(context['command'])(context)


def release_from_master(context):
    # print('make a new release from master:', context)
    get_version_info(context)
    # print(context)
    # current_branch_cmd = ['git', 'checkout', '-b', context['new_stab_branch']]
    # current_branch_output = subprocess.check_output(current_branch_cmd)

    # print('branch from master to', context['new_master_branch'])
    execute_command(('git checkout -b ' + context['new_master_branch']).split())
    # print('branch from', context['new_master_branch'], 'to', context['new_release_branch'])
    execute_command(('git checkout -b ' + context['new_release_branch']).split())
    # print('set pom.xml on', context['new_release_branch'], 'to', context['release_version'], "(non snapshot)")
    bump_pom_version_to(context, context['release_version'])
    execute_command('git add pom.xml'.split())
    # this has spaces in a parameter, so it's different...
    execute_command([
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['release_version'] + '"'
    ])
    # print('tag as', context['release_version'])
    execute_command('git tag {}'.format(context['release_version']).split())
    execute_command('git checkout {}'.format(context['new_master_branch']).split())
    # this is a transient branch/merge, so we won't actually merge, we'll just mark it as merged
    execute_command('git merge --strategy=ours {}'.format(context['new_release_branch']).split())
    bump_pom_version_to(context, context['next_version'])
    # print('set pom.xml on', context['new_master_branch'], 'to', context['next_version'], '(next snapshot version)')
    execute_command('git add pom.xml'.split())
    # this has spaces in a parameter, so it's different...
    execute_command([
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['next_version'] + '"'
    ])
    execute_command('git checkout master'.split())
    execute_command('git merge --strategy=ours {}'.format(context['new_master_branch']).split())
    bump_pom_version_to(context, context['next_minor'])
    execute_command('git add pom.xml'.split())
    execute_command([
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['next_minor'] + '"'
    ])


def execute_command(cmd):
    print('$', ' '.join(cmd))
    output = subprocess.check_output(cmd)
    # print(output, '\n')


def release_from_point(context):
    get_version_info(context)
    execute_command('git checkout {}'.format(context['new_release_branch']).split())
    execute_command('git merge {}'.format(context['current_branch']).split())
    # print('(bump pom on {} to {} - no snapshot)'.format(context['new_release_branch'], context['release_version']))
    bump_pom_version_to(context, context['release_version'])
    execute_command('git add pom.xml'.split())
    execute_command([
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['release_version'] + '"'
    ])
    execute_command('git tag {}'.format(context['release_version']).split())
    execute_command('git checkout {}'.format(context['current_branch']).split())
    # merge changes, but not really.
    execute_command('git merge {}'.format(context['new_release_branch']).split())
    # print("(bump pom on {} to {})".format(context['current_branch'], context['next_version']))
    bump_pom_version_to(context, context['next_version'])
    execute_command('git add pom.xml'.split())
    execute_command([
        'git',
        'commit',
        '-m',
        '"bumped version to ' + context['next_version'] + '"'
    ])


def help_cmd(context):
    if len(context['branch_parts']) > 1:
        # a release branch
        print('available commands on branch "{}" are:'.format(context['current_branch']))
        print('  release     - create a new tagged release')
        print('  task [name] - create a new task branch named "{}[name]"'.format(context['task_prefix']))
    else:
        # master?
        print('available commands on branch "{}" are:'.format(context['current_branch']))
        print('  release     - create a new release stabilization branch and release candidate')
        print('  task [name] - create a new task branch named "{}[name]"'.format(context['task_prefix']))


def task_from_master(context):
    execute_command('git checkout -b {}{}'.format(context['task_prefix'], context['task_name']).split())


def task_from_point(context):
    execute_command('git checkout -b {}{}'.format(context['task_prefix'], context['task_name']).split())


def task(context):
    print('make a new task branch')
    # we need a task name - like 123234_some_task_name
    if len(sys.argv) > 2:
        context['task_name'] = sys.argv[2]
        if len(context['branch_parts']) > 1:
            context['command'] = 'task_from_point'
        else:
            context['command'] = 'task_from_master'
    else:
        context['command'] = 'help'

    # print('release command:', context['command'])
    command_handler(context)


def release(context):
    if len(context['branch_parts']) > 1:
        context['command'] = 'release_from_point'
    else:
        context['command'] = 'release_from_master'
    command_handler(context)


def get_version_info(context):
    pom_ns = 'http://maven.apache.org/POM/4.0.0'
    ns = {'pom': pom_ns}
    ElementTree.register_namespace('', pom_ns)

    # we use this so we preserve comments in the pom
    parser = ElementTree.XMLParser(target=CommentedTreeBuilder())
    pom_doc = ElementTree.parse('pom.xml', parser)
    pom = pom_doc.getroot()

    current_version_tag = pom.find('pom:version', ns)
    context['current_version'] = current_version_tag.text
    if context['current_version'].endswith('-SNAPSHOT'):

        context['release_version'] = context['current_version'][: -9]
        # print('snapshot; release version is', context['release_version'])

        # build the next version
        release_version_split = context['release_version'].split(".")
        context['new_master_branch'] = '.'.join(release_version_split[:-1]) + '/master'
        context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/release'
        next_sub = str(int(release_version_split[2]) + 1)
        next_min = str(int(release_version_split[1]) + 1)
        release_version_split[2] = next_sub
        context['next_version'] = '.'.join(release_version_split) + '-SNAPSHOT'
        context['next_minor'] = '.'.join([
            release_version_split[0],
            next_min,
            '0'
        ]) + '-SNAPSHOT'
    else:
        print('should this ever happen?')


def bump_pom_version_to(context, new_version):
    print('bumping pom to', new_version)

    # make a backup
    # shutil.copy('pom.xml', '.backup-pre-' + new_version + '.pom.xml')

    # a pom has a namespace
    pom_ns = 'http://maven.apache.org/POM/4.0.0'
    ns = {'pom': pom_ns}
    ElementTree.register_namespace('', pom_ns)

    # we use this so we preserve comments in the pom
    parser = ElementTree.XMLParser(target=CommentedTreeBuilder())
    pom_doc = ElementTree.parse('pom.xml', parser)
    pom = pom_doc.getroot()

    version_tag = pom.find('pom:version', ns)
    version_tag.text = new_version
    pom_doc.write("pom.xml")

    # edit the pom to make it a non-snapshot version


# this is to make the xml in the pom retain comments...
class CommentedTreeBuilder(ElementTree.TreeBuilder):
    def comment(self, data):
        self.start(ElementTree.Comment, {})
        self.data(data)
        self.end(ElementTree.Comment)
