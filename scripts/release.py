# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "dunamai",
#     "tomlkit",
# ]
# [tool.uv]
# exclude-newer = "2024-12-28T00:00:00Z"
# ///

import argparse
from pathlib import Path
from datetime import datetime
from typing import Literal

from dunamai import Version, Style
from tomlkit import parse as toml_parse, dump as toml_dump

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def bump_version(current_version: Version, bump_element: Literal["major", "minor", "patch"]) -> str:
    bump_index = ["major", "minor", "patch"].index(bump_element)
    return current_version.bump(index=bump_index).serialize(style=Style.SemVer).split("-")[0]


def bump_pyproject_version(bumped_version: str) -> None:
    path = PROJECT_ROOT / "pyproject.toml"

    with path.open(mode="r") as f:
        data = toml_parse(f.read())

    data["project"]["version"] = bumped_version

    with path.open(mode="w") as f:
        toml_dump(data, f)


def bump_change_log_version(bumped_version: str) -> None:
    path = PROJECT_ROOT / "CHANGELOG.md"

    with path.open(mode="r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("## [Unreleased]"):
            lines[i] = f"## [Unreleased]\n\n## [{bumped_version}] - {datetime.now().date().isoformat()}\n"

    with path.open(mode="w") as f:
        f.writelines(lines)


def dump_bumped_git_version(bumped_version: str) -> None:
    path = PROJECT_ROOT / "RELEASE_VERSION.txt"

    with path.open(mode="w") as f:
        f.write(bumped_version)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version_element", choices=["major", "minor", "patch"])
    args = parser.parse_args()

    current_version = Version.from_git()
    bumped_version = bump_version(current_version=current_version, bump_element=args.version_element)

    print(f"Bumping version: {current_version} -> {bumped_version}")
    bump_pyproject_version(bumped_version)
    print("- updated pyproject.toml")
    bump_change_log_version(bumped_version)
    print("- updated CHANGELOG.md")
    dump_bumped_git_version(f"v{bumped_version}")


if __name__ == "__main__":
    main()
