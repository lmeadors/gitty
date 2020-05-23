import json


def bump_node_version_to(context, new_version):
    print('bump version to {}'.format(new_version))

    if not context['dry_run']:
        with open('package.json') as package_json:
            data = json.load(package_json)
            data['version'] = new_version
        with open('package.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)


def get_version_info_node(context):
    context['project_file'] = 'package.json'
    with open('package.json') as package_json:
        data = json.load(package_json)
        context['current_version'] = data['version']
        context['release_version'] = data['version']
        # i think these are the same, but i'm not positive...
        context['new_child_version'] = context['release_version']
        release_version_split = context['release_version'].split(".")
        context['new_stabilization_branch'] = '.'.join(release_version_split[:-1]) + '/master'
        context['new_release_branch'] = '.'.join(release_version_split[:-1]) + '/release'
        # increment the patch
        context['next_patch'] = '.'.join([
            release_version_split[0],
            release_version_split[1],
            str(int(release_version_split[2]) + 1),
        ])
        next_min = str(int(release_version_split[1]) + 1)
        context['next_minor'] = '.'.join([
            release_version_split[0],
            next_min,
            '0'
        ])
        # we want to increment the last number, regardless of how many there are...
        next_version = release_version_split.copy()
        next_version[-1] = str(int(next_version[-1]) + 1)
        context['next_version'] = '.'.join(next_version)


