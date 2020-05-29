from distutils.core import run_setup


def bump_pip_version_to(context, new_version):
    # no-op to show what this function should do - a template for other project types
    return


def get_version_info_pip(context):
    context['project_file'] = 'setup.py'
    setup = run_setup(context['project_file'], stop_after='config')
    current_version = setup.metadata.version

    # print(setup.metadata.__dict__)
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

    context['current_release_branch'] = 'n/a'

    context['new_stabilization_version'] = 'unknown'
