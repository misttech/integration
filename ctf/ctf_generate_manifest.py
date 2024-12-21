#!/usr/bin/env python3
# Copyright 2024 The Fuchsia Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import os
import sys
import json
import re
import subprocess
import tempfile
import difflib
from typing import Set, Dict, List

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FUCHSIA_CTS_PACKAGE = "fuchsia/cts/linux-amd64"


def main(args: argparse.Namespace) -> int:
    f_release_regex = re.compile(r"f[0-9]+")

    try:
        level_mapping = get_git_revisions_from_cipd(sorted(get_supported_api_levels()))
    except Exception as e:
        print_error(f"Could not load all data: {e}")
        return 1

    existing_files = [
        f
        for f in os.listdir(SCRIPT_DIRECTORY)
        if os.path.isfile(os.path.join(SCRIPT_DIRECTORY, f))
        and f_release_regex.match(f)
    ]

    deleted_files: Set[str] = set()
    added_files: Set[str] = set()
    populated_files: Set[str] = set()
    skipped_files: Set[str] = set()

    expected_file_contents: Dict[str, str] = {
        api_level: format_ctf_template(api_level, git_revision)
        for api_level, git_revision in level_mapping.items()
    }
    for file, expected_contents in expected_file_contents.items():
        if file not in existing_files:
            added_files.add(file)
        else:
            contents: str
            with open(os.path.join(SCRIPT_DIRECTORY, file)) as f:
                contents = f.read()
            if contents == expected_contents:
                skipped_files.add(file)
            else:
                populated_files.add(file)
    for file in existing_files:
        if file not in expected_file_contents:
            deleted_files.add(file)

    import_file_path = os.path.join(SCRIPT_DIRECTORY, "all")
    new_import_file_contents = format_import_file(sorted(level_mapping.keys()))
    old_import_file_contents = (
        open(import_file_path).read() if os.path.isfile(import_file_path) else None
    )

    if not args.dry_run:
        for file in deleted_files:
            os.remove(os.path.join(SCRIPT_DIRECTORY, file))
        for file in added_files.union(populated_files):
            with open(os.path.join(SCRIPT_DIRECTORY, file), "w") as f:
                f.write(expected_file_contents[file])

    if new_import_file_contents != old_import_file_contents:
        if not args.dry_run:
            with open(import_file_path, "w") as f:
                f.write(new_import_file_contents)

        print("Import file diff:\n=====")
        print(
            "\n".join(
                difflib.Differ().compare(
                    (old_import_file_contents or "").split("\n"),
                    new_import_file_contents.split("\n"),
                )
            )
        )
        print("=====")

        if old_import_file_contents is None:
            added_files.add("all")
        else:
            populated_files.add("all")
    else:
        skipped_files.add("all")

    print_outcome(
        args.dry_run,
        deleted=sorted(deleted_files),
        added=sorted(added_files),
        populated=sorted(populated_files),
        skipped=sorted(skipped_files),
    )

    return 0


def get_supported_api_levels() -> Set[str]:
    """Return a set of supported API levels, as listed in version_history.json

    Returns:
        Set[str]: Versions that are supported. For example, {"f15", "f16"}.
    """
    version_path = os.path.join(
        SCRIPT_DIRECTORY,
        "..",
        "..",
        "infra",
        "config",
        "common",
        "version_history.json",
    )
    with open(version_path) as f:
        version_contents = json.load(f)

    # Get the name of each API level where its status is "supported"
    version_data: Dict[str, Dict[str, str]] = version_contents["data"]["api_levels"]
    return {
        f"f{key}"
        for key, value in version_data.items()
        if (value.get("phase") or value.get("status")) == "supported"
    }


