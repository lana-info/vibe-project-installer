#!/usr/bin/env python3
"""Python CLI wrapper for creating projects from the vibe template."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PACK_ROOT = ROOT / "templates" / "project-pack"
DEFAULT_SOURCE_URL = "https://github.com/di-sukharev/vibe.git"
DEFAULT_WEB_BRANCH = "master"
DEFAULT_MOBILE_BRANCH = "mobile"
HOSTING_MODES = ("custom", "none", "digitalocean")
FEATURES = {
    "payments": "Payments / subscriptions",
    "uploads-media": "Uploads / media",
    "social-auth": "Social auth",
    "push-notifications": "Push notifications",
    "admin": "Admin panel",
    "realtime": "Realtime / chat",
    "marketplace-catalog": "Marketplace / catalog",
    "ai-features": "AI features",
}


def parse_surfaces(value: str) -> list[str]:
    surfaces = [item.strip() for item in value.split(",") if item.strip()]
    if not surfaces:
        raise argparse.ArgumentTypeError("Provide at least one surface.")
    return surfaces


def parse_features(value: str) -> list[str]:
    features = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [feature for feature in features if feature not in FEATURES]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"Unknown feature(s): {', '.join(invalid)}. Use: {', '.join(FEATURES)}."
        )
    return features


def find_powershell() -> str:
    for candidate in ("pwsh", "powershell"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError("PowerShell was not found on PATH.")


def build_command(args: argparse.Namespace, script_path: Path) -> list[str]:
    branch = args.branch
    if branch is None:
        branch = DEFAULT_MOBILE_BRANCH if "mobile" in args.active_surfaces else DEFAULT_WEB_BRANCH

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

    if branch:
        command.extend(["-Branch", branch])

    if args.keep_template_remote:
        command.append("-KeepTemplateRemote")

    command.append("-SkipWorkflowDocs")

    return command


def format_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def render_template(text: str, args: argparse.Namespace) -> str:
    feature_names = [FEATURES[feature] for feature in args.features]
    replacements = {
        "{{PROJECT_NAME}}": args.project_name,
        "{{ACTIVE_SURFACES}}": ", ".join(args.active_surfaces),
        "{{FEATURE_LIST}}": ", ".join(feature_names) if feature_names else "No extra feature packs selected yet.",
    }

    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def write_template_file(source: Path, destination: Path, args: argparse.Namespace) -> bool:
    if destination.exists():
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    text = render_template(source.read_text(encoding="utf-8"), args)
    destination.write_text(text, encoding="utf-8", newline="\n")
    return True


def copy_template_tree(source_root: Path, target_root: Path, args: argparse.Namespace) -> list[str]:
    created: list[str] = []
    if not source_root.exists():
        return created

    for source in source_root.rglob("*"):
        if not source.is_file():
            continue

        relative = source.relative_to(source_root)
        destination = target_root / relative
        if write_template_file(source, destination, args):
            created.append(str(relative).replace("\\", "/"))

    return created


def append_feature_summary(target_root: Path, args: argparse.Namespace) -> bool:
    readme = target_root / "README.md"
    if not readme.exists() or not args.features:
        return False

    content = readme.read_text(encoding="utf-8", errors="replace")
    if "## Selected Feature Packs" in content:
        return False

    lines = ["", "## Selected Feature Packs", ""]
    for feature in args.features:
        lines.append(f"- {FEATURES[feature]}: see `wiki/features/{feature}.md` and `prompts/features/{feature}.md`.")
    lines.append("")

    readme.write_text(content.rstrip() + "\n" + "\n".join(lines), encoding="utf-8", newline="\n")
    return True


def install_project_pack(args: argparse.Namespace) -> list[str]:
    if args.skip_workflow_docs:
        return []

    target_root = Path(args.target_path).expanduser().resolve()
    created = copy_template_tree(PROJECT_PACK_ROOT / "base", target_root, args)

    for feature in args.features:
        created.extend(copy_template_tree(PROJECT_PACK_ROOT / "features" / feature, target_root, args))

    if append_feature_summary(target_root, args):
        created.append("README.md#Selected Feature Packs")

    return created


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
        default=["web", "mobile", "backend"],
        help="Comma-separated surfaces: web,mobile,backend,landing,full-stack.",
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="Template Git URL. Use an empty string only for a local template checkout.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Template branch. Defaults to mobile when mobile is active, otherwise master.",
    )
    parser.add_argument(
        "--hosting",
        choices=HOSTING_MODES,
        default="custom",
        help="Advanced: cloud setup note to write into the bootstrap plan.",
    )
    parser.add_argument(
        "--keep-template-remote",
        action="store_true",
        help="Keep the template origin remote in the generated project.",
    )
    parser.add_argument(
        "--skip-workflow-docs",
        action="store_true",
        help="Do not create starter PRD, TASKS, wiki, and prompts files.",
    )
    parser.add_argument(
        "--features",
        type=parse_features,
        default=[],
        help=f"Comma-separated feature packs: {','.join(FEATURES)}.",
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
    if completed.returncode != 0:
        return completed.returncode

    created = install_project_pack(args)
    if created:
        print("Project workflow pack created:", ", ".join(created))
    return 0


if __name__ == "__main__":
    sys.exit(main())
