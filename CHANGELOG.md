1.10.0
======

### Features
- Add support for hooks written in `rust`
    - #751 PR by @chriskuehl.

1.9.0
=====

### Features
- Add new `python_venv` language which uses the `venv` module instead of
  `virtualenv`
    - #631 issue by @dongyuzheng.
    - #739 PR by @ojii.
- Include `LICENSE` in distribution
    - #745 issue by @nicoddemus.
    - #746 PR by @nicoddemus.

### Fixes
- Normalize relative paths for `pre-commit try-repo`
    - #750 PR by @asottile.


1.8.2
=====

### Fixes
- Fix cloning relative paths (regression in 1.7.0)
    - #728 issue by @jdswensen.
    - #729 PR by @asottile.


1.8.1
=====

### Fixes
- Fix integration with go 1.10 and `pkg` directory
    - #725 PR by @asottile
- Restore support for `git<1.8.5` (inadvertantly removed in 1.7.0)
    - #723 issue by @JohnLyman.
    - #724 PR by @asottile.


1.8.0
=====

### Features
- Add a `manual` stage for cli-only interaction
    - #719 issue by @hectorv.
    - #720 PR by @asottile.
- Add a `--multiline` option to `pygrep` hooks
    - #716 PR by @tdeo.


1.7.0
=====

### Features
- pre-commit config validation was split to a separate `cfgv` library
    - #700 PR by @asottile.
- Allow `--repo` to be specified multiple times to autoupdate
    - #658 issue by @KevinHock.
    - #713 PR by @asottile.
- Enable `rev` as a preferred alternative to `sha` in `.pre-commit-config.yaml`
    - #106 issue by @asottile.
    - #715 PR by @asottile.
- Use `--clean-src` option when invoking `nodeenv` to save ~70MB per node env
    - #717 PR by @asottile.
- Refuse to install with `core.hooksPath` set
    - pre-commit/pre-commit-hooks#250 issue by @revolter.
    - #663 issue by @asottile.
    - #718 PR by @asottile.

### Fixes
- hooks with `additional_dependencies` now get isolated environments
    - #590 issue by @coldnight.
    - #711 PR by @asottile.

### Misc
- test against swift 4.x
    - #709 by @theresama.

### Updating

- Run `pre-commit migrate-config` to convert `sha` to `rev` in the
  `.pre-commit-config.yaml` file.


1.6.0
=====

### Features
- Hooks now may have a `verbose` option to produce output even without failure
    - #689 issue by @bagerard.
    - #695 PR by @bagerard.
- Installed hook no longer requires `bash`
    - #699 PR by @asottile.

### Fixes
- legacy pre-push / commit-msg hooks are now invoked as if `git` called them
    - #693 issue by @samskiter.
    - #694 PR by @asottile.
    - #699 PR by @asottile.

1.5.1
=====

### Fixes
- proper detection for root commit during pre-push
    - #503 PR by @philipgian.
    - #692 PR by @samskiter.

1.5.0
=====

### Features
- pre-commit now supports node hooks on windows.
    - for now, requires python3 due to https://bugs.python.org/issue32539
    - huge thanks to @wenzowski for the tip!
    - #200 issue by @asottile.
    - #685 PR by @asottile.

### Misc
- internal reorganization of `PrefixedCommandRunner` -> `Prefix`
    - #684 PR by @asottile.
- https-ify links.
    - pre-commit.com is now served over https.
    - #688 PR by @asottile.


1.4.5
=====

### Fixes
- Fix `local` golang repositories with `additional_dependencies`.
    - #679 #680 issue and PR by @asottile.

### Misc
- Replace some string literals with constants
    - #678 PR by @revolter.

1.4.4
=====

### Fixes
- Invoke `git diff` without a pager during `--show-diff-on-failure`.
    - #676 PR by @asottile.

1.4.3
=====

### Fixes
- `pre-commit` on windows can find pythons at non-hardcoded paths.
    - #674 PR by @asottile.

1.4.2
=====

### Fixes
- `pre-commit` no longer clears `GIT_SSH` environment variable when cloning.
    - #671 PR by @rp-tanium.

1.4.1
=====

### Fixes
- `pre-commit autoupdate --repo ...` no longer deletes other repos.
    - #660 issue by @KevinHock.
    - #661 PR by @KevinHock.