def get_git_revisions_from_cipd(versions: List[str]) -> Dict[str, str]:
    """Annotate versions with their corresponding git_revision tag from CIPD.

    This method uses CIPD to find the associated git_revision for a CIPD
    package by its version name. If the package doesn't exist or does not have
    a git_revision, that version is omitted from the output dictionary.

    Args:
        keys (abc.Iterable[str]): CIPD package versions to search for.

    Returns:
        Dict[str, str]: Mapping from version to its git_revision,
            only if it exists.
    """
    ret: Dict[str, str] = dict()

    for key in versions:
        with tempfile.TemporaryDirectory() as td:
            # Run CIPD command to search for a matching version of the
            # Fuchsia CTS package.
            output_path = os.path.join(td, "output.json")
            args = [
                "cipd",
                "describe",
                FUCHSIA_CTS_PACKAGE,
                "-version",
                key,
                "-json-output",
                output_path,
            ]
            print("Running ", args)
            result = subprocess.run(args)

            # If we found one, look through the tags for one containing
            # the git revision.
            if result.returncode == 0:
                with open(output_path) as f:
                    data = json.load(f)
                for tag_object in data["result"]["tags"]:
                    tag: str = tag_object["tag"]
                    if tag.startswith("git_revision:"):
                        ret[key] = tag.split(":")[1]
                        break

    return ret


_CTF_TEMPLATE: str = r"""<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <packages>
    <!-- Versioned CTF release. See ctf_generate_manifest.py for details. -->
    <package name="fuchsia/cts/${platform}"
             path="prebuilt/ctf/{F_RELEASE}/{{.OS}}-{{.Arch}}"
             platforms="linux-amd64"
             version="git_revision:{REVISION}" />
  </packages>
</manifest>"""


def format_ctf_template(f_release: str, git_revision: str) -> str:
    """Format a manifest file for the given f_release version and git revision.

    Args:
        f_release (str): Release name. For example, "f15".
        revision (str): Git revision tag from CIPD for that release.

    Returns:
        str: Formatted jiri manifest file, to be written to disk.
    """
    return _CTF_TEMPLATE.replace(r"{F_RELEASE}", f_release).replace(
        r"{REVISION}", git_revision
    )


_IMPORTER_TEMPLATE: str = r"""<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <imports>
    {IMPORTS}
  </imports>
</manifest>
"""


def format_import_file(files: List[str]) -> str:
    """Format a complete manifest import file.

    Args:
        files (List[str]): Files to import in the manifest.

    Returns:
        str: Formatted manifest file, ready to write to disk.
    """
    return _IMPORTER_TEMPLATE.replace(r"{IMPORTS}", format_import_list(files))


_IMPORT_TEMPLATE: str = r'<localimport file="{FILE}"/>'


def format_import_list(files: List[str]) -> str:
    """Format the localimport section for a manifest.

    Args:
        files (List[str]): Files to include in the import list.

    Returns:
        _type_: Formatted string containing imports to include in a manifest.
    """
    return "\n    ".join([_IMPORT_TEMPLATE.replace(r"{FILE}", name) for name in files])


def print_error(reason: str) -> None:
    """Print a formatted error as JSON.

    Args:
        reason (str): Reason string to include in the error.
    """
    print(
        json.dumps(
            {
                "status": "ERROR",
                "reason": reason,
            }
        ),
    )


def print_outcome(
    dry_run: bool,
    deleted: List[str],
    added: List[str],
    populated: List[str],
    skipped: List[str],
):
    """Print the outcome of the operation as a JSON object.

    Args:
        dry_run (bool): True if this tool was executed with --dry-run.
        deleted (List[str]): List of files deleted.
        added (List[str]): List of files added.
        populated (List[str]): List of files populated (existed but have new data).
        skipped (List[str]): List of unchanged files.
    """
    did_work = len(deleted + added + populated) != 0
    status: str
    if dry_run:
        status = "DRY_RUN"
    elif did_work:
        status = "OK"
    else:
        status = "SKIPPED"

    print(
        json.dumps(
            {
                "status": status,
                "deleted": deleted,
                "added": added,
                "populated": populated,
                "skipped": skipped,
            }
        ),
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser(
        "ctf_generate_manifest", "Generate configs for CTF manifests"
    )
    args.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_const",
        default=True,
        const=False,
        help="If set, do not actually mutate files. Default True.",
    )

    sys.exit(main(args.parse_args()))
