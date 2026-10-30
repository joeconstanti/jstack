#!/usr/bin/env python3
"""Install pinned Claude SEO instructions locally, without installing its runtime."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from install import project_root, safe_path

REPO = 'https://github.com/AgriciDaniel/claude-seo.git'
COMMIT = '6be93f45064ffbadced572b5d5c95f55fd263af0'
DEST = '.agents/skills/claude-seo'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = project_root(args.project)
    # Existing flattened or repo-layout installations belong to the project.
    for relative in ['.agents/skills/seo/SKILL.md', DEST + '/skills/seo/SKILL.md']:
        if safe_path(root, relative, True).is_file():
            print('Existing SEO installation retained; no files changed.')
            return 0
    destination = safe_path(root, DEST, True)
    if destination.exists() or destination.is_symlink():
        raise ValueError('SEO destination already exists; inspect it before installing.')
    with tempfile.TemporaryDirectory(prefix='jstack-seo-') as temp:
        checkout = Path(temp) / 'source'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout', REPO, str(checkout)], check=True)
        subprocess.run(['git', '-C', str(checkout), 'checkout', '--quiet', '--detach', COMMIT], check=True)
        actual = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != COMMIT:
            raise ValueError('Pinned SEO commit verification failed.')
        aliases = {}
        for skill in sorted((checkout / 'skills').iterdir()):
            if not (skill / 'SKILL.md').is_file():
                continue
            canonical = destination / 'skills' / skill.name
            for provider in ['.agents', '.claude', '.cursor', '.gemini', '.opencode']:
                relative = f'{provider}/skills/{skill.name}'
                alias = safe_path(root, relative)
                actual_path = alias.parent.resolve() / alias.name
                if actual_path in aliases:
                    continue
                if alias.exists() or alias.is_symlink():
                    raise ValueError(f'Unmanaged SEO collision: {relative}; no files changed.')
                aliases[actual_path] = (alias, os.path.relpath(canonical, alias.parent.resolve()))
        print(f'Install Claude SEO {COMMIT} under {DEST}; {len(aliases)} discovery links. Runtime setup is separate.')
        if args.dry_run:
            return 0
        stage = safe_path(root, DEST + '.jstack-stage', True)
        if stage.exists():
            raise ValueError('SEO staging directory exists; inspect it before retrying.')
        created = []
        installed = False
        try:
            stage.mkdir(parents=True)
            for name in ['skills', 'scripts', 'schema', 'data', 'pdf', 'agents']:
                source = checkout / name
                if source.is_dir():
                    shutil.copytree(source, stage / name)
            for name in ['LICENSE', 'README.md', 'requirements.txt']:
                shutil.copy2(checkout / name, stage / name)
            shutil.copy2(checkout / '.claude-plugin/plugin.json', stage / 'runtime-plugin.json')
            shutil.copy2(checkout / '.gitignore', stage / '.gitignore')
            # Adapt plugin-root tokens to a portable repository-relative path.
            for doc in stage.rglob('*.md'):
                text = doc.read_text()
                doc.write_text(text.replace('${CLAUDE_PLUGIN_ROOT}', DEST))
            (stage / 'JSTACK-INSTALL.json').write_text(json.dumps({
                'source': REPO, 'commit': COMMIT, 'license': 'MIT',
                'modification': 'Markdown plugin-root tokens replaced with project-relative path.',
                'runtime_setup': False,
                'aliases': [str(alias.relative_to(root)) for alias, _ in aliases.values()]
            }, indent=2) + '\n')
            stage.rename(destination)
            installed = True
            for alias, target in aliases.values():
                alias.parent.mkdir(parents=True, exist_ok=True)
                alias.symlink_to(target, target_is_directory=True)
                created.append(alias)
        except Exception:
            for alias in reversed(created):
                alias.unlink()
            if installed:
                shutil.rmtree(destination)
            elif stage.exists():
                shutil.rmtree(stage)
            raise
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
