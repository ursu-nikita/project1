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


def run_script(emulator, path):
    """Echo commands and stop on the first script error."""
    with open(path, encoding='utf-8') as stream:
        for number, raw in enumerate(stream, start=1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            print(emulator.prompt() + line)
            try:
                result = emulator.execute(line)
            except ShellError as error:
                print(f'Error in script line {number}: {error}', file=sys.stderr)
                return False
            if result:
                print(result)
            if not emulator.running:
                break
    return True


def main(argv=None):
    """Read CLI/JSON configuration, run script, then enter REPL."""
    parser = argparse.ArgumentParser(description='Variant 24 shell emulator')
    parser.add_argument('--vfs', help='path to VFS JSON')
    parser.add_argument('--script', help='path to startup script')
    parser.add_argument('--config', help='path to configuration JSON')
    args = parser.parse_args(argv)
    try:
        config = {}
        if args.config:
            with open(args.config, encoding='utf-8') as stream:
                config = json.load(stream)
            if not isinstance(config, dict):
                raise ValueError('config must be a JSON object')
        vfs_path = args.vfs or config.get('vfs', 'vfs/sample.json')
        script_path = args.script if args.script is not None else config.get('script')
        if not isinstance(vfs_path, str) or (script_path is not None and not isinstance(script_path, str)):
            raise ValueError('config values must be strings')
        print(f'Config: {args.config or "(none)"}')
        print(f'VFS: {vfs_path}')
        print(f'Startup script: {script_path or "(none)"}')
        shell = Emulator()
        if script_path and not run_script(shell, script_path):
            return 1
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
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f'Configuration/VFS/script error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
