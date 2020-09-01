import subprocess


class Executor:
    def execute_command(self, context, command_parts, raise_error=False, dry_run=False) -> str:
        """executes a command and returns the output as a decoded and stripped string"""
        pass

    def execute_immutable_command(self, context, command_parts, raise_error=False, dry_run=False) -> str:
        """executes a command and returns the output as a decoded and stripped string"""
        pass


class DescribeExecutor(Executor):

    def execute_command(self, context, command_parts, raise_error=False, dry_run=False) -> [str]:
        response = ' '.join(command_parts)
        return [response]

    def execute_immutable_command(self, context, command_parts, raise_error=False, dry_run=False) -> [str]:
        return self.execute_command(context, command_parts, False, False)


class CommandExecutor(Executor):

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def execute_command(self, context, command_parts, raise_error=False, dry_run=False) -> str:
        # if either of these is true, it's a dry run which means don't change anything
        dry_run = self.dry_run or dry_run
        # show the command to be run
        print('$', ' '.join(command_parts))
        if not dry_run:
            try:
                return subprocess.check_output(command_parts).decode().strip()
            except subprocess.CalledProcessError as e:
                from gitty import Color
                print(Color.red_lt(e.output.decode()))
                if raise_error:
                    raise e

    def execute_immutable_command(self, context, command_parts, raise_error=False, dry_run=False) -> str:
        return self.execute_command(context, command_parts, raise_error, dry_run)
