#!/usr/bin/env python3
"""Project-only jstack installer. Python 3.11+, no third-party dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent
MANIFEST = '.agents/jstack/manifest.json'
PROVIDERS = ('.claude', '.cursor', '.gemini', '.opencode')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def project_root(value):
    root = Path(value).expanduser().resolve(strict=True)
    if root == Path.home() or root == Path(root.anchor):
        raise ValueError('A project repository root is required; home/global installation is unsupported.')
    result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if result.returncode or Path(result.stdout.strip()).resolve() != root:
        raise ValueError('--project must name the Git repository root.')
    return root


def safe_path(root, relative, follow_leaf=False):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError(f'Unsafe managed path: {relative}')
    path = root / rel
    resolved = path.resolve() if follow_leaf else path.parent.resolve() / path.name
    if not resolved.is_relative_to(root):
        raise ValueError(f'Path escapes the project (possibly a global symlink): {relative}')
    return path


def state(path):
    if path.is_symlink():
        return {'kind': 'link', 'target': os.readlink(path)}
    if path.is_file():
        return {'kind': 'file', 'sha256': digest(path.read_bytes()), 'executable': bool(path.stat().st_mode & 0o111)}
    if path.exists():
        return {'kind': 'directory'}
    return None


def file_entry(data, executable=False):
    return {'kind': 'file', 'sha256': digest(data), 'executable': executable, 'data': data}


def record(entry):
    return {k: v for k, v in entry.items() if k != 'data'}


def load_manifest(root):
    path = safe_path(root, MANIFEST, True)
    return json.loads(path.read_text()) if path.exists() else {'files': {}}


def plan(root):
    desired = {}
    for source in sorted((SOURCE / 'skills').rglob('*')):
        if source.is_file() and '__pycache__' not in source.parts and source.suffix != '.pyc':
            relative = '.agents/skills/' + source.relative_to(SOURCE / 'skills').as_posix()
            desired[relative] = file_entry(source.read_bytes(), bool(source.stat().st_mode & 0o111))
    desired['.agents/jstack/.gitignore'] = file_entry(b'runtime/\nreports/\n')
    desired['.agents/jstack/LICENSE'] = file_entry((SOURCE / 'LICENSE').read_bytes())
    # Every skill points here, so shared rules live in one place.
    desired['.agents/jstack/rules.md'] = file_entry((SOURCE / 'shared/rules.md').read_bytes())
    for skill in sorted((SOURCE / 'skills').iterdir()):
        if not (skill / 'SKILL.md').is_file():
            continue
        canonical = root / '.agents/skills' / skill.name
        for provider in PROVIDERS:
            alias = safe_path(root, f'{provider}/skills/{skill.name}')
            safe_path(root, f'{provider}/skills/{skill.name}', True)
            # Existing whole-directory discovery links already expose this skill.
            if alias.parent.resolve() == canonical.parent.resolve():
                continue
            target = os.path.relpath(canonical, alias.parent.resolve())
            desired[f'{provider}/skills/{skill.name}'] = {'kind': 'link', 'target': target}
        body = skill.joinpath('SKILL.md').read_text(encoding='utf-8').split('---', 2)[2].strip()
        # Cursor commands and Gemini TOML give native short slash aliases as well
        # as ordinary SKILL.md discovery. Claude discovers the skill name directly.
        desired[f'.cursor/commands/{skill.name}.md'] = file_entry((body + '\n\nArguments: $ARGUMENTS\n').encode())
        prompt = body + '\n\nArguments: {{args}}\n'
        # TOML has no surrogate-pair escapes, so keep non-ASCII text as UTF-8.
        toml = f'description = {json.dumps("jstack " + skill.name)}\nprompt = {json.dumps(prompt, ensure_ascii=False)}\n'
        desired[f'.gemini/commands/{skill.name}.toml'] = file_entry(toml.encode())
        desired[f'.opencode/commands/{skill.name}.md'] = file_entry((body + '\n\nArguments: $ARGUMENTS\n').encode())
    # Refuse two lexical paths that resolve onto the same file via custom links.
    resolved = {}
    for relative in desired:
        path = safe_path(root, relative)
        actual = path.parent.resolve() / path.name
        if actual in resolved:
            raise ValueError(f'Aliased destinations collide: {relative}, {resolved[actual]}')
        resolved[actual] = relative
    return desired


def inspect(root, old, desired):
    conflicts = []
    for relative in sorted(set(old) | set(desired)):
        current = state(safe_path(root, relative))
        expected = old.get(relative)
        if expected is not None:
            if current != expected:
                conflicts.append(f'{relative}: managed file changed or missing')
        elif current is not None:
            conflicts.append(f'{relative}: unmanaged collision')
    return conflicts


def atomic_write(path, data, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.jstack-', dir=path.parent)
    temp = Path(temporary)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        temp.chmod(0o755 if executable else 0o644)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)



def run(args):
    root = project_root(args.project)
    previous = load_manifest(root)
    old = previous['files']
    if args.action == 'check':
        problems = []
        if not old:
            problems.append('No jstack installation manifest found.')
        for relative, expected in old.items():
            if state(safe_path(root, relative)) != expected:
                problems.append(f'{relative}: missing or modified')
            if expected['kind'] == 'link' and not safe_path(root, relative, True).exists():
                problems.append(f'{relative}: broken link')
        print(json.dumps({'version': previous.get('version'), 'managed_paths': len(old), 'ok': not problems, 'problems': problems}, indent=2))
        return 1 if problems else 0
    desired = plan(root) if args.action == 'install' else {}
    conflicts = inspect(root, old, desired)
    if conflicts:
        raise ValueError('No files changed.\n' + '\n'.join(conflicts))
    changes = []
    for relative in sorted(set(old) | set(desired)):
        current = state(safe_path(root, relative))
        target = record(desired[relative]) if relative in desired else None
        if current != target:
            changes.append((relative, 'remove' if target is None else 'write'))
    config = safe_path(root, '.agents/jstack/project.json', True)
    if config.exists() and not config.is_file():
        raise ValueError('project.json must be a file.')
    if config.exists():
        json.loads(config.read_text())
    for relative, action in changes:
        print(f'{action}: {relative}')
    print(f'{args.action}: {len(changes)} changes' + (' (dry run; no files changed)' if args.dry_run else ''))
    if args.dry_run:
        return 0
    # Keep snapshots to roll back if any filesystem operation fails.
    snapshots = {}
    touched = []
    manifest_path = safe_path(root, MANIFEST, True)
    old_manifest = manifest_path.read_bytes() if manifest_path.exists() else None
    config_created = False
    try:
        for relative, action in changes:
            path = safe_path(root, relative)
            snapshots[relative] = (state(path), path.read_bytes() if path.is_file() and not path.is_symlink() else None)
            touched.append(relative)
            if action == 'remove':
                path.unlink()
                continue
            entry = desired[relative]
            path.parent.mkdir(parents=True, exist_ok=True)
            if entry['kind'] == 'link':
                if path.exists() or path.is_symlink():
                    path.unlink()
                path.symlink_to(entry['target'], target_is_directory=True)
            else:
                atomic_write(path, entry['data'], entry['executable'])
        if args.action == 'install':
            if not config.exists():
                atomic_write(config, b'{\n  "remote": "origin",\n  "main_branch": "main"\n}\n')
                config_created = True
            manifest = {'schema': 1, 'version': (SOURCE / 'VERSION').read_text().strip(),
                        'source': 'https://github.com/joeconstanti/jstack',
                        'files': {k: record(v) for k, v in desired.items()}}
            atomic_write(manifest_path, (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode())
        else:
            manifest_path.unlink(missing_ok=True)
    except Exception:
        for relative in reversed(touched):
            path = safe_path(root, relative)
            before, data = snapshots[relative]
            if before and before['kind'] == 'file':
                atomic_write(path, data, before['executable'])
            else:
                if path.is_file() or path.is_symlink():
                    path.unlink()
                if before:
                    path.symlink_to(before['target'], target_is_directory=True)
        if config_created:
            config.unlink(missing_ok=True)
        if old_manifest is not None:
            atomic_write(manifest_path, old_manifest)
        else:
            manifest_path.unlink(missing_ok=True)
        raise
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'check', 'uninstall'])
    parser.add_argument('--project', required=True, help='Git repository root; never a global skills directory')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        return run(args)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
