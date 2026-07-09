#!/usr/bin/env python3
"""Install vibe-coding workflow docs into an existing project."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from project_options import HOSTING_PROJECT_TYPES, PROJECT_TYPE_SURFACES, allowed_features_for_project_type

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PACK_ROOT = ROOT / "templates" / "project-pack"
PROJECT_TYPES = ("website", "landing", "mobile-web-app", "desktop-python", "chrome-extension")
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


def normalize_features(project_type: str, features: list[str]) -> list[str]:
    allowed = allowed_features_for_project_type(project_type, tuple(FEATURES))
    invalid = [feature for feature in features if feature not in allowed]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"{project_type} projects do not support feature(s): {', '.join(invalid)}."
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


def detect_project_files(target_root: Path) -> list[str]:
    candidates = [
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "poetry.lock",
        "pnpm-lock.yaml",
        "package-lock.json",
        "yarn.lock",
        "bun.lock",
        "vite.config.ts",
        "vite.config.js",
        "next.config.js",
        "next.config.mjs",
        "README.md",
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
    ]
    return [path for path in candidates if (target_root / path).exists()]


def write_setup_audit(target_root: Path, args: argparse.Namespace) -> list[str]:
    audit_path = unique_setup_audit_path(target_root)

    detected = detect_project_files(target_root)
    feature_names = [FEATURES[feature] for feature in args.features]
    lines = [
        "# Setup Audit",
        "",
        "This file was created by vibe-project-installer for an existing project.",
        "",
        "## Selected Setup",
        "",
        f"- Project name: {args.project_name}",
        f"- Project type: {args.project_type}",
        f"- Active surfaces: {', '.join(args.active_surfaces)}",
        f"- Deployment plan: {DEPLOYMENT_PLANS[args.deployment_plan]}",
        f"- Feature packs: {', '.join(feature_names) if feature_names else 'No extra feature packs selected.'}",
        "",
        "## Detected Files",
        "",
    ]
    if detected:
        lines.extend(f"- `{path}`" for path in detected)
    else:
        lines.append("- No common dependency/config files detected yet.")

    lines.extend(
        [
            "",
            "## Safety Rules",
            "",
            "- Existing files were not overwritten.",
            "- Dependencies were not installed automatically.",
            "- Secrets, `.env` values, tokens, and passwords must not be pasted into chat.",
            "- Before installing dependencies, ask Codex to explain what is missing, why it is needed, and which files will change.",
            "",
            "## Suggested Next Prompt",
            "",
            "```text",
            "Это существующий проект для вайбкодинга.",
            "Проверь структуру, зависимости и запуск.",
            "Ничего не устанавливай без объяснения.",
            "Сначала предложи план: что уже есть, чего не хватает, какие зависимости нужны и зачем.",
            "```",
            "",
        ]
    )
    audit_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return [audit_path.name]


def unique_setup_audit_path(target_root: Path) -> Path:
    audit_path = target_root / "SETUP_AUDIT.md"
    if not audit_path.exists():
        return audit_path

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for index in range(1, 1000):
        candidate = target_root / f"SETUP_AUDIT-{timestamp}-{index}.md"
        if not candidate.exists():
            return candidate

    raise RuntimeError("Could not choose a unique SETUP_AUDIT filename.")


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


def write_vibe_setup_file(target_root: Path, args: argparse.Namespace) -> list[str]:
    setup_file = target_root / "VIBE_SETUP.md"
    if setup_file.exists():
        return []

    created: list[str] = []
    lines = [
        "# Vibe Coding Setup",
        "",
        f"- Project name: {args.project_name}",
        f"- Project type: {args.project_type}",
        f"- Active surfaces: {', '.join(args.active_surfaces)}",
        f"- Deployment plan: {DEPLOYMENT_PLANS[args.deployment_plan]}",
        "- Start with `START_HERE.md`, `PRD.md`, `TASKS.md`, and `wiki/how-to-work-with-ai.md`.",
    ]

    if args.features:
        lines.extend(["", "## Selected Feature Packs", ""])
        for feature in args.features:
            lines.append(f"- {FEATURES[feature]}: see `wiki/features/{feature}.md` and `prompts/features/{feature}.md`.")

    setup_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    created.append("VIBE_SETUP.md")
    return created


def install_project_pack(args: argparse.Namespace) -> list[str]:
    target_root = Path(args.target_path).expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        raise RuntimeError(f"Existing project folder was not found: {target_root}")

    created = write_setup_audit(target_root, args)
    if args.skip_workflow_docs:
        return created

    created.extend(copy_template_tree(PROJECT_PACK_ROOT / "base", target_root, args))
    for feature in args.features:
        created.extend(copy_template_tree(PROJECT_PACK_ROOT / "features" / feature, target_root, args))
    created.extend(write_vibe_setup_file(target_root, args))
    return created


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install vibe-coding workflow docs into an existing project.")
    parser.add_argument("--target-path", default=".", help="Existing project folder. Defaults to current directory.")
    parser.add_argument("--project-name", help="Project display name. Defaults to target folder name.")
    parser.add_argument(
        "--project-type",
        choices=tuple(PROJECT_TYPES),
        default="mobile-web-app",
        help="Existing project type.",
    )
    parser.add_argument(
        "--active-surfaces",
        type=parse_csv,
        default=None,
        help="Comma-separated surfaces. Defaults from --project-type.",
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
    parser.add_argument(
        "--skip-workflow-docs",
        action="store_true",
        help="Only create SETUP_AUDIT.md; do not add starter docs/prompts.",
    )

    args = parser.parse_args(argv)
    target_root = Path(args.target_path).expanduser().resolve()
    if not args.project_name:
        args.project_name = target_root.name
    if args.active_surfaces is None:
        args.active_surfaces = PROJECT_TYPE_SURFACES[args.project_type]
    if args.project_type not in HOSTING_PROJECT_TYPES:
        args.deployment_plan = "decide-later"
    try:
        args.features = normalize_features(args.project_type, args.features)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    try:
        created = install_project_pack(args)
    except RuntimeError as exc:
        parser.error(str(exc))
    if created:
        print("Project workflow pack installed:", ", ".join(created))
    else:
        print("Project workflow pack already present. No files changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
