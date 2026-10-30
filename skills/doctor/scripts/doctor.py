#!/usr/bin/env python3
"""Read-only project and jstack installation diagnostics."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def diagnose(root):
    result = {'tools': {name: bool(shutil.which(name)) for name in ['git', 'python3', 'node', 'npm', 'gh']},
              'problems': [], 'unverified': ['agent reload/discovery', 'hook activation', 'SEO runtime dependencies',
                                               'authenticated accounts', 'rendered app and deployment']}
    manifest_path = root / '.agents/jstack/manifest.json'
    manifest_files = {}
    if not manifest_path.is_file():
        result['problems'].append('jstack manifest missing')
    else:
        manifest = json.loads(manifest_path.read_text())
        manifest_files = manifest.get('files', {})
        result['version'] = manifest.get('version')
        result['managed_paths'] = len(manifest.get('files', {}))
        for relative, expected in manifest.get('files', {}).items():
            path = root / relative
            if not path.resolve().is_relative_to(root) or Path(relative).is_absolute() or '..' in Path(relative).parts:
                result['problems'].append(f'unsafe managed path: {relative}')
                continue
            if expected['kind'] == 'link':
                good = path.is_symlink() and os.readlink(path) == expected['target'] and path.exists()
            else:
                good = path.is_file() and not path.is_symlink()
                if good:
                    good = (hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'] and
                            bool(path.stat().st_mode & 0o111) == expected['executable'])
            if not good:
                result['problems'].append(f'missing or modified: {relative}')
    config = root / '.agents/jstack/project.json'
    result['project_config'] = json.loads(config.read_text()) if config.is_file() else {}
    package = root / 'package.json'
    result['package_scripts'] = json.loads(package.read_text()).get('scripts', {}) if package.is_file() else {}
    result['lockfiles'] = [name for name in ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'bun.lock', 'uv.lock', 'poetry.lock', 'Cargo.lock', 'go.sum'] if (root / name).exists()]
    result['seo'] = next((name for name in ['.agents/skills/seo/SKILL.md', '.agents/skills/claude-seo/skills/seo/SKILL.md'] if (root / name).is_file()), None)
    result['impeccable'] = (root / '.agents/skills/impeccable/SKILL.md').is_file()
    result['impeccable_launcher'] = (root / '.agents/skills/impeccable/scripts/impeccable').is_file()
    # Installed skill names come from the manifest, so new releases need no edit here.
    skills = sorted({Path(p).parts[2] for p in manifest_files if p.startswith('.agents/skills/') and p.endswith('/SKILL.md')})
    result['discovery_files'] = {}
    for provider in ['.agents', '.claude', '.cursor', '.gemini', '.opencode']:
        result['discovery_files'][provider] = bool(skills) and all((root / provider / 'skills' / name / 'SKILL.md').is_file() for name in skills)
    if not result['seo']:
        result['problems'].append('audit dependency missing: Claude SEO')
    if not result['impeccable'] or not result['impeccable_launcher']:
        result['problems'].append('edit dependency missing: Impeccable')
    if not all(result['discovery_files'].values()):
        result['problems'].append('one or more provider skill entrypoints missing')
    git = subprocess.run(['git', '-C', str(root), 'status', '--porcelain'], capture_output=True, text=True)
    result['dirty_paths'] = len(git.stdout.splitlines()) if git.returncode == 0 else None
    result['ok'] = not result['problems']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default='.')
    args = parser.parse_args()
    try:
        report = diagnose(Path(args.project).expanduser().resolve(strict=True))
        print(json.dumps(report, indent=2))
        raise SystemExit(0 if report['ok'] else 1)
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        raise SystemExit(1)
