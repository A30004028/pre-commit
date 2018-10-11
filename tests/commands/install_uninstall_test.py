# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os.path
import re
import shutil
import subprocess
import sys

import mock

import pre_commit.constants as C
from pre_commit.commands.install_uninstall import CURRENT_HASH
from pre_commit.commands.install_uninstall import install
from pre_commit.commands.install_uninstall import install_hooks
from pre_commit.commands.install_uninstall import is_our_script
from pre_commit.commands.install_uninstall import PRIOR_HASHES
from pre_commit.commands.install_uninstall import uninstall
from pre_commit.runner import Runner
from pre_commit.util import cmd_output
from pre_commit.util import make_executable
from pre_commit.util import mkdirp
from pre_commit.util import resource_filename
from testing.fixtures import git_dir
from testing.fixtures import make_consuming_repo
from testing.fixtures import remove_config_from_repo
from testing.util import cmd_output_mocked_pre_commit_home
from testing.util import cwd
from testing.util import xfailif_no_symlink


def test_is_not_script():
    assert is_our_script('setup.py') is False


def test_is_script():
    assert is_our_script(resource_filename('hook-tmpl'))


def test_is_previous_pre_commit(tmpdir):
    f = tmpdir.join('foo')
    f.write(PRIOR_HASHES[0] + '\n')
    assert is_our_script(f.strpath)


def test_install_pre_commit(tempdir_factory, store):
    path = git_dir(tempdir_factory)
    runner = Runner(path, C.CONFIG_FILE)
    assert not install(runner, store)
    assert os.access(os.path.join(path, '.git/hooks/pre-commit'), os.X_OK)

    assert not install(runner, store, hook_type='pre-push')
    assert os.access(os.path.join(path, '.git/hooks/pre-push'), os.X_OK)


def test_install_hooks_directory_not_present(tempdir_factory, store):
    path = git_dir(tempdir_factory)
    # Simulate some git clients which don't make .git/hooks #234
    hooks = os.path.join(path, '.git/hooks')
    if os.path.exists(hooks):  # pragma: no cover (latest git)
        shutil.rmtree(hooks)
    runner = Runner(path, C.CONFIG_FILE)
    install(runner, store)
    assert os.path.exists(os.path.join(path, '.git/hooks/pre-commit'))


def test_install_refuses_core_hookspath(tempdir_factory, store):
    path = git_dir(tempdir_factory)
    with cwd(path):
        cmd_output('git', 'config', '--local', 'core.hooksPath', 'hooks')
        runner = Runner(path, C.CONFIG_FILE)
        assert install(runner, store)


@xfailif_no_symlink
def test_install_hooks_dead_symlink(
        tempdir_factory, store,
):  # pragma: no cover (non-windows)
    path = git_dir(tempdir_factory)
    runner = Runner(path, C.CONFIG_FILE)
    mkdirp(os.path.join(path, '.git/hooks'))
    os.symlink('/fake/baz', os.path.join(path, '.git/hooks/pre-commit'))
    install(runner, store)
    assert os.path.exists(os.path.join(path, '.git/hooks/pre-commit'))


def test_uninstall_does_not_blow_up_when_not_there(tempdir_factory):
    path = git_dir(tempdir_factory)
    runner = Runner(path, C.CONFIG_FILE)
    ret = uninstall(runner)
    assert ret == 0


def test_uninstall(tempdir_factory, store):
    path = git_dir(tempdir_factory)
    runner = Runner(path, C.CONFIG_FILE)
    assert not os.path.exists(os.path.join(path, '.git/hooks/pre-commit'))
    install(runner, store)
    assert os.path.exists(os.path.join(path, '.git/hooks/pre-commit'))
    uninstall(runner)
    assert not os.path.exists(os.path.join(path, '.git/hooks/pre-commit'))


def _get_commit_output(tempdir_factory, touch_file='foo', **kwargs):
    commit_msg = kwargs.pop('commit_msg', 'Commit!')
    open(touch_file, 'a').close()
    cmd_output('git', 'add', touch_file)
    return cmd_output_mocked_pre_commit_home(
        'git', 'commit', '-am', commit_msg, '--allow-empty',
        # git commit puts pre-commit to stderr
        stderr=subprocess.STDOUT,
        retcode=None,
        tempdir_factory=tempdir_factory,
        **kwargs
    )[:2]


# osx does this different :(
FILES_CHANGED = (
    r'('
    r' 1 file changed, 0 insertions\(\+\), 0 deletions\(-\)\r?\n'
    r'|'
    r' 0 files changed\r?\n'
    r')'
)


