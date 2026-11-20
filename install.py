#!/usr/bin/env python3
"""Project-only jstack installer. Python 3.11+, no third-party dependencies."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile

import upstream

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


def managed_path(relative, kind, seo=False):
    """Only installer-owned namespaces may be claimed by a saved manifest."""
    if seo:
        return ((kind == 'file' and relative.startswith(upstream.SEO_DEST + '/')) or
                (kind == 'link' and bool(re.fullmatch(
                    r'\.(?:agents|claude|cursor|gemini|opencode)/skills/seo(?:-[a-z0-9]+)*', relative))))
    if relative in {'.agents/jstack/.gitignore', '.agents/jstack/LICENSE', '.agents/jstack/rules.md'}:
        return kind == 'file'
    name = r'[a-z0-9]+(?:-[a-z0-9]+)*'
    if kind == 'file' and re.fullmatch(r'\.agents/skills/' + name + r'/.+', relative):
        return True
    providers = r'\.(?:claude|cursor|gemini|opencode)'
    if kind == 'link' and re.fullmatch(providers + r'/skills/' + name, relative):
        return True
    return kind == 'file' and bool(re.fullmatch(
        r'\.(?:cursor|opencode)/commands/' + name + r'\.md|\.gemini/commands/' + name + r'\.toml', relative))


def load_manifest(root):
    path = safe_path(root, MANIFEST, True)
    if not path.exists():
        return {'files': {}}
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or manifest.get('schema') != 1 or not isinstance(manifest.get('files'), dict):
        raise ValueError('Invalid jstack manifest: expected schema 1 and a files object.')
    validate_records(root, manifest['files'])
    validate_records(root, manifest.get('seo_files', {}), seo=True)
    return manifest


def validate_records(root, files, seo=False):
    if not isinstance(files, dict):
        raise ValueError('Invalid imported files manifest.')
    for relative, entry in files.items():
        path = safe_path(root, relative)
        if seo and relative.startswith(upstream.SEO_DEST + '/') and path.parent.resolve() != path.parent:
            raise ValueError(f'Unsafe SEO destination parent symlink: {relative}')
        if Path(relative).as_posix() != relative or not managed_path(relative, entry.get('kind') if isinstance(entry, dict) else None, seo):
            raise ValueError(f'Invalid unowned manifest path: {relative}')
        if not isinstance(entry, dict):
            raise ValueError(f'Invalid manifest entry: {relative}')
        if entry.get('kind') == 'file':
            valid = (isinstance(entry.get('sha256'), str) and
                     re.fullmatch(r'[0-9a-f]{64}', entry['sha256']) and
                     isinstance(entry.get('executable'), bool))
        else:
            valid = entry.get('kind') == 'link' and isinstance(entry.get('target'), str) and bool(entry['target'])
        if not valid:
            raise ValueError(f'Invalid manifest entry: {relative}')


def validate_catalog():
    """Validate our intentionally small frontmatter dialect without a YAML runtime."""
    catalog = SOURCE / 'skills'
    # Never dereference source links: a release must be self-contained.
    if catalog.is_symlink():
        raise ValueError('Unsafe source symlink: skills')
    for source in catalog.rglob('*'):
        if source.is_symlink():
            raise ValueError(f'Unsafe source symlink: {source.relative_to(SOURCE)}')
    skills = sorted(catalog.iterdir())
    if not skills:
        raise ValueError('Skill catalog is empty.')
    for skill in skills:
        text = (skill / 'SKILL.md').read_text(encoding='utf-8')
        parts = text.split('---\n', 2)
        if len(parts) != 3 or parts[0] or len(text.splitlines()) > 60:
            raise ValueError(f'{skill.name}: invalid frontmatter or exceeds 60 lines')
        fields = {}
        for line in parts[1].splitlines():
            key, separator, value = line.partition(': ')
            if not separator or key in fields or key not in {'name', 'description', 'disable-model-invocation'}:
                raise ValueError(f'{skill.name}: unsupported or duplicate frontmatter field')
            fields[key] = value
        if fields.get('name') != skill.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill.name):
            raise ValueError(f'{skill.name}: name must match its folder')
        description = json.loads(fields.get('description', 'null'))
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f'{skill.name}: description must be a JSON-quoted string')
        # Agent Skills specification limits, so every client accepts the catalog.
        if len(skill.name) > 64 or len(description) > 1024:
            raise ValueError(f'{skill.name}: name exceeds 64 or description exceeds 1024 characters')
        typed = skill.name in {'push', 'update-skills'}
        if fields.get('disable-model-invocation') != ('true' if typed else None):
            raise ValueError(f'{skill.name}: incorrect invocation policy')
        policy = skill / 'agents/openai.yaml'
        explicit = policy.is_file() and bool(re.search(r'^  allow_implicit_invocation: false$', policy.read_text(encoding='utf-8'), re.M))
        if explicit != typed:
            raise ValueError(f'{skill.name}: inconsistent Codex invocation policy')
        if 'Read `.agents/jstack/rules.md` first' not in parts[2]:
            raise ValueError(f'{skill.name}: missing shared rules reference')
        for matches in re.findall(r'`(references/[^`]+)`|\]\((references/[^)]+)\)', parts[2]):
            reference = skill / next(value for value in matches if value)
            if not reference.resolve().is_relative_to(skill.resolve()) or not reference.is_file():
                raise ValueError(f'{skill.name}: missing or unsafe reference {reference.name}')
    return skills


def validate_release():
    # Shared release inputs must be self-contained, just like skill sources.
    for relative in ('LICENSE', 'VERSION', 'shared/rules.md'):
        source = SOURCE / relative
        for component in (source, *source.parents):
            if component == SOURCE:
                break
            if component.is_symlink():
                raise ValueError(f'Unsafe source symlink: {component.relative_to(SOURCE)}')
        if not source.is_file():
            raise ValueError(f'Missing source file: {relative}')
    return validate_catalog()


def plan(root, imported=()):
    skills = validate_release()
    desired = {}
    for source in sorted((SOURCE / 'skills').rglob('*')):
        if source.is_file() and '__pycache__' not in source.parts and source.suffix != '.pyc':
            relative = '.agents/skills/' + source.relative_to(SOURCE / 'skills').as_posix()
            desired[relative] = file_entry(source.read_bytes(), bool(source.stat().st_mode & 0o111))
    names = {skill.name for skill in skills}
    if imported:
        for relative in list(desired):
            if Path(relative).parts[2] in upstream.MATT_SKILLS:
                del desired[relative]
        for relative, data, executable in imported:
            desired['.agents/skills/' + relative] = file_entry(data, executable)
        names.update(upstream.MATT_SKILLS)
    desired['.agents/jstack/.gitignore'] = file_entry(b'runtime/\nreports/\n')
    desired['.agents/jstack/LICENSE'] = file_entry((SOURCE / 'LICENSE').read_bytes())
    # Every skill points here, so shared rules live in one place.
    desired['.agents/jstack/rules.md'] = file_entry((SOURCE / 'shared/rules.md').read_bytes())
    for name in sorted(names):
        canonical = root / '.agents/skills' / name
        for provider in PROVIDERS:
            alias = safe_path(root, f'{provider}/skills/{name}')
            safe_path(root, f'{provider}/skills/{name}', True)
            # Existing whole-directory discovery links already expose this skill.
            if alias.parent.resolve() == canonical.parent.resolve():
                continue
            target = os.path.relpath(canonical, alias.parent.resolve())
            desired[f'{provider}/skills/{name}'] = {'kind': 'link', 'target': target}
        # Adapters load the canonical skill so skill-local references have one base.
        prompt = (f'Read `.agents/skills/{name}/SKILL.md` and follow it for this request.\n'
                  'Resolve its relative references from that skill folder.\n'
                  'Apply `.agents/jstack/rules.md`.\n')
        desired[f'.cursor/commands/{name}.md'] = file_entry((prompt + '\nArguments: $ARGUMENTS\n').encode())
        gemini_prompt = prompt + "\nArguments: {{args}}\n"
        toml = f'description = {json.dumps("jstack " + name)}\nprompt = {json.dumps(gemini_prompt, ensure_ascii=False)}\n'
        desired[f'.gemini/commands/{name}.toml'] = file_entry(toml.encode())
        desired[f'.opencode/commands/{name}.md'] = file_entry((prompt + '\nArguments: $ARGUMENTS\n').encode())
    return desired


def seo_plan(root, source, commit, legacy=False):
    files = {path: file_entry(data, executable)
             for path, data, executable in upstream.seo_files(source, legacy)}
    if not legacy:
        ignore = f'{upstream.SEO_DEST}/.gitignore'
        if ignore in files:
            paths = [path.removeprefix(upstream.SEO_DEST + '/') for path in files]
            exceptions = upstream.ignored_sources(source, paths)
            if exceptions:
                entry = files[ignore]
                files[ignore] = file_entry(entry['data'] + exceptions, entry['executable'])
    skill_pattern = re.escape(upstream.SEO_DEST) + r'/skills/(seo(?:-[a-z0-9]+)*)/SKILL\.md'
    skills = {match[1] for path in files if (match := re.fullmatch(skill_pattern, path))}
    if 'seo' not in skills or f'{upstream.SEO_DEST}/LICENSE' not in files:
        raise ValueError('Upstream Claude SEO is missing its entrypoint or license.')
    aliases = upstream.seo_aliases(root, skills, PROVIDERS, safe_path)
    for relative, target in aliases.items():
        files[relative] = {'kind': 'link', 'target': target}
    files[f'{upstream.SEO_DEST}/JSTACK-INSTALL.json'] = file_entry(
        upstream.seo_metadata(commit, list(aliases)))
    validate_records(root, files, seo=True)
    return files


def refresh_seo(root, previous):
    metadata = safe_path(root, f'{upstream.SEO_DEST}/JSTACK-INSTALL.json', True)
    if not metadata.is_file():
        if previous:
            raise ValueError('Claude SEO installation metadata is missing.')
        print('Claude SEO refresh skipped: no jstack-managed installation found.')
        return {}, {}, None
    old = previous
    if not old:
        # Rebuild the exact original payload before claiming a legacy install.
        info = json.loads(metadata.read_text(encoding='utf-8'))
        commit = info.get('commit') if isinstance(info, dict) else None
        if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise ValueError('Invalid Claude SEO installation commit.')
        with upstream.checkout(upstream.SEO_REPO, commit) as (source, revision):
            legacy = seo_plan(root, source, revision, legacy=revision == upstream.SEO_PIN)
        old = {path: record(entry) for path, entry in legacy.items()}
    with upstream.checkout(upstream.SEO_REPO) as (source, revision):
        desired = seo_plan(root, source, revision)
    print(f'Claude SEO upstream commit: {revision}')
    return old, desired, revision


def validate_destinations(root, desired):
    # Refuse two lexical paths that resolve onto the same file via custom links.
    resolved = {}
    for relative in desired:
        path = safe_path(root, relative)
        actual = path.parent.resolve() / path.name
        if actual in resolved:
            raise ValueError(f'Aliased destinations collide: {relative}, {resolved[actual]}')
        resolved[actual] = relative
    for actual, relative in resolved.items():
        for parent in actual.parents:
            if parent in resolved:
                raise ValueError(f'Overlapping destinations: {relative}, {resolved[parent]}')


def inspect(root, old, desired):
    conflicts = []
    for relative in sorted(set(old) | set(desired)):
        path = safe_path(root, relative)
        for parent in path.parents:
            if parent == root:
                break
            if parent.exists() and not parent.is_dir():
                conflicts.append(f'{relative}: parent is not a directory: {parent.relative_to(root)}')
                break
        current = state(path)
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
    seo_old = previous.get('seo_files', {})
    seo_desired = {}
    revisions = previous.get('upstream', {})
    config = safe_path(root, '.agents/jstack/project.json', True)
    if config.exists() and not config.is_file():
        raise ValueError('project.json must be a file.')
    if config.exists():
        if not isinstance(json.loads(config.read_text(encoding='utf-8')), dict):
            raise ValueError('project.json must contain a JSON object.')
    if args.action == 'check':
        problems = []
        if not old:
            problems.append('No jstack installation manifest found.')
        for relative, expected in (old | seo_old).items():
            if state(safe_path(root, relative)) != expected:
                problems.append(f'{relative}: missing or modified')
            if expected['kind'] == 'link' and not safe_path(root, relative, True).exists():
                problems.append(f'{relative}: broken link')
        print(json.dumps({'version': previous.get('version'), 'managed_paths': len(old) + len(seo_old), 'ok': not problems, 'problems': problems}, indent=2))
        return 1 if problems else 0
    imported = []
    if args.action == 'install' and (getattr(args, 'refresh_imports', False) or revisions):
        with upstream.checkout(upstream.MATT_REPO) as (source, revision):
            imported = list(upstream.matt_files(source))
        print(f'Matt Pocock skills upstream commit: {revision}')
        revisions = {'mattpocock/skills': revision}
        seo_old, seo_desired, seo_revision = refresh_seo(root, seo_old)
        if seo_revision:
            revisions['AgriciDaniel/claude-seo'] = seo_revision
    desired = plan(root, imported) if args.action == 'install' else {}
    if seo_desired:
        if set(old | desired) & set(seo_old | seo_desired):
            raise ValueError('Claude SEO overlaps the jstack catalog.')
        old = old | seo_old
    targets = desired | seo_desired
    validate_destinations(root, old.keys() | targets.keys())
    # Metadata is project-owned, and cannot alias content this operation manages.
    for relative in (MANIFEST, '.agents/jstack/project.json'):
        metadata = safe_path(root, relative, True).resolve()
        for managed in set(old) | set(targets):
            path = safe_path(root, managed)
            actual = path.parent.resolve() / path.name
            if metadata == actual or metadata in actual.parents or actual in metadata.parents:
                raise ValueError(f'Installer metadata overlaps managed content: {relative}, {managed}')
    conflicts = inspect(root, old, targets)
    if conflicts:
        raise ValueError('No files changed.\n' + '\n'.join(conflicts))
    changes = []
    for relative in sorted(set(old) | set(targets)):
        current = state(safe_path(root, relative))
        target = record(targets[relative]) if relative in targets else None
        if current != target:
            changes.append((relative, 'remove' if target is None else 'write'))
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
            entry = targets[relative]
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
            manifest = {'schema': 1, 'version': (SOURCE / 'VERSION').read_text(encoding='utf-8').strip(),
                        'source': 'https://github.com/joeconstanti/jstack',
                        'files': {k: record(v) for k, v in desired.items()}}
            if revisions:
                manifest['upstream'] = revisions
                manifest['seo_files'] = {k: record(v) for k, v in seo_desired.items()}
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
    parser.add_argument('action', choices=['install', 'check', 'uninstall', 'validate'])
    parser.add_argument('--project', help='Git repository root; never a global skills directory')
    parser.add_argument('--refresh-imports', action='store_true', help='Fetch current imported skills during install')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.action != 'validate' and not args.project:
        parser.error('--project is required for install, check and uninstall')
    if args.refresh_imports and args.action != 'install':
        parser.error('--refresh-imports requires install')
    try:
        if args.action == 'validate':
            skills = validate_release()
            print(json.dumps({'ok': True, 'skills': [skill.name for skill in skills]}, indent=2))
            return 0
        return run(args)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
