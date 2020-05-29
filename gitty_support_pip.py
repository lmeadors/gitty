import json
from distutils.core import run_setup
from distutils.core import Distribution


def bump_pip_version_to(context, new_version):
    # no-op to show what this function should do - a template for other project types
    return


def get_version_info_pip(context):
    # this reads a setup.py file
    setup = run_setup('./setup.py', stop_after='config')
    print(setup.metadata.version)
    context['hotfix'] = None
    context['project_file'] = 'unknown'
    context['current_version'] = 'unknown'
    context['release_version'] = 'unknown'
    context['new_stabilization_branch'] = 'unknown/master'
    context['new_release_branch'] = 'unknown/releases'
    context['next_master_version'] = 'unknown'
    context['next_stable_version'] = 'unknown'