1.4.0
=====

### Features
- Lazily install repositories.
    - When running `pre-commit run <hookid>`, pre-commit will only install
      the necessary repositories.
    - #637 issue by @webknjaz.
    - #639 PR by @asottile.
- Version defaulting now applies to local hooks as well.
    - This extends #556 to apply to local hooks.
    - #646 PR by @asottile.
- Add new `repo: meta` hooks.
    - `meta` hooks expose some linters of the pre-commit configuration itself.
    - `id: check-useless-excludes`: ensures that `exclude` directives actually
      apply to *any* file in the repository.
    - `id: check-hooks-apply`: ensures that the configured hooks apply to
      at least one file in the repository.
    - pre-commit/pre-commit-hooks#63 issue by @asottile.
    - #405 issue by @asottile.
    - #643 PR by @hackedd.
    - #653 PR by @asottile.
    - #654 PR by @asottile.
- Allow a specific repository to be autoupdated instead of all repositories.
    - `pre-commit autoupdate --repo ...`
    - #656 issue by @KevinHock.
    - #657 PR by @KevinHock.

### Fixes
- Apply selinux labelling option to docker volumes
    - #642 PR by @jimmidyson.


1.3.0
=====

### Features
- Add `pre-commit try-repo` commands
    - The new `try-repo` takes a repo and will run the hooks configured in
      that hook repository.
    - An example invocation:
      `pre-commit try-repo https://github.com/pre-commit/pre-commit-hooks`
    - `pre-commit try-repo` can also take all the same arguments as
      `pre-commit run`.
    - It can be used to try out a repository without needing to configure it.
    - It can also be used to test a hook repository while developing it.
    - #589 issue by @sverhagen.
    - #633 PR by @asottile.

1.2.0
=====

### Features
- Add `pygrep` language
    - `pygrep` aims to be a more cross-platform alternative to `pcre` hooks.
    - #630 PR by @asottile.

### Fixes
- Use `pipes.quote` for executable path in hook template
    - Fixes bash syntax error when git dir contains spaces
    - #626 PR by @asottile.
- Clean up hook template
    - Simplify code
    - Fix `--config` not being respected in some situations
    - #627 PR by @asottile.
- Use `file://` protocol for cloning under test
    - Fix `file://` clone paths being treated as urls for golang
    - #629 PR by @asottile.
- Add `ctypes` as an import for virtualenv healthchecks
    - Fixes python3.6.2 <=> python3.6.3 virtualenv invalidation
    - e70825ab by @asottile.

1.1.2
=====

### Fixes
- pre-commit can successfully install commit-msg hooks
    - Due to an oversight, the commit-msg-tmpl was missing from the packaging
    - #623 issue by @sobolevn.
    - #624 PR by @asottile.

1.1.1
=====

### Features
- pre-commit also checks the `ssl` module for virtualenv health
    - Suggestion by @merwok.
    - #619 PR by @asottile.
### Fixes
- pre-commit no longer crashes with unstaged files when run for the first time
    - #620 #621 issue by @Lucas-C.
    - #622 PR by @asottile.

1.1.0
=====

### Features
- pre-commit configuration gains a `fail_fast` option.
    - You must be using the v2 configuration format introduced in 1.0.0.
    - `fail_fast` defaults to `false`.
    - #240 issue by @Lucas-C.
    - #616 PR by @asottile.
- pre-commit configuration gains a global `exclude` option.
    - This option takes a python regular expression and can be used to exclude
      files from _all_ hooks.
    - You must be using the v2 configuration format introduced in 1.0.0.
    - #281 issue by @asieira.
    - #617 PR by @asottile.

1.0.1
=====

### Fixes
- Fix a regression in the return code of `pre-commit autoupdate`
    - `pre-commit migrate-config` and `pre-commit autoupdate` return 0 when
      successful.
    - #614 PR by @asottile.

