#!/usr/bin/env python3
from gitty_support import *
import sys

context = setup({})

# figure out the command
if len(sys.argv) > 1:
    context['command'] = sys.argv[1]
else:
    context['command'] = 'help'

exit(command_handler(context))
