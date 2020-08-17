import json
from os import path
from xml.etree import ElementTree
# noinspection PyUnresolvedReferences
# this is so distutils doesn't complain about being imported before setuptools...apparently that's frowned upon.
import setuptools
from distutils.core import run_setup


class GittyProjectType:

    def get_name(self):
        return 'None'

    def get_version_info(self, context):
        print('put version info into context')

    def is_in_use(self, context):
        print('does this project type fit the current directory?')

    def bump_version_to(self, context, new_version):
        print('bump version in project file to {}'.format(new_version))


class GittyUnknownProjectType(GittyProjectType):

    def get_name(self):
        return 'unknown'

    def is_in_use(self, context):
        return True

    def get_version_info(self, context):
        print('unable to get version info for unknown project type')

    def bump_version_to(self, context, new_version):
        print('unable to set version for unknown project type')


class GittyMaven(GittyProjectType):

    def get_name(self):
        return 'maven'

    def is_in_use(self, context):
        # print('is there a pom.xml file in {}?'.format(path.curdir))
        # for f in listdir(path.curdir):
        #     print(f)

        is_maven = path.exists('pom.xml')
        # print('is maven: {}'.format(is_maven))
        if is_maven:
            context['project_type_name'] = 'maven'
        return is_maven

    def get_version_info(self, context):
        context['project_file'] = 'pom.xml'
        pom_ns = 'http://maven.apache.org/POM/4.0.0'
        ns = {'pom': pom_ns}
        ElementTree.register_namespace('', pom_ns)

        # we use this so we preserve comments in the pom
        parser = ElementTree.XMLParser(target=CommentedTreeBuilder())
        pom_doc = ElementTree.parse('pom.xml', parser)
        pom = pom_doc.getroot()

        current_version_tag = pom.find('pom:version', ns)
        context['current_version'] = current_version_tag.text

        # todo: we could use `git tag --points-at HEAD` to see if this commit is tagged - that might be a better way to
        #  know if we want a hotfix or not - for now, this will do...

        if context['current_version'].endswith('-SNAPSHOT'):

            context['hotfix'] = False

            context['release_version'] = context['current_version'][: -9]

            # build the next version
            release_version_split = context['release_version'].split(".")
            if len(context['branch_parts']) > 1:
                # we're already on a stabilization branch, so this includes the full version
                context['new_stabilization_branch'] = '.'.join(release_version_split) + '/master'
                context['new_release_branch'] = '.'.join(release_version_split) + '/releases'
                context['new_stabilization_version'] = '.'.join(release_version_split) + '.0-SNAPSHOT'
            else:
                # we're on master, so we want to only include major.minor
                context['new_stabilization_branch'] = '.'.join(release_version_split[:-1]) + '/master'
                context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/releases'
                context['new_stabilization_version'] = '.'.join(release_version_split) + '.0-SNAPSHOT'

            context['current_release_branch'] = '/'.join([
                context['branch_parts'][0],
                'releases'
            ])

            next_sub = str(int(release_version_split[2]) + 1)
            next_min = str(int(release_version_split[1]) + 1)

            patch_version = release_version_split.copy()
            patch_version[2] = next_sub
            context['next_stable_version'] = '.'.join(patch_version) + '-SNAPSHOT'

            context['next_master_version'] = '.'.join([
                release_version_split[0],
                next_min,
                '0'
            ]) + '-SNAPSHOT'

            # we want to increment the last number, regardless of how many there are...
            next_stable_version = release_version_split.copy()
            next_stable_version[-1] = str(int(next_stable_version[-1]) + 1)
            context['next_stable_version'] = '.'.join(next_stable_version) + '-SNAPSHOT'

        else:
            # this can happen when making a hotfix!

            context['hotfix'] = True

            # we want to make a stabilization ecosystem from this commit...
            context['release_version'] = context['current_version']

            # build the next version
            release_version_split = context['release_version'].split(".")

            # we're on an actual release branch, so this includes the full version
            context['new_stabilization_branch'] = '.'.join(release_version_split) + '/master'
            context['new_release_branch'] = '.'.join(release_version_split) + '/releases'
            context['new_stabilization_version'] = '.'.join(release_version_split) + '.0-SNAPSHOT'

            context['current_release_branch'] = '/'.join([
                context['branch_parts'][0],
                'releases'
            ])

            next_sub = str(int(release_version_split[2]) + 1)
            next_min = str(int(release_version_split[1]) + 1)

            patch_version = release_version_split.copy()
            patch_version[2] = next_sub
            context['next_stable_version'] = '.'.join(patch_version) + '-SNAPSHOT'

            context['next_master_version'] = '.'.join([
                release_version_split[0],
                next_min,
                '0'
            ]) + '-SNAPSHOT'

            # we want to increment the last number, regardless of how many there are...
            next_stable_version = release_version_split.copy()
            next_stable_version[-1] = str(int(next_stable_version[-1]) + 1)
            context['next_stable_version'] = '.'.join(next_stable_version) + '-SNAPSHOT'

    def bump_version_to(self, context, new_version):
        print('setting pom version to "{}"'.format(new_version))

        if not context['dry_run']:
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

            # read the pom back in...
            f = open("pom.xml", "r")
            contents = f.readlines()
            f.close()

            # insert xml declaration
            contents.insert(0, '<?xml version="1.0" encoding="UTF-8"?>\n')
            # append a blank line
            contents.append('\n')

            f = open("pom.xml", "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()


class GittyNode(GittyProjectType):

    def get_name(self):
        return 'node'

    def get_version_info(self, context):
        # node project file...
        context['project_file'] = 'package.json'

        # todo: we could use `git tag --points-at HEAD` to see if this commit is tagged - that might be a better way to
        #  know if we want a hotfix or not - for now, we'll assume that hotfix doesn't really apply for node projects - any
        #  commit could be the starting point for a hotfix
        context['hotfix'] = True

        with open(context['project_file']) as package_json:
            data = json.load(package_json)
            context['current_version'] = data['version']
            context['release_version'] = data['version']
            release_version_split = context['release_version'].split(".")
            context['new_stabilization_branch'] = '.'.join(release_version_split) + '/master'
            context['new_release_branch'] = '.'.join(release_version_split) + '/releases'
            context['current_release_branch'] = '.'.join(release_version_split[:-1]) + '/releases'
            # increment the patch
            context['next_stable_version'] = '.'.join([
                release_version_split[0],
                release_version_split[1],
                str(int(release_version_split[2]) + 1),
            ])
            next_min = str(int(release_version_split[1]) + 1)
            context['next_master_version'] = '.'.join([
                release_version_split[0],
                next_min,
                '0'
            ])
            # we want to increment the last number, regardless of how many there are...
            next_stable_version = release_version_split.copy()
            next_stable_version[-1] = str(int(next_stable_version[-1]) + 1)
            context['next_stable_version'] = '.'.join(next_stable_version)
            context['new_stabilization_version'] = '.'.join(release_version_split) + '.0'

    def is_in_use(self, context):
        return path.exists('package.json')

    def bump_version_to(self, context, new_version):
        print('bump version to {}'.format(new_version))

        if not context['dry_run']:
            with open('package.json') as package_json:
                data = json.load(package_json)
                data['version'] = new_version
            with open('package.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)


class GittyPip(GittyProjectType):

    def get_name(self):
        return 'pip'

    def get_version_info(self, context):
        context['project_file'] = 'setup.py'
        setup = run_setup(context['project_file'], stop_after='config')

        current_version = setup.metadata.version

        context['hotfix'] = False
        context['current_version'] = current_version
        context['release_version'] = current_version

        current_version_split = current_version.split(".")
        stable_branch_version = '.'.join(
            current_version_split[:-1]
        )
        context['new_stabilization_branch'] = stable_branch_version + '/master'
        context['new_release_branch'] = stable_branch_version + '/releases'

        next_master_version = '.'.join([
            current_version_split[0],
            str(int(current_version_split[1]) + 1),
            current_version_split[2]
        ])
        context['next_master_version'] = next_master_version

        next_stable_version = '.'.join([
            current_version_split[0],
            current_version_split[1],
            str(int(current_version_split[2]) + 1)
        ])
        context['next_stable_version'] = next_stable_version

        if len(context['branch_parts']) > 1:
            context['current_release_branch'] = stable_branch_version + '/releases'
        else:
            context['current_release_branch'] = 'n/a'

        context['new_stabilization_version'] = 'unknown'

    def is_in_use(self, context):
        return path.exists('setup.py')

    def bump_version_to(self, context, new_version):
        # we need to read in the setup.py file and replace the
        print('set version to {} in {}'.format(new_version, context['project_file']))

        if not context['dry_run']:

            with open(context['project_file'], 'r') as setup_file:
                lines = setup_file.readlines()

            new_lines = []
            for line in lines:
                if line.strip().startswith('version='):
                    new_lines.append('    version="{}",'.format(new_version))
                else:
                    new_lines.append(line.rstrip())

            with open(context['project_file'], 'w') as setup_file:
                for line in new_lines:
                    setup_file.write(line + "\n")


# this is to make the xml in the pom retain comments...
class CommentedTreeBuilder(ElementTree.TreeBuilder):
    def comment(self, data):
        self.start(ElementTree.Comment, {})
        self.data(data)
        self.end(ElementTree.Comment)