1.0.0
=====
pre-commit will now be following [semver](https://semver.org/).  Thanks to all
of the [contributors](https://github.com/pre-commit/pre-commit/graphs/contributors)
that have helped us get this far!

### Features

- pre-commit's cache directory has moved from `~/.pre-commit` to
  `$XDG_CACHE_HOME/pre-commit` (usually `~/.cache/pre-commit`).
    - `pre-commit clean` now cleans up both the old and new directory.
    - If you were caching this directory in CI, you'll want to adjust the
      location.
    - #562 issue by @nagromc.
    - #602 PR by @asottile.
- A new configuration format for `.pre-commit-config.yaml` is introduced which
  will enable future development.
    - The new format has a top-level map instead of a top-level list.  The
      new format puts the hook repositories in a `repos` key.
    - Old list-based configurations will continue to be supported.
    - A command `pre-commit migrate-config` has been introduced to "upgrade"
      the configuration format to the new map-based configuration.
    - `pre-commit autoupdate` now automatically calls `migrate-config`.
    - In a later release, list-based configurations will issue a deprecation
      warning.
    - An example diff for upgrading a configuration:

    ```diff
    +repos:
     -   repo: https://github.com/pre-commit/pre-commit-hooks
         sha: v0.9.2
         hooks:
    ```
    - #414 issue by @asottile.
    - #610 PR by @asottile.

### Updating

- Run `pre-commit migrate-config` to convert `.pre-commit-config.yaml` to the
  new map format.
- Update any references from `~/.pre-commit` to `~/.cache/pre-commit`.

0.18.3
======
- Allow --config to affect `pre-commit install`
- Tweak not found error message during `pre-push` / `commit-msg`
- Improve node support when running under cygwin.

0.18.2
======
- Fix `--all-files`, detection of staged files, detection of manually edited
  files during merge conflict, and detection of files to push for non-ascii
  filenames.

0.18.1
======
- Only mention locking when waiting for a lock.
- Fix `IOError` during locking in timeout situtation on windows under python 2.

0.18.0
======
- Add a new `docker_image` language type.  `docker_image` is intended to be a
  lightweight hook type similar to `system` / `script` which allows one to use
  an existing docker image that provides a hook.  `docker_image` hooks can
  also be used as repository `local` hooks.

0.17.0
======
- Fix typos in help
- Allow `commit-msg` hook to be uninstalled
- Upgrade the `sample-config`
- Remove undocumented `--no-stash` and `--allow-unstaged-config`
- Remove `validate_config` hook pre-commit hook.
- Fix installation race condition when multiple `pre-commit` processes would
  attempt to install the same repository.

0.16.3
======
- autoupdate attempts to maintain config formatting.

0.16.2
======
- Initialize submodules in hook repositories.

0.16.1
======
- Improve node support when running under cygwin.

0.16.0
======
- Remove backward compatibility with repositories providing metadata via
  `hooks.yaml`.  New repositories should provide `.pre-commit-hooks.yaml`.
  Run `pre-commit autoupdate` to upgrade to the latest repositories.
- Improve golang support when running under cygwin.
- Fix crash with unstaged trailing whitespace additions while git was
  configured with `apply.whitespace = error`.
- Fix crash with unstaged end-of-file crlf additions and the file's lines
  ended with crlf while git was configured with `core-autocrlf = true`.

0.15.4
======
- Add support for the `commit-msg` git hook

0.15.3
======
- Recover from invalid python virtualenvs


0.15.2
======
- Work around a windows-specific virtualenv bug pypa/virtualenv#1062
  This failure mode was introduced in 0.15.1

0.15.1
======
- Use a more intelligent default language version for python

0.15.0
======
- Add `types` and `exclude_types` for filtering files.  These options take
  an array of "tags" identified for each file.  The tags are sourced from
  [identify](https://github.com/chriskuehl/identify).  One can list the tags
  for a file by running `identify-cli filename`.
- `files` is now optional (defaulting to `''`)
- `always_run` + missing `files` also defaults to `files: ''` (previously it
  defaulted to `'^$'` (this reverses e150921c).

0.14.3
======
- Expose `--origin` and `--source` as `PRE_COMMIT_ORIGIN` and
  `PRE_COMMIT_SOURCE` environment variables when running as `pre-push`.

0.14.2
======
- Use `--no-ext-diff` when running `git diff`

0.14.1
======
- Don't crash when `always_run` is `True` and `files` is not provided.
- Set `VIRTUALENV_NO_DOWNLOAD` when making python virtualenvs.

0.14.0
======
- Add a `pre-commit sample-config` command
- Enable ansi color escapes on modern windows
- `autoupdate` now defaults to `--tags-only`, use `--bleeding-edge` for the
  old behavior
- Add support for `log_file` in hook configuration to tee hook output to a
  file for CI consumption, etc.
- Fix crash with unicode commit messages during merges in python 2.
- Add a `pass_filenames` option to allow disabling automatic filename
  positional arguments to hooks.

0.13.6
======
- Fix regression in 0.13.5: allow `always_run` and `files` together despite
  doing nothing.

0.13.5
======
- 0.13.4 contained incorrect files

0.13.4
======
- Add `--show-diff-on-failure` option to `pre-commit run`
- Replace `jsonschema` with better error messages

0.13.3
======
- Add `--allow-missing-config` to install: allows `git commit` without a
  configuration.

0.13.2
======
- Version the local hooks repo
- Allow `minimum_pre_commit_version` for local hooks

0.13.1
======
- Fix dummy gem for ruby local hooks

0.13.0
======
- Autoupdate now works even when the current state is broken.
- Improve pre-push fileset on new branches
- Allow "language local" hooks, hooks which install dependencies using
  `additional_dependencies` and `language` are now allowed in `repo: local`.

0.12.2
======
- Fix docker hooks on older (<1.12) docker

0.12.1
======
- golang hooks now support additional_dependencies
- Added a --tags-only option to pre-commit autoupdate

0.12.0
======
- The new default file for implementing hooks in remote repositories is now
  .pre-commit-hooks.yaml to encourage repositories to add the metadata.  As
  such, the previous hooks.yaml is now deprecated and generates a warning.
- Fix bug with local configuration interfering with ruby hooks
- Added support for hooks written in golang.

0.11.0
======
- SwiftPM support.

0.10.1
======
- shlex entry of docker based hooks.
- Make shlex behaviour of entry more consistent.

0.10.0
======
- Add an `install-hooks` command similar to `install --install-hooks` but
  without the `install` side-effects.
- Adds support for docker based hooks.

0.9.4
=====
- Warn when cygwin / python mismatch
- Add --config for customizing configuration during run
- Update rbenv + plugins to latest versions
- pcre hooks now fail when grep / ggrep are not present

0.9.3
=====
- Fix python hook installation when a strange setup.cfg exists

0.9.2
=====
- Remove some python2.6 compatibility
- UI is no longer sized to terminal width, instead 80 characters or longest
  necessary width.
- Fix inability to create python hook environments when using venv / pyvenv on
  osx

0.9.1
=====
- Remove some python2.6 compatibility
- Fix staged-files-only with external diff tools

0.9.0
=====
- Only consider forward diff in changed files
- Don't run on staged deleted files that still exist
- Autoupdate to tags when available
- Stop supporting python2.6
- Fix crash with staged files containing unstaged lines which have non-utf8
  bytes and trailing whitespace

0.8.2
=====
- Fix a crash introduced in 0.8.0 when an executable was not found

0.8.1
=====
- Fix regression introduced in 0.8.0 when already using rbenv with no
  configured ruby hook version

0.8.0
=====
- Fix --files when running in a subdir
- Improve --help a bit
- Switch to pyterminalsize for determining terminal size

0.7.6
=====
- Work under latest virtualenv
- No longer create empty directories on windows with latest virtualenv

0.7.5
=====
- Consider dead symlinks as files when committing

0.7.4
=====
- Produce error message instead of crashing on non-utf8 installation failure

0.7.3
=====
- Fix regression introduced in 0.7.1 breaking `git commit -a`

0.7.2
=====
- Add `always_run` setting for hooks to run even without file changes.

0.7.1
=====
- Support running pre-commit inside submodules

0.7.0
=====
- Store state about additional_dependencies for rollforward/rollback compatibility

0.6.8
=====
- Build as a universal wheel
- Allow '.format('-like strings in arguments
- Add an option to require a minimum pre-commit version

0.6.7
=====
- Print a useful message when a hook id is not present
- Fix printing of non-ascii with unexpected errors
- Print a message when a hook modifies files but produces no output

0.6.6
=====
- Add `additional_dependencies` to hook configuration.
- Fix pre-commit cloning under git 2.6
- Small improvements for windows

0.6.5
=====
- Allow args for pcre hooks

0.6.4
=====
- Fix regression introduced in 0.6.3 regarding hooks which make non-utf8 diffs

0.6.3
=====
- Remove `expected_return_code`
- Fail a hook if it makes modifications to the working directory

0.6.2
=====
- Use --no-ri --no-rdoc instead of --no-document for gem to fix old gem

0.6.1
=====
- Fix pre-push when pushing something that's already up to date

0.6.0
=====
- Filter hooks by stage (commit, push).

0.5.5
=====
- Change permissions a few files
- Rename the validate entrypoints
- Add --version to some entrypoints
- Add --no-document to gem installations
- Use expanduser when finding the python binary
- Suppress complaint about $TERM when no tty is attached
- Support pcre hooks on osx through ggrep

0.5.4
=====
- Allow hooks to produce outputs with arbitrary bytes
- Fix pre-commit install when .git/hooks/pre-commit is a dead symlink
- Allow an unstaged config when using --files or --all-files

0.5.3
=====
- Fix autoupdate with "local" hooks - don't purge local hooks.

0.5.2
=====
- Fix autoupdate with "local" hooks

0.5.1
=====
- Fix bug with unknown non-ascii hook-id
- Avoid crash when .git/hooks is not present in some git clients

0.5.0
=====
- Add a new "local" hook type for running hooks without remote configuration.
- Complain loudly when .pre-commit-config.yaml is unstaged.
- Better support for multiple language versions when running hooks.
- Allow exclude to be defaulted in repository configuration.

0.4.4
=====
- Use sys.executable when executing virtualenv

0.4.3
=====
- Use reset instead of checkout when checkout out hook repo

0.4.2
=====
- Limit length of xargs arguments to workaround windows xargs bug

0.4.1
=====
- Don't rename across devices when creating sqlite database

0.4.0
=====
- Make ^C^C During installation not cause all subsequent runs to fail
- Print while installing (instead of while cloning)
- Use sqlite to manage repositories (instead of symlinks)
- MVP Windows support

0.3.6
=====
- `args` in venv'd languages are now property quoted.

0.3.5
=====
- Support running during `pre-push`.  See https://pre-commit.com/#advanced 'pre-commit during push'.

0.3.4
=====
- Allow hook providers to default `args` in `hooks.yaml`

0.3.3
=====
- Improve message for `CalledProcessError`

0.3.2
=====
- Fix for `staged_files_only` with color.diff = always #176.

0.3.1
=====
- Fix error clobbering #174.
- Remove dependency on `plumbum`.
- Allow pre-commit to be run from anywhere in a repository #175.

0.3.0
=====
- Add `--files` option to `pre-commit run`

0.2.11
======
- Fix terminal width detection (broken in 0.2.10)

0.2.10
======
- Bump version of nodeenv to fix bug with ~/.npmrc
- Choose `python` more intelligently when running.

0.2.9
=====
- Fix bug where sys.stdout.write must take `bytes` in python 2.6

0.2.8
=====
- Allow a client to have duplicates of hooks.
- Use --prebuilt instead of system for node.
- Improve some fatal error messages

0.2.7
=====
- Produce output when running pre-commit install --install-hooks

0.2.6
=====
- Print hookid on failure
- Use sys.executable for running nodeenv
- Allow running as `python -m pre_commit`

0.2.5
=====
- Default columns to 80 (for non-terminal execution).

0.2.4
=====
- Support --install-hooks as an argument to `pre-commit install`
- Install hooks before attempting to run anything
- Use `python -m nodeenv` instead of `nodeenv`

0.2.3
=====
- Freeze ruby building infrastructure
- Fix bug that assumed diffs were utf-8

0.2.2
=====
- Fix filenames with spaces

0.2.1
=====
- Use either `pre-commit` or `python -m pre_commit.main` depending on which is
  available
- Don't use readlink -f

0.2.0
=====
- Fix for merge-conflict during cherry-picking.
- Add -V / --version
- Add migration install mode / install -f / --overwrite
- Add `pcre` "language" for perl compatible regexes
- Reorganize packages.

0.1.1
=====
- Fixed bug with autoupdate setting defaults on un-updated repos.


0.1
===
- Initial Release
