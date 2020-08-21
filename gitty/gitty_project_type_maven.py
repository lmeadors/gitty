from os import path
from xml.etree import ElementTree

from gitty import GittyProjectType


# this is to make the xml in the pom retain comments...
class CommentedTreeBuilder(ElementTree.TreeBuilder):
    def comment(self, data):
        self.start(ElementTree.Comment, {})
        self.data(data)
        self.end(ElementTree.Comment)


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
            context['project_type_name'] = self.get_name()
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

            # we're not on a release branch
            context['hotfix'] = False

            context['release_version'] = context['current_version'][: -9]

            # build the next version
            release_version_split = context['release_version'].split(".")
            if context['a_task']:
                context['new_stabilization_branch'] = None
                context['new_release_branch'] = None
                context['new_stabilization_version'] = None
            else:
                if context['is_stable']:
                    # we're already on a stabilization branch, so this includes the full version
                    context['new_stabilization_branch'] = '.'.join(release_version_split) + '/master'
                    context['new_release_branch'] = '.'.join(release_version_split) + '/releases'
                    context['new_stabilization_version'] = '.'.join(release_version_split) + '.0-SNAPSHOT'
                else:
                    # we're not in a stabilization ecosystem - this will make an inner one...
                    context['new_stabilization_branch'] = '.'.join(release_version_split[:-1]) + '/master'
                    context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/releases'
                    context['new_stabilization_version'] = '.'.join(release_version_split) + '-SNAPSHOT'

            if context['is_stable']:
                context['current_release_branch'] = '/'.join([
                    context['branch_parts'][0],
                    'releases'
                ])
            else:
                context['current_release_branch'] = None

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
        print('# setting pom version to "{}"'.format(new_version))

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

