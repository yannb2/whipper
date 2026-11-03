# Yann's whipper fork

This fork is upstream [whipper](https://github.com/whipper-team/whipper) plus two
changes, used as the default CD ripper in the homelab's `arm` VM (Hitachi-LG GH40L
drive). Everything else is upstream's code, unchanged.

| Commit | What it does | Tested |
| --- | --- | --- |
| Add flac_level option to whipper cd rip | Adds `--flac-level 0-8` to `whipper cd rip`, also settable as `flac_level` in `whipper.conf`. Writes "FLAC compression level" to the rip log when set. | Unit tests and a config-file check (2026-10-26) |
| Dockerfile: build on Debian trixie | Moves the official Dockerfile from Debian buster (end of life, so the stock image can no longer be built) to trixie. | By the **Homelab image** workflow on every pull request |
| Homelab image workflow (this file too) | Builds the image, checks that `--flac-level` is there, and publishes `ghcr.io/yannb2/whipper:latest` on every push to `develop`. | Runs in GitHub Actions |

The two code changes were made against upstream `develop` at `71251a0` (February 2026).
They are kept in the fork only for now (Yann, 2026-10-26); either could be sent upstream
as its own pull request later.

## How flac_level works

- `[whipper.cd.rip]` keys are read as defaults for `whipper cd rip` options. That's how
  `track_template` already works, so the new `--flac-level` option makes `flac_level = 8`
  work in the config file with no extra code.
- The value goes from `command/cd.py` to `Program.ripTrack()`, then `ReadVerifyTrackTask`,
  then `FlacEncodeTask`, and finally `program/flac.encode()`, which adds `-8` to
  `flac --silent --verify -o <out> -f <in>`.
- When the option is unset, nothing changes: flac gets no level (its default is 5) and the
  log looks as before. A value outside 0 to 8 stops the rip with
  "flac level must be between 0 and 8".
- With this build, the old `flac` wrapper script in `PATH` is no longer needed.

## Config

```ini
[whipper.cd.rip]
output_directory = /rips/music
track_template = %%A/%%d (%%y)/%%N-%%t - %%n
disc_template = %%A/%%d (%%y)/%%A - %%d
flac_level = 8
```

`whipper cd rip --flac-level 5` still overrides the config for one rip.

## Run it (arm VM, Docker)

```bash
docker pull ghcr.io/yannb2/whipper:latest
docker run --rm -it \
  --device /dev/disk/by-id/<the GH40L's link>:/dev/cdrom \
  -v /opt/whipper/config:/home/worker/.config/whipper \
  -v /rips:/rips \
  ghcr.io/yannb2/whipper:latest cd rip
```

The container runs as uid 1000 in the `cdrom` group, so `/rips` must be writable by uid
1000 (the homelab's `media` user). Podman takes the same arguments.

To build it yourself instead of pulling: `docker build -t localhost/whipper-flac .` in a
clone of this repo (a full clone, since setuptools-scm reads the version from git). If
the build fails on a Debian package name, the error names the missing package; fix it
in the Dockerfile.

## Check the first rip

- The log has `FLAC compression level: 8` under "Ripping phase information".
- Files are a few percent smaller than a rip without the option, and AccurateRip results
  are the same (the audio is identical).

## Updating from upstream

On GitHub, **Sync fork** on `develop` merges new upstream commits; the workflow then
publishes a new image. If the sync reports a conflict, rebase the two commits onto
upstream's `develop` in a clone (`git fetch upstream && git rebase upstream/develop`),
fix the conflict, and open a pull request.

## Test results (2026-10-26, before the fork)

- Full suite: 118 passed, 3 failed. The same 3 also fail without the patch in that
  sandbox: two need the `cdparanoia` and `cdrdao` binaries, and one checks a version
  string that a shallow git clone doesn't produce.
- New tests, all passing: flac arguments with no level, level 8 and level 0; a real encode
  where level 8 makes a smaller file than level 0; the log line only appearing when the
  level is set.
- Config check: with `flac_level = 8` in `whipper.conf`, the option reads 8;
  `--flac-level 3` overrides it to 3; 9 is rejected.
- Not tested then: a real rip (no CD drive) and the container build (now the workflow's job).
