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
        self.register_plugin_at(Path.home().joinpath('.gitty'), context, 'home')
        self.register_plugin_at(Path.cwd().joinpath(".gitty"), context, 'local')

    @staticmethod
    def register_plugin_at(directory, context, suffix):
        plugin_path = directory.joinpath('plugins.py')
        module_name = 'gitty_plugin_{0}'.format(suffix)
        if plugin_path.exists():
            import imp
            # print('adding plugin from {0} as {1}'.format(plugin_path, module_name))
            with open(plugin_path, 'rb') as fp:
                plugin = imp.load_module(module_name, fp, '.gitty/plugins.py', ('.py', 'rb', imp.PY_SOURCE))
                plugin.register(context)
                context["plugins"].append(plugin.describe(context))

    def do_it(self, context):
        # print('available commands on branch "{}" are:'.format(Color.white_lt(context['current_branch'])))
        plugins = context["plugins"]
        print('Available plugins:')
        for plugin in plugins:
            print(plugin)
