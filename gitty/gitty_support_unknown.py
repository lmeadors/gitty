

def bump_unknown_version_to(context, new_version):
    # no-op to show what this function should do - a template for other project types
    return


def get_version_info_unknown(context):
    # this is a no-op - but it shows what's expected from get_version_info_* functions
    context['hotfix'] = None
    context['project_file'] = 'unknown'
    context['current_version'] = 'unknown'
    context['release_version'] = 'unknown'
    context['new_stabilization_branch'] = 'unknown/master'
    context['new_release_branch'] = 'unknown/releases'
    context['next_master_version'] = 'unknown'
    context['next_stable_version'] = 'unknown'
