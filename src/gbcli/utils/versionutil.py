from importlib.metadata import PackageNotFoundError, version

from packaging.version import InvalidVersion, Version

from gbcli.utils.gbconstants import PROJECT_NAME
from gbcli.utils.gh_clone import get_public_repo_tags, run_github_command
from gbcommon.types.constants import GB_PUBLIC_REPO_NAME, GB_PUBLIC_REPO_ORG


def get_latest_version(repo_org: str, repo_name: str) -> str:
    tags = run_github_command(lambda: get_public_repo_tags(repo_org, repo_name))

    versions = []
    for tag in tags:
        raw = str(tag["ref"]).split("/")[-1].lstrip("v")
        try:
            versions.append(Version(raw))
        except InvalidVersion:
            continue  # skip non-PEP440 tags rather than failing the whole check

    return str(max(versions)) if versions else "0.0.0"


def get_current_version(package_name: str) -> str:
    try:
        return str(version(package_name))
    except PackageNotFoundError:
        return "unknown"


def check_current_and_latest_versions() -> str:
    # The version check queries the public granite.build repo over unauthenticated
    # HTTPS, so it needs no GitHub credentials, SSH keys, or login. It therefore works
    # everywhere, including standalone mode.
    #
    # This is a best-effort notice, not a gate: if the public lookup can't complete
    # (offline, rate-limited, etc.) we silently skip it rather than blocking the
    # command the user actually ran.
    try:
        latest_version = get_latest_version(GB_PUBLIC_REPO_ORG, GB_PUBLIC_REPO_NAME)
    except Exception:
        return ""

    current_version = get_current_version("granite.build")

    if Version(current_version) < Version(latest_version):
        return (
            f"A new version of {PROJECT_NAME} CLI ({latest_version}) is available. "
            f"You are currently running version {current_version}. "
            "Run `pip install --upgrade granite.build` or a command suitable to your environment to upgrade."
        )
    else:
        return ""
