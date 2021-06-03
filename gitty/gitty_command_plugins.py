import os
import importlib
from pathlib import Path
from gitty import GittyCommand, Color


class GittyPlugins(GittyCommand):
    _title = 'plugins'
    _name = 'list installed plugins'
    _bindings = ['plugins']

    def __init__(self, context):
        # initialize the plugins array in the context
        context["plugins"] = []

        # look in the home directory and current directory for plugins
        self.register_plugins_at(Path.home().joinpath('.gitty'), context, 'home')
        self.register_plugins_at(Path.cwd().joinpath(".gitty"), context, 'local')

    @staticmethod
    def register_plugins_at(plugin_path, context, suffix):
        # plugin_path = directory.joinpath('plugins.py')
        if plugin_path.exists():
            import imp
            # print('adding plugin from {0} as {1}'.format(plugin_path, module_name))
            index = 0
            for plugin in plugin_path.glob('*.py'):
                module_name = 'gitty_plugin_{0}_{1}'.format(suffix, index)
                index = index + 1
                with open(plugin, 'rb') as fp:
                    # print('loading module {0} from file {1}'.format(module_name, plugin))
                    plugin = imp.load_module(module_name, fp, str(plugin), ('.py', 'rb', imp.PY_SOURCE))
                    plugin.register(context)
                    context["plugins"].append(plugin.describe(context))

    def do_it(self, context):
        # print('available commands on branch "{}" are:'.format(Color.white_lt(context['current_branch'])))
        plugins = context["plugins"]
        print('Available plugins:')
        for plugin in plugins:
            print(' - ' + plugin)
