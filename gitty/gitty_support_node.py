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
        context['new_stabilization_version'] = '.'.join(release_version_split)+'.0'


