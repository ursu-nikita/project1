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


def normalize(path, current):
    """Normalize an absolute or relative virtual path without disk access."""
    parts = [] if path.startswith('/') else current.strip('/').split('/')
    for part in path.split('/'):
        if part in ('', '.'):
            continue
        if part == '..':
            if parts:
                parts.pop()
        else:
            parts.append(part)
    return '/' + '/'.join(p for p in parts if p)


def load_vfs(path):
    """Read and validate a JSON VFS containing directories and files."""
    with open(path, 'rb') as stream:
        raw = stream.read()
    document = json.loads(raw.decode('utf-8'))
    if not isinstance(document, dict) or not isinstance(document.get('name'), str):
        raise ValueError('VFS must have a name')
    root = document.get('root')
    validate_node(root)
    if root['type'] != 'dir':
        raise ValueError('VFS root must be a directory')
    return document, hashlib.sha256(raw).hexdigest()


def validate_node(node):
    """Recursively validate the VFS JSON schema."""
    if not isinstance(node, dict) or node.get('type') not in ('dir', 'file'):
        raise ValueError('invalid VFS node')
    if not isinstance(node.get('mode', '755'), str):
        raise ValueError('invalid VFS mode')
    if node['type'] == 'dir':
        children = node.get('children')
        if not isinstance(children, dict):
            raise ValueError('directory must contain children object')
        for name, child in children.items():
            if not name or '/' in name or name in ('.', '..'):
                raise ValueError('invalid VFS entry name')
            validate_node(child)
    else:
        encoded = node.get('content_b64')
        if not isinstance(encoded, str):
            raise ValueError('file must contain content_b64')
        base64.b64decode(encoded, validate=True)


class Emulator:
    """A simple shell operating exclusively on an in-memory JSON tree."""

    def __init__(self, document, checksum):
        self.document = document
        self.checksum = checksum
        self.cwd = '/'
        self.running = True

    def node(self, path):
        """Find a node in the in-memory filesystem."""
        absolute = normalize(path, self.cwd)
        item = self.document['root']
        for name in [part for part in absolute.split('/') if part]:
            if item['type'] != 'dir' or name not in item['children']:
                raise ShellError(f'No such file or directory: {path}')
            item = item['children'][name]
        return item

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
        if command == 'vfs-info':
            self.require(params, 0, 'vfs-info')
            return f"Name: {self.document['name']}\nSHA-256: {self.checksum}"
        if command == 'whoami':
            self.require(params, 0, 'whoami')
            return getpass.getuser()
        if command == 'clear':
            self.require(params, 0, 'clear')
            return '\033[2J\033[H'
        if command == 'ls':
            self.require_range(params, 0, 1, 'ls [path]')
            target = self.node(params[0] if params else '.')
            if target['type'] == 'dir':
                return '\n'.join(sorted(target['children']))
            return PurePosixPath(params[0]).name
        if command == 'cd':
            self.require_range(params, 0, 1, 'cd [path]')
            path = params[0] if params else '/'
            target = self.node(path)
            if target['type'] != 'dir':
                raise ShellError(f'Not a directory: {path}')
            self.cwd = normalize(path, self.cwd)
            return ''
        if command == 'tac':
            self.require(params, 1, 'tac <file>')
            target = self.node(params[0])
            if target['type'] != 'file':
                raise ShellError('tac expects a file')
            data = base64.b64decode(target['content_b64'])
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError as error:
                raise ShellError('tac only supports UTF-8 text') from error
            return '\n'.join(reversed(content.splitlines()))
        if command == 'chmod':
            self.require(params, 2, 'chmod <octal-mode> <path>')
            mode, path = params
            if len(mode) not in (3, 4) or any(ch not in '01234567' for ch in mode):
                raise ShellError('chmod: mode must be 3 or 4 octal digits')
            self.node(path)['mode'] = mode
            return ''
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
        doc, checksum = load_vfs(vfs_path)
        shell = Emulator(doc, checksum)
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
