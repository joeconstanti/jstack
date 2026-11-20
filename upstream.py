"""Fetch and stage project-local skills without running upstream code."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import tempfile

MATT_REPO = 'https://github.com/mattpocock/skills.git'
MATT_SKILLS = {
    'grill': 'productivity/grill-me',
    'grilling': 'productivity/grilling',
    'grill-with-docs': 'engineering/grill-with-docs',
    'domain-modeling': 'engineering/domain-modeling',
}
SEO_REPO = 'https://github.com/AgriciDaniel/claude-seo.git'
SEO_PIN = '6be93f45064ffbadced572b5d5c95f55fd263af0'
SEO_DEST = '.agents/skills/claude-seo'
SEO_DIRS = ('skills', 'scripts', 'schema', 'data', 'pdf', 'agents')
SEO_FILES = ('LICENSE', 'README.md', 'requirements.txt', '.gitignore')


@contextmanager
def checkout(repo, revision=None):
    with tempfile.TemporaryDirectory(prefix='jstack-upstream-') as directory:
        source = Path(directory) / 'source'
        if revision is None:
            subprocess.run(['git', 'clone', '--quiet', '--depth', '1', repo, str(source)], check=True)
        else:
            subprocess.run(['git', 'init', '--quiet', str(source)], check=True)
            subprocess.run(['git', '-C', str(source), 'fetch', '--quiet', '--depth', '1', repo, revision], check=True)
            subprocess.run(['git', '-C', str(source), 'checkout', '--quiet', '--detach', 'FETCH_HEAD'], check=True)
        actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        if revision and actual != revision:
            raise ValueError(f'Upstream commit verification failed for {repo}')
        yield source, actual


def source_files(path):
    for item in (path, *sorted(path.rglob('*'))):
        if item.is_symlink():
            raise ValueError(f'Unsafe upstream source symlink: {item}')
        if item.is_file():
            yield item


def matt_files(source):
    if (source / 'skills').is_symlink():
        raise ValueError('Unsafe Matt Pocock skills symlink')
    license_file = source / 'LICENSE'
    if license_file.is_symlink() or not license_file.is_file():
        raise ValueError('Missing or unsafe Matt Pocock skills license')
    for name, upstream in MATT_SKILLS.items():
        folder = source / 'skills' / upstream
        if folder.parent.is_symlink() or not (folder / 'SKILL.md').is_file():
            raise ValueError(f'Missing or unsafe upstream skill: {upstream}')
        for item in source_files(folder):
            data = item.read_bytes()
            if name == 'grill' and item.name == 'SKILL.md':
                header, body = data.split(b'\n---\n', 1)
                if b'\nname: grill-me\n' not in header + b'\n':
                    raise ValueError('Upstream grill-me skill has an unexpected name')
                header = header.replace(b'\nname: grill-me', b'\nname: grill')
                data = header + b'\n---\n' + body
            yield f'{name}/{item.relative_to(folder).as_posix()}', data, bool(item.stat().st_mode & 0o111)
        yield f'{name}/LICENSE', license_file.read_bytes(), False


def seo_files(source, legacy=False):
    directories = SEO_DIRS if legacy else (*SEO_DIRS, 'assets', 'extensions')
    for name in (*directories, *SEO_FILES):
        path = source / name
        for item in source_files(path):
            relative = item.relative_to(source).as_posix()
            data = item.read_bytes()
            if relative.endswith('.md'):
                data = data.decode('utf-8').replace('${CLAUDE_PLUGIN_ROOT}', SEO_DEST).encode()
            yield f'{SEO_DEST}/{relative}', data, bool(item.stat().st_mode & 0o111)
    if (source / '.claude-plugin').is_symlink():
        raise ValueError('Unsafe Claude SEO plugin directory symlink')
    plugin = source / '.claude-plugin/plugin.json'
    if plugin.is_symlink() or not plugin.is_file():
        raise ValueError('Missing or unsafe Claude SEO plugin manifest')
    yield f'{SEO_DEST}/runtime-plugin.json', plugin.read_bytes(), bool(plugin.stat().st_mode & 0o111)


def seo_metadata(commit, aliases):
    return json.dumps({
        'source': SEO_REPO, 'commit': commit, 'license': 'MIT',
        'modification': 'Markdown plugin-root tokens replaced with project-relative path.',
        'runtime_setup': False,
        'aliases': aliases,
    }, indent=2).encode() + b'\n'


def seo_aliases(root, skills, providers, safe_path):
    aliases = {}
    for name in sorted(skills):
        canonical = root / SEO_DEST / 'skills' / name
        for provider in ('.agents', *providers):
            relative = f'{provider}/skills/{name}'
            alias = safe_path(root, relative)
            actual = alias.parent.resolve() / alias.name
            aliases.setdefault(actual, (relative, os.path.relpath(canonical, actual.parent)))
    return dict(aliases.values())

def ignored_sources(source, paths):
    """Keep tracked templates that match upstream generated-output patterns."""
    result = subprocess.run(
        ['git', '-c', 'core.excludesFile=/dev/null', '-C', str(source), 'check-ignore', '--no-index', '-z', '--stdin'],
        input=b''.join(os.fsencode(path) + b'\0' for path in paths),
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        result.check_returncode()
    ignored = result.stdout.rstrip(b'\0').split(b'\0') if result.stdout else []
    if not ignored:
        return b''
    rules = set()
    for path in ignored:
        relative = Path(os.fsdecode(path))
        for part in (relative, *relative.parents):
            if part == Path('.'):
                continue
            escaped = ''.join('\\' + char if char in '\\*?[] ' else char for char in part.as_posix())
            rules.add('!/' + escaped + ('/' if part != relative else ''))
    return ('\n# Keep jstack-managed upstream files in Git.\n' +
            '\n'.join(sorted(rules)) + '\n').encode()
