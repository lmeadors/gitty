from os import path
from xml.etree import ElementTree

from gitty import GittyProjectType


# this is to make the xml in the pom retain comments...
from gitty.gitty_xml_tree_builder import CommentedTreeBuilder


class GittyMaven(GittyProjectType):

    pom_ns = 'http://maven.apache.org/POM/4.0.0'
    ns = {'pom': pom_ns}

    def get_name(self):
        return 'maven'

    def is_in_use(self, context):
        is_maven = path.exists('pom.xml')
        if is_maven:
            context['project_type_name'] = self.get_name()
            context['project_file'] = 'pom.xml'
        return is_maven

    def get_version_info(self, context):

        pom, pom_doc = self.read_pom()

        current_version_tag = pom.find('pom:version', self.ns)
        current_version = current_version_tag.text
        context['current_version'] = current_version

        context['hotfix'] = current_version in context['tags_on_commit']

        if context['current_version'].endswith('-SNAPSHOT'):

            # we're not on a release branch

            context['release_version'] = context['current_version'][: -9]

            # build the next version
            release_version_split = context['release_version'].split(".")
            if context['a_task']:
                # we're on a task, so no release or stabilization is needed
                context['new_stabilization_branch'] = None
                context['new_release_branch'] = None
                context['new_stabilization_version'] = None
            else:
                if context['is_stable']:
                    # we're already on a stabilization branch, so this includes the full version
                    context['new_stabilization_branch'] = '.'.join(release_version_split) + '/' + context['trunk']
                    context['new_release_branch'] = '.'.join(release_version_split) + '/' + context['release_prefix']
                    context['new_stabilization_version'] = '.'.join(release_version_split) + '.0-SNAPSHOT'
                else:
                    # we're not in a stabilization ecosystem - this will make one...
                    context['new_stabilization_branch'] = '.'.join(release_version_split[:-1]) + '/' + context['trunk']
                    context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/' + context['release_prefix']
                    context['new_stabilization_version'] = '.'.join(release_version_split) + '-SNAPSHOT'

            if context['is_stable']:
                context['current_release_branch'] = '/'.join([
                    context['branch_parts'][0],
                    context['release_prefix']
                ])
            else:
                # we're on THE master branch - so there is not a current release branch
                context['current_release_branch'] = None

            self.build_next_version_numbers(context, release_version_split)

        else:
            # this can happen when making a hotfix!

            # we want to make a stabilization ecosystem from this commit...
            context['release_version'] = context['current_version']

            # build the next version
            release_version_split = context['release_version'].split(".")

            # we're on an actual release branch, so this includes the full version
            context['new_release_branch'] = '.'.join(release_version_split) + '/' + context['release_prefix']
            context['new_stabilization_branch'] = '.'.join(release_version_split) + '/' + context['trunk']
            context['new_stabilization_version'] = '.'.join(release_version_split) + '.0-SNAPSHOT'

            context['current_release_branch'] = '/'.join([
                context['branch_parts'][0],
                context['release_prefix']
            ])

            self.build_next_version_numbers(context, release_version_split)

    def bump_version_to(self, context, new_version):
        print('# setting pom version to "{}"'.format(new_version))

        if not context['dry_run']:

            pom, pom_doc = self.read_pom()

            version_tag = pom.find('pom:version', self.ns)
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

    def read_pom(self):
        # a pom has a namespace
        ElementTree.register_namespace('', self.pom_ns)
        # we use this so we preserve comments in the pom
        parser = ElementTree.XMLParser(target=CommentedTreeBuilder())
        pom_doc = ElementTree.parse('pom.xml', parser)
        pom = pom_doc.getroot()
        return pom, pom_doc

    @staticmethod
    def build_next_version_numbers(context, release_version_split):
        next_sub = str(int(release_version_split[2]) + 1)
        next_min = str(int(release_version_split[1]) + 1)
        patch_version = release_version_split.copy()
        patch_version[2] = next_sub
        context['next_master_version'] = '.'.join([
            release_version_split[0],
            next_min,
            '0'
        ]) + '-SNAPSHOT'
        # we want to increment the last number, regardless of how many there are...
        next_stable_version = release_version_split.copy()
        next_stable_version[-1] = str(int(next_stable_version[-1]) + 1)
        context['next_stable_version'] = '.'.join(next_stable_version) + '-SNAPSHOT'

