from xml.etree import ElementTree


def bump_maven_version_to(context, new_version):
    print('bumping pom to', new_version)

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


def get_version_info_maven(context):
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
    if context['current_version'].endswith('-SNAPSHOT'):

        context['release_version'] = context['current_version'][: -9]
        # i think these are the same, but i'm not positive...
        context['new_child_version'] = context['release_version']

        # build the next version
        release_version_split = context['release_version'].split(".")
        context['new_stabilization_branch'] = '.'.join(release_version_split[:-1]) + '/master'
        context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/release'
        next_sub = str(int(release_version_split[2]) + 1)
        next_min = str(int(release_version_split[1]) + 1)

        patch_version = release_version_split.copy()
        patch_version[2] = next_sub
        context['next_patch'] = '.'.join(patch_version) + '-SNAPSHOT'

        context['next_minor'] = '.'.join([
            release_version_split[0],
            next_min,
            '0'
        ]) + '-SNAPSHOT'

        # we want to increment the last number, regardless of how many there are...
        next_version = release_version_split.copy()
        next_version[-1] = str(int(next_version[-1]) + 1)
        context['next_version'] = '.'.join(next_version) + '-SNAPSHOT'

    else:
        print('should this ever happen?')


# this is to make the xml in the pom retain comments...
class CommentedTreeBuilder(ElementTree.TreeBuilder):
    def comment(self, data):
        self.start(ElementTree.Comment, {})
        self.data(data)
        self.end(ElementTree.Comment)
