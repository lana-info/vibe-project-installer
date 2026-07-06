#!/usr/bin/env python3
"""Python CLI wrapper for creating projects from the vibe template."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_SOURCE_URL = "https://github.com/di-sukharev/vibe.git"
DEFAULT_BRANCH = "master"
HOSTING_MODES = ("custom", "none", "digitalocean", "yandex")


def parse_surfaces(value: str) -> list[str]:
    surfaces = [item.strip() for item in value.split(",") if item.strip()]
    if not surfaces:
        raise argparse.ArgumentTypeError("Provide at least one surface.")
    return surfaces


def find_powershell() -> str:
    for candidate in ("pwsh", "powershell"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError("PowerShell was not found on PATH.")


def build_command(args: argparse.Namespace, script_path: Path) -> list[str]:
    command = [
        find_powershell(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-TargetPath",
        str(Path(args.target_path).expanduser()),
        "-ProjectName",
        args.project_name,
        "-ActiveSurfaces",
        ",".join(args.active_surfaces),
        "-Hosting",
        args.hosting,
    ]

    if args.source_url:
        command.extend(["-SourceUrl", args.source_url])

    if args.branch:
        command.extend(["-Branch", args.branch])

    if args.keep_template_remote:
        command.append("-KeepTemplateRemote")

    return command


def format_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a new project from the di-sukharev/vibe template."
    )
    parser.add_argument("--target-path", required=True, help="Output project folder.")
    parser.add_argument(
        "--project-name",
        required=True,
        help="Display name written into the generated README.",
    )
    parser.add_argument(
        "--active-surfaces",
        type=parse_surfaces,
        default=["web", "backend"],
        help="Comma-separated surfaces: web,mobile,backend,landing,full-stack.",
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="Template Git URL. Use an empty string only for a local template checkout.",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help="Template branch. Use an empty string for the source default branch.",
    )
    parser.add_argument(
        "--hosting",
        choices=HOSTING_MODES,
        default="custom",
        help="Hosting posture to write into the bootstrap plan.",
    )
    parser.add_argument(
        "--keep-template-remote",
        action="store_true",
        help="Keep the template origin remote in the generated project.",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the PowerShell command before running it.",
    )

    args = parser.parse_args(argv)
    script_path = Path(__file__).resolve().with_name("bootstrap-project.ps1")
    if not script_path.exists():
        parser.error(f"Missing installer script: {script_path}")

    try:
        command = build_command(args, script_path)
    except RuntimeError as exc:
        parser.error(str(exc))

    if args.print_command:
        print(format_command(command), flush=True)

    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
