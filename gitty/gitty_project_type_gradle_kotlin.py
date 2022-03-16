from os import path
from gitty import GittyProjectType


class GittyGradleKotlin(GittyProjectType):

    # experimental support for kotlin/gradle projects

    def get_name(self):
        return 'gradle (w/ kotlin)'

    def is_in_use(self, context):
        is_gradle = path.exists('settings.gradle.kts')
        if is_gradle:
            context['project_type_name'] = self.get_name()
            context['project_file'] = 'settings.gradle.kts'
        # print("**** GRADLE ****")
        return is_gradle

    def get_version_info(self, context):
        # start at the project file
        main_project_file = context['project_file']
        # print("starting at {}".format(main_project_file))
        # find the "include" line
        include_line = ''
        with open(main_project_file) as file:
            for line in file:
                line = line.strip()
                if line.strip().startswith('include'):
                    include_line = line
                    app_path = include_line.split('"')[1]
                elif line.strip().startswith('rootProject.name'):
                    include_line = line
                    app_path = '.'

        # TODO: this will need some attention for multi-build projects; we
        #  will want to make it possible to deal with more than one build
        #  file - that will be a nice feature - i think we just want a list
        #  of project files and would only support keeping the version
        #  numbers in lockstep (initially, at least). (I suspect xcode
        #  support would benefit from this as well).
        # print('app path is: {}'.format(app_path))

        if len(app_path) > 0:
            # now we have our actual config file and can
            # start setting things up...
            app_file_name = path.join(app_path, 'build.gradle.kts')
            context['project_file'] = app_file_name
            # print('app file: {}'.format(app_file_name))
            with open(app_file_name) as app_file:
                for line in app_file:
                    line = line.rstrip()
                    if line.startswith('version'):
                        current_version = line.split('=')[1].strip().replace('"', '')
                        context['current_version'] = current_version
                        current_version_parts = current_version.split('.')
                        context['hotfix'] = not current_version.endswith('SNAPSHOT')
                        current_version_number_parts = current_version.split('-')[0].split('.')
                        context['new_stabilization_version'] = '.'.join(current_version_number_parts[:-1])
                        # print('new_stabilization_version: {}'.format(context['new_stabilization_version']))
                        context['new_release_branch'] = '/'.join([
                            context['new_stabilization_version'],
                            context['release_prefix'],
                        ])
                        context['new_stabilization_branch'] = '/'.join([
                            context['new_stabilization_version'],
                            context['trunk'],
                        ])
                        context['next_master_version'] = '.'.join([
                            current_version_parts[0],
                            str(int(current_version_parts[1]) + 1),
                            current_version_parts[2],
                        ])
                        context['next_stable_version'] = '.'.join([
                            current_version_number_parts[0],
                            current_version_number_parts[1],
                            str(int(current_version_number_parts[2]) + 1) + '-SNAPSHOT',
                        ])
                        context['release_version'] = '.'.join([
                            current_version_number_parts[0],
                            current_version_number_parts[1],
                            current_version_number_parts[2],
                        ])

    def bump_version_to(self, context, new_version):
        print('# setting version to "{}"'.format(new_version))

        if not context['dry_run']:

            with open(context['project_file'], 'r', encoding='UTF-8') as file:
                # read the file
                lines = file.readlines()
                # strip trailing white space
                lines = [line.rstrip() for line in lines]

                for index in range(len(lines)):
                    if lines[index].startswith('version'):
                        lines[index] = 'version = "{}"'.format(new_version)
                    # print(lines[index])

            with open(context['project_file'], 'w', encoding='UTF-8') as file:
                for line in lines:
                    file.write(line+'\n')
