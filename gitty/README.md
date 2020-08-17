This branch is a refactoring of the gitty commands and project types to be objects.

Each command object will have an API that it supports:

- display_help: used by the help command to show the aliases and describe behavior
- is_available: used to determine if a command can be executed in the current context
- do_it: used to perform the commands actions

Similarly, each project type will have an API that it supports:

- get_version_info: examine the project and set fields in the context
- bump_version_to: perform the actions required to bump the version to a new value

The command objects will get the project type from the context and use it to interact 
with the project meta data - that way, the commands don't have to know/care about 
the project type, they can simply call the API to perform the needed actions.

Eventually, I would like to add support for pre/post command hooks that a user could 
use to extend gitty to perform custom actions - perhaps a `.gitty.py` file in the 
current directory with expected function names like `pre_stabilize` and `post_release`. 
The command processor could then execute those around the default behaviors.
