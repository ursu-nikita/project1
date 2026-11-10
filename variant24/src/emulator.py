"""UNIX-like in-memory shell emulator for variant 24."""
import argparse
import base64
import getpass
import hashlib
import json
import os
from pathlib import PurePosixPath
import shlex
import socket
import sys


class ShellError(Exception):
    """An invalid emulated command or virtual path."""


class Emulator:
    """A simple shell operating exclusively on an in-memory JSON tree."""

    def __init__(self):
        self.cwd = '/'
        self.running = True

    def execute(self, line):
        """Execute one command and return output, or raise ShellError."""
        try:
            args = shlex.split(line, posix=True)
        except ValueError as error:
            raise ShellError(f'Parser error: {error}') from error
        if not args:
            return ''
        command, *params = args
        if command == 'exit':
            self.require(params, 0, 'exit')
            self.running = False
            return ''
        if command in ('ls', 'cd'):
            self.require_range(params, 0, 1, f'{command} [path]')
            return f'{command}: {params!r}'
        raise ShellError(f'Unknown command: {command}')

    @staticmethod
    def require(args, count, usage):
        """Validate the exact number of arguments."""
        if len(args) != count:
            raise ShellError(f'Usage: {usage}')

    @staticmethod
    def require_range(args, minimum, maximum, usage):
        """Validate a range of argument counts."""
        if not minimum <= len(args) <= maximum:
            raise ShellError(f'Usage: {usage}')

    def prompt(self):
        """Build a prompt from the real username and hostname."""
        return f'{getpass.getuser()}@{socket.gethostname()}:{self.cwd}$ '


def main():
    shell = Emulator()
    while shell.running:
        try:
            line = input(shell.prompt())
            output = shell.execute(line)
            if output:
                print(output)
        except EOFError:
            break
        except ShellError as error:
            print(f'Error: {error}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
