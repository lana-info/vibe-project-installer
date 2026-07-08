#!/usr/bin/env python3
"""Install vibe-coding workflow docs into an existing project."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PACK_ROOT = ROOT / "templates" / "project-pack"
DEPLOYMENT_PLANS = {
    "decide-later": "Decide later",
    "hetzner": "Hetzner",
    "timeweb": "Timeweb",
    "digitalocean": "DigitalOcean",
    "hostinger": "Hostinger",
    "custom": "Custom hosting",
}
FEATURES = {
    "payments": "Payments / subscriptions",
    "uploads-media": "Uploads / media",
    "social-auth": "Social auth",
    "push-notifications": "Push notifications",
    "background-jobs": "Background jobs",
    "scheduled-tasks": "Scheduled tasks / cron",
    "e2e-tests": "Mobile + web E2E tests",
    "admin": "Admin panel",
    "realtime": "Realtime / chat",
    "marketplace-catalog": "Marketplace / catalog",
    "ai-features": "AI features",
    "design-starter": "Design starter",
}


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_features(value: str) -> list[str]:
    features = parse_csv(value)
    invalid = [feature for feature in features if feature not in FEATURES]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"Unknown feature(s): {', '.join(invalid)}. Use: {', '.join(FEATURES)}."
        )
    return features


def render_template(text: str, args: argparse.Namespace) -> str:
    feature_names = [FEATURES[feature] for feature in args.features]
    replacements = {
        "{{PROJECT_NAME}}": args.project_name,
        "{{ACTIVE_SURFACES}}": ", ".join(args.active_surfaces),
        "{{FEATURE_LIST}}": ", ".join(feature_names) if feature_names else "No extra feature packs selected yet.",
        "{{DEPLOYMENT_PLAN}}": DEPLOYMENT_PLANS[args.deployment_plan],
        "{{PROJECT_TEMPLATE}}": "existing-project",
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def write_template_file(source: Path, destination: Path, args: argparse.Namespace) -> bool:
    if destination.exists():
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_template(source.read_text(encoding="utf-8"), args), encoding="utf-8", newline="\n")
    return True


def copy_template_tree(source_root: Path, target_root: Path, args: argparse.Namespace) -> list[str]:
    created: list[str] = []
    if not source_root.exists():
        return created

    for source in source_root.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root)
        if write_template_file(source, target_root / relative, args):
            created.append(str(relative).replace("\\", "/"))
    return created


def append_readme_sections(target_root: Path, args: argparse.Namespace) -> list[str]:
    readme = target_root / "README.md"
    if not readme.exists():
        readme.write_text(f"# {args.project_name}\n", encoding="utf-8", newline="\n")

    content = readme.read_text(encoding="utf-8", errors="replace")
    created: list[str] = []

    if "## Vibe Coding Setup" not in content:
        lines = [
            "",
            "## Vibe Coding Setup",
            "",
            f"- Active surfaces: {', '.join(args.active_surfaces)}",
            f"- Deployment plan: {DEPLOYMENT_PLANS[args.deployment_plan]}",
            "- Start with `START_HERE.md`, `PRD.md`, `TASKS.md`, and `wiki/how-to-work-with-ai.md`.",
        ]
        content = content.rstrip() + "\n" + "\n".join(lines) + "\n"
        created.append("README.md#Vibe Coding Setup")

    if args.features and "## Selected Feature Packs" not in content:
        lines = ["", "## Selected Feature Packs", ""]
        for feature in args.features:
            lines.append(f"- {FEATURES[feature]}: see `wiki/features/{feature}.md` and `prompts/features/{feature}.md`.")
        lines.append("")
        content = content.rstrip() + "\n" + "\n".join(lines)
        created.append("README.md#Selected Feature Packs")

    readme.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")
    return created


def install_project_pack(args: argparse.Namespace) -> list[str]:
    target_root = Path(args.target_path).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    created = copy_template_tree(PROJECT_PACK_ROOT / "base", target_root, args)
    for feature in args.features:
        created.extend(copy_template_tree(PROJECT_PACK_ROOT / "features" / feature, target_root, args))
    created.extend(append_readme_sections(target_root, args))
    return created


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install vibe-coding workflow docs into an existing project.")
    parser.add_argument("--target-path", default=".", help="Existing project folder. Defaults to current directory.")
    parser.add_argument("--project-name", help="Project display name. Defaults to target folder name.")
    parser.add_argument(
        "--active-surfaces",
        type=parse_csv,
        default=["web", "mobile", "backend"],
        help="Comma-separated surfaces: web,mobile,backend,landing.",
    )
    parser.add_argument(
        "--deployment-plan",
        choices=tuple(DEPLOYMENT_PLANS),
        default="decide-later",
        help="Documentation-only deployment plan.",
    )
    parser.add_argument(
        "--features",
        type=parse_features,
        default=[],
        help=f"Comma-separated feature packs: {','.join(FEATURES)}.",
    )

    args = parser.parse_args(argv)
    target_root = Path(args.target_path).expanduser().resolve()
    if not args.project_name:
        args.project_name = target_root.name

    created = install_project_pack(args)
    if created:
        print("Project workflow pack installed:", ", ".join(created))
    else:
        print("Project workflow pack already present. No files changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