NORMAL_PRE_COMMIT_RUN = re.compile(
    r'^\[INFO\] Initializing environment for .+\.\r?\n'
    r'Bash hook\.+Passed\r?\n'
    r'\[master [a-f0-9]{7}\] Commit!\r?\n' +
    FILES_CHANGED +
    r' create mode 100644 foo\r?\n$',
)


def test_install_pre_commit_and_run(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        assert install(Runner(path, C.CONFIG_FILE), store) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_install_pre_commit_and_run_custom_path(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        cmd_output('git', 'mv', C.CONFIG_FILE, 'custom-config.yaml')
        cmd_output('git', 'commit', '-m', 'move pre-commit config')
        assert install(Runner(path, 'custom-config.yaml'), store) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_install_in_submodule_and_run(tempdir_factory, store):
    src_path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    parent_path = git_dir(tempdir_factory)
    cmd_output('git', 'submodule', 'add', src_path, 'sub', cwd=parent_path)
    cmd_output('git', 'commit', '-m', 'foo', cwd=parent_path)

    sub_pth = os.path.join(parent_path, 'sub')
    with cwd(sub_pth):
        assert install(Runner(sub_pth, C.CONFIG_FILE), store) == 0
        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_install_in_worktree_and_run(tempdir_factory, store):
    src_path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    path = tempdir_factory.get()
    cmd_output('git', '-C', src_path, 'branch', '-m', 'notmaster')
    cmd_output('git', '-C', src_path, 'worktree', 'add', path, '-b', 'master')

    with cwd(path):
        assert install(Runner(path, C.CONFIG_FILE), store) == 0
        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_commit_am(tempdir_factory, store):
    """Regression test for #322."""
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        # Make an unstaged change
        open('unstaged', 'w').close()
        cmd_output('git', 'add', '.')
        cmd_output('git', 'commit', '-m', 'foo')
        with io.open('unstaged', 'w') as foo_file:
            foo_file.write('Oh hai')

        assert install(Runner(path, C.CONFIG_FILE), store) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0


def test_unicode_merge_commit_message(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        assert install(Runner(path, C.CONFIG_FILE), store) == 0
        cmd_output('git', 'checkout', 'master', '-b', 'foo')
        cmd_output('git', 'commit', '--allow-empty', '-n', '-m', 'branch2')
        cmd_output('git', 'checkout', 'master')
        cmd_output('git', 'merge', 'foo', '--no-ff', '--no-commit', '-m', '☃')
        # Used to crash
        cmd_output_mocked_pre_commit_home(
            'git', 'commit', '--no-edit',
            tempdir_factory=tempdir_factory,
        )


def test_install_idempotent(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        assert install(Runner(path, C.CONFIG_FILE), store) == 0
        assert install(Runner(path, C.CONFIG_FILE), store) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def _path_without_us():
    # Choose a path which *probably* doesn't include us
    return os.pathsep.join([
        x for x in os.environ['PATH'].split(os.pathsep)
        if x.lower() != os.path.dirname(sys.executable).lower()
    ])


def test_environment_not_sourced(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        # Patch the executable to simulate rming virtualenv
        with mock.patch.object(sys, 'executable', '/does-not-exist'):
            assert install(Runner(path, C.CONFIG_FILE), store) == 0

        # Use a specific homedir to ignore --user installs
        homedir = tempdir_factory.get()
        ret, stdout, stderr = cmd_output(
            'git', 'commit', '--allow-empty', '-m', 'foo',
            env={
                'HOME': homedir,
                'PATH': _path_without_us(),
                # Git needs this to make a commit
                'GIT_AUTHOR_NAME': os.environ['GIT_AUTHOR_NAME'],
                'GIT_COMMITTER_NAME': os.environ['GIT_COMMITTER_NAME'],
                'GIT_AUTHOR_EMAIL': os.environ['GIT_AUTHOR_EMAIL'],
                'GIT_COMMITTER_EMAIL': os.environ['GIT_COMMITTER_EMAIL'],
            },
            retcode=None,
        )
        assert ret == 1
        assert stdout == ''
        assert stderr.replace('\r\n', '\n') == (
            '`pre-commit` not found.  '
            'Did you forget to activate your virtualenv?\n'
        )


FAILING_PRE_COMMIT_RUN = re.compile(
    r'^\[INFO\] Initializing environment for .+\.\r?\n'
    r'Failing hook\.+Failed\r?\n'
    r'hookid: failing_hook\r?\n'
    r'\r?\n'
    r'Fail\r?\n'
    r'foo\r?\n'
    r'\r?\n$',
)


def test_failing_hooks_returns_nonzero(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'failing_hook_repo')
    with cwd(path):
        assert install(Runner(path, C.CONFIG_FILE), store) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 1
        assert FAILING_PRE_COMMIT_RUN.match(output)


EXISTING_COMMIT_RUN = re.compile(
    r'^legacy hook\r?\n'
    r'\[master [a-f0-9]{7}\] Commit!\r?\n' +
    FILES_CHANGED +
    r' create mode 100644 baz\r?\n$',
)


def _write_legacy_hook(path):
    mkdirp(os.path.join(path, '.git/hooks'))
    with io.open(os.path.join(path, '.git/hooks/pre-commit'), 'w') as f:
        f.write('#!/usr/bin/env bash\necho "legacy hook"\n')
    make_executable(f.name)


def test_install_existing_hooks_no_overwrite(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        _write_legacy_hook(path)

        # Make sure we installed the "old" hook correctly
        ret, output = _get_commit_output(tempdir_factory, touch_file='baz')
        assert ret == 0
        assert EXISTING_COMMIT_RUN.match(output)

        # Now install pre-commit (no-overwrite)
        assert install(runner, store) == 0

        # We should run both the legacy and pre-commit hooks
        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert output.startswith('legacy hook\n')
        assert NORMAL_PRE_COMMIT_RUN.match(output[len('legacy hook\n'):])


def test_install_existing_hook_no_overwrite_idempotent(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        _write_legacy_hook(path)

        # Install twice
        assert install(runner, store) == 0
        assert install(runner, store) == 0

        # We should run both the legacy and pre-commit hooks
        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert output.startswith('legacy hook\n')
        assert NORMAL_PRE_COMMIT_RUN.match(output[len('legacy hook\n'):])


FAIL_OLD_HOOK = re.compile(
    r'fail!\r?\n'
    r'\[INFO\] Initializing environment for .+\.\r?\n'
    r'Bash hook\.+Passed\r?\n',
)


def test_failing_existing_hook_returns_1(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        # Write out a failing "old" hook
        mkdirp(os.path.join(path, '.git/hooks'))
        with io.open(os.path.join(path, '.git/hooks/pre-commit'), 'w') as f:
            f.write('#!/usr/bin/env bash\necho "fail!"\nexit 1\n')
        make_executable(f.name)

        assert install(runner, store) == 0

        # We should get a failure from the legacy hook
        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 1
        assert FAIL_OLD_HOOK.match(output)


def test_install_overwrite_no_existing_hooks(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)
        assert install(runner, store, overwrite=True) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_install_overwrite(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        _write_legacy_hook(path)
        assert install(runner, store, overwrite=True) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_uninstall_restores_legacy_hooks(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        _write_legacy_hook(path)

        # Now install and uninstall pre-commit
        assert install(runner, store) == 0
        assert uninstall(runner) == 0

        # Make sure we installed the "old" hook correctly
        ret, output = _get_commit_output(tempdir_factory, touch_file='baz')
        assert ret == 0
        assert EXISTING_COMMIT_RUN.match(output)


def test_replace_old_commit_script(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        # Install a script that looks like our old script
        with io.open(resource_filename('hook-tmpl')) as f:
            pre_commit_contents = f.read()
        new_contents = pre_commit_contents.replace(
            CURRENT_HASH, PRIOR_HASHES[-1],
        )

        mkdirp(os.path.join(path, '.git/hooks'))
        with io.open(os.path.join(path, '.git/hooks/pre-commit'), 'w') as f:
            f.write(new_contents)
        make_executable(f.name)

        # Install normally
        assert install(runner, store) == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def test_uninstall_doesnt_remove_not_our_hooks(tempdir_factory):
    path = git_dir(tempdir_factory)
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)
        mkdirp(os.path.join(path, '.git/hooks'))
        with io.open(os.path.join(path, '.git/hooks/pre-commit'), 'w') as f:
            f.write('#!/usr/bin/env bash\necho 1\n')
        make_executable(f.name)

        assert uninstall(runner) == 0

        assert os.path.exists(os.path.join(path, '.git/hooks/pre-commit'))


PRE_INSTALLED = re.compile(
    r'Bash hook\.+Passed\r?\n'
    r'\[master [a-f0-9]{7}\] Commit!\r?\n' +
    FILES_CHANGED +
    r' create mode 100644 foo\r?\n$',
)


def test_installs_hooks_with_hooks_True(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        install(Runner(path, C.CONFIG_FILE), store, hooks=True)
        ret, output = _get_commit_output(
            tempdir_factory, pre_commit_home=store.directory,
        )

        assert ret == 0
        assert PRE_INSTALLED.match(output)


def test_install_hooks_command(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)
        install(runner, store)
        install_hooks(runner, store)
        ret, output = _get_commit_output(
            tempdir_factory, pre_commit_home=store.directory,
        )

        assert ret == 0
        assert PRE_INSTALLED.match(output)


def test_installed_from_venv(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        install(Runner(path, C.CONFIG_FILE), store)
        # No environment so pre-commit is not on the path when running!
        # Should still pick up the python from when we installed
        ret, output = _get_commit_output(
            tempdir_factory,
            env={
                'HOME': os.path.expanduser('~'),
                'PATH': _path_without_us(),
                'TERM': os.environ.get('TERM', ''),
                # Windows needs this to import `random`
                'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                # Windows needs this to resolve executables
                'PATHEXT': os.environ.get('PATHEXT', ''),
                # Git needs this to make a commit
                'GIT_AUTHOR_NAME': os.environ['GIT_AUTHOR_NAME'],
                'GIT_COMMITTER_NAME': os.environ['GIT_COMMITTER_NAME'],
                'GIT_AUTHOR_EMAIL': os.environ['GIT_AUTHOR_EMAIL'],
                'GIT_COMMITTER_EMAIL': os.environ['GIT_COMMITTER_EMAIL'],
            },
        )
        assert ret == 0
        assert NORMAL_PRE_COMMIT_RUN.match(output)


def _get_push_output(tempdir_factory, opts=()):
    return cmd_output_mocked_pre_commit_home(
        'git', 'push', 'origin', 'HEAD:new_branch', *opts,
        # git push puts pre-commit to stderr
        stderr=subprocess.STDOUT,
        tempdir_factory=tempdir_factory,
        retcode=None
    )[:2]


def test_pre_push_integration_failing(tempdir_factory, store):
    upstream = make_consuming_repo(tempdir_factory, 'failing_hook_repo')
    path = tempdir_factory.get()
    cmd_output('git', 'clone', upstream, path)
    with cwd(path):
        install(Runner(path, C.CONFIG_FILE), store, hook_type='pre-push')
        # commit succeeds because pre-commit is only installed for pre-push
        assert _get_commit_output(tempdir_factory)[0] == 0
        assert _get_commit_output(tempdir_factory, touch_file='zzz')[0] == 0

        retc, output = _get_push_output(tempdir_factory)
        assert retc == 1
        assert 'Failing hook' in output
        assert 'Failed' in output
        assert 'foo zzz' in output  # both filenames should be printed
        assert 'hookid: failing_hook' in output


def test_pre_push_integration_accepted(tempdir_factory, store):
    upstream = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    path = tempdir_factory.get()
    cmd_output('git', 'clone', upstream, path)
    with cwd(path):
        install(Runner(path, C.CONFIG_FILE), store, hook_type='pre-push')
        assert _get_commit_output(tempdir_factory)[0] == 0

        retc, output = _get_push_output(tempdir_factory)
        assert retc == 0
        assert 'Bash hook' in output
        assert 'Passed' in output


def test_pre_push_force_push_without_fetch(tempdir_factory, store):
    upstream = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    path1 = tempdir_factory.get()
    path2 = tempdir_factory.get()
    cmd_output('git', 'clone', upstream, path1)
    cmd_output('git', 'clone', upstream, path2)
    with cwd(path1):
        assert _get_commit_output(tempdir_factory)[0] == 0
        assert _get_push_output(tempdir_factory)[0] == 0

    with cwd(path2):
        install(Runner(path2, C.CONFIG_FILE), store, hook_type='pre-push')
        assert _get_commit_output(tempdir_factory, commit_msg='force!')[0] == 0

        retc, output = _get_push_output(tempdir_factory, opts=('--force',))
        assert retc == 0
        assert 'Bash hook' in output
        assert 'Passed' in output


def test_pre_push_new_upstream(tempdir_factory, store):
    upstream = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    upstream2 = git_dir(tempdir_factory)
    path = tempdir_factory.get()
    cmd_output('git', 'clone', upstream, path)
    with cwd(path):
        install(Runner(path, C.CONFIG_FILE), store, hook_type='pre-push')
        assert _get_commit_output(tempdir_factory)[0] == 0

        cmd_output('git', 'remote', 'rename', 'origin', 'upstream')
        cmd_output('git', 'remote', 'add', 'origin', upstream2)
        retc, output = _get_push_output(tempdir_factory)
        assert retc == 0
        assert 'Bash hook' in output
        assert 'Passed' in output


def test_pre_push_integration_empty_push(tempdir_factory, store):
    upstream = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    path = tempdir_factory.get()
    cmd_output('git', 'clone', upstream, path)
    with cwd(path):
        install(Runner(path, C.CONFIG_FILE), store, hook_type='pre-push')
        _get_push_output(tempdir_factory)
        retc, output = _get_push_output(tempdir_factory)
        assert output == 'Everything up-to-date\n'
        assert retc == 0


def test_pre_push_legacy(tempdir_factory, store):
    upstream = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    path = tempdir_factory.get()
    cmd_output('git', 'clone', upstream, path)
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        mkdirp(os.path.join(path, '.git/hooks'))
        with io.open(os.path.join(path, '.git/hooks/pre-push'), 'w') as f:
            f.write(
                '#!/usr/bin/env bash\n'
                'set -eu\n'
                'read lr ls rr rs\n'
                'test -n "$lr" -a -n "$ls" -a -n "$rr" -a -n "$rs"\n'
                'echo legacy\n',
            )
        make_executable(f.name)

        install(runner, store, hook_type='pre-push')
        assert _get_commit_output(tempdir_factory)[0] == 0

        retc, output = _get_push_output(tempdir_factory)
        assert retc == 0
        first_line, _, third_line = output.splitlines()[:3]
        assert first_line == 'legacy'
        assert third_line.startswith('Bash hook')
        assert third_line.endswith('Passed')


def test_commit_msg_integration_failing(
        commit_msg_repo, tempdir_factory, store,
):
    runner = Runner(commit_msg_repo, C.CONFIG_FILE)
    install(runner, store, hook_type='commit-msg')
    retc, out = _get_commit_output(tempdir_factory)
    assert retc == 1
    assert out.startswith('Must have "Signed off by:"...')
    assert out.strip().endswith('...Failed')


def test_commit_msg_integration_passing(
        commit_msg_repo, tempdir_factory, store,
):
    runner = Runner(commit_msg_repo, C.CONFIG_FILE)
    install(runner, store, hook_type='commit-msg')
    msg = 'Hi\nSigned off by: me, lol'
    retc, out = _get_commit_output(tempdir_factory, commit_msg=msg)
    assert retc == 0
    first_line = out.splitlines()[0]
    assert first_line.startswith('Must have "Signed off by:"...')
    assert first_line.endswith('...Passed')


def test_commit_msg_legacy(commit_msg_repo, tempdir_factory, store):
    runner = Runner(commit_msg_repo, C.CONFIG_FILE)

    hook_path = os.path.join(commit_msg_repo, '.git/hooks/commit-msg')
    mkdirp(os.path.dirname(hook_path))
    with io.open(hook_path, 'w') as hook_file:
        hook_file.write(
            '#!/usr/bin/env bash\n'
            'set -eu\n'
            'test -e "$1"\n'
            'echo legacy\n',
        )
    make_executable(hook_path)

    install(runner, store, hook_type='commit-msg')

    msg = 'Hi\nSigned off by: asottile'
    retc, out = _get_commit_output(tempdir_factory, commit_msg=msg)
    assert retc == 0
    first_line, second_line = out.splitlines()[:2]
    assert first_line == 'legacy'
    assert second_line.startswith('Must have "Signed off by:"...')


def test_install_disallow_mising_config(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        remove_config_from_repo(path)
        ret = install(
            runner, store, overwrite=True, skip_on_missing_conf=False,
        )
        assert ret == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 1


def test_install_allow_mising_config(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        remove_config_from_repo(path)
        ret = install(
            runner, store, overwrite=True, skip_on_missing_conf=True,
        )
        assert ret == 0

        ret, output = _get_commit_output(tempdir_factory)
        assert ret == 0
        expected = (
            '`.pre-commit-config.yaml` config file not found. '
            'Skipping `pre-commit`.'
        )
        assert expected in output


def test_install_temporarily_allow_mising_config(tempdir_factory, store):
    path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')
    with cwd(path):
        runner = Runner(path, C.CONFIG_FILE)

        remove_config_from_repo(path)
        ret = install(
            runner, store, overwrite=True, skip_on_missing_conf=False,
        )
        assert ret == 0

        env = dict(os.environ, PRE_COMMIT_ALLOW_NO_CONFIG='1')
        ret, output = _get_commit_output(tempdir_factory, env=env)
        assert ret == 0
        expected = (
            '`.pre-commit-config.yaml` config file not found. '
            'Skipping `pre-commit`.'
        )
        assert expected in output
