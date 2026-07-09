[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$ProjectName,

    [string[]]$ActiveSurfaces,

    [string]$SourceUrl,

    [string]$Branch = '',

    [ValidateSet('none', 'custom', 'digitalocean')]
    [string]$Hosting = 'custom',

    [switch]$KeepTemplateRemote,

    [switch]$SkipWorkflowDocs
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Split-Path -Parent $scriptRoot
$knownSurfaces = @('website', 'web', 'mobile', 'backend', 'landing', 'desktop-python', 'chrome-extension')
$fullStackSurfaces = @('website', 'web', 'mobile', 'backend')

function Resolve-Surfaces {
    param([string[]]$Requested)

    if ($Requested -and $Requested.Count -gt 0) {
        $normalized = $Requested | ForEach-Object {
            $_ -split ','
        } | ForEach-Object {
            $value = $_.Trim().ToLowerInvariant()
            switch ($value) {
                'full' { 'full-stack' }
                'fullstack' { 'full-stack' }
                'api' { 'backend' }
                'backend/api' { 'backend' }
                'site' { 'website' }
                'web-site' { 'website' }
                'desktop' { 'desktop-python' }
                'python-desktop' { 'desktop-python' }
                default { $value }
            }
        } | Where-Object { $_ }

        foreach ($surface in $normalized) {
            if ($surface -eq 'full-stack') {
                return $fullStackSurfaces
            }
        }

        if (($normalized -contains 'chrome-extension') -and ($normalized.Count -gt 1)) {
            throw 'chrome-extension cannot be combined with website, web, mobile, backend, landing, desktop-python, or full-stack. Create it as a separate project template.'
        }

        if (($normalized -contains 'desktop-python') -and ($normalized.Count -gt 1)) {
            throw 'desktop-python cannot be combined with website, web, mobile, backend, landing, chrome-extension, or full-stack. Create it as a separate project template.'
        }

        $invalid = $normalized | Where-Object { $knownSurfaces -notcontains $_ }
        if ($invalid.Count -gt 0) {
            throw "Unknown surface(s): $($invalid -join ', '). Use one or more of: $($knownSurfaces -join ', ') or full-stack."
        }

        return $normalized | Select-Object -Unique
    }

    $prompt = "Choose active surfaces as a comma-separated list ($($knownSurfaces -join ', '), full-stack)"
    $input = Read-Host $prompt
    if ([string]::IsNullOrWhiteSpace($input)) {
        throw 'No surfaces selected.'
    }

    return Resolve-Surfaces -Requested ($input -split ',')
}

function Copy-RepoTree {
    param(
        [string]$Source,
        [string]$Destination
    )

    $excluded = @('.git', '.scratch', 'node_modules', 'dist', 'coverage')

    if (Test-Path -LiteralPath $Destination) {
        throw "Target path already exists: $Destination"
    }

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null

    Get-ChildItem -LiteralPath $Source -Force |
        Where-Object { $excluded -notcontains $_.Name } |
        ForEach-Object {
            $dest = Join-Path $Destination $_.Name
            Copy-Item -LiteralPath $_.FullName -Destination $dest -Recurse -Force
        }
}

function Clone-RepoTree {
    param(
        [string]$Url,
        [string]$Destination,
        [string]$GitBranch,
        [bool]$KeepRemote
    )

    if (Test-Path -LiteralPath $Destination) {
        throw "Target path already exists: $Destination"
    }

    if ([string]::IsNullOrWhiteSpace($GitBranch)) {
        git clone --progress --depth 1 $Url $Destination
    } else {
        git clone --progress --depth 1 --branch $GitBranch $Url $Destination
    }
    if ($LASTEXITCODE -ne 0) {
        $branchText = if ([string]::IsNullOrWhiteSpace($GitBranch)) { 'default branch' } else { "branch $GitBranch" }
        throw "git clone failed for $Url $branchText"
    }

    if (-not $KeepRemote) {
        git -C $Destination remote remove origin
        if ($LASTEXITCODE -ne 0) {
            throw 'Template cloned, but origin remote could not be removed.'
        }
    }
}

function Get-HostingText {
    param([string]$HostingMode)

    switch ($HostingMode) {
        'none' {
@"
- Cloud setup: local only
- Cloud resources: not configured during project creation.
"@
        }
        'custom' {
@"
- Cloud setup: not configured now
- Cloud resources: choose later when the product is ready to launch.
- Do not assume DigitalOcean unless the project README is updated with that choice.
"@
        }
        'digitalocean' {
@"
- Cloud setup: DigitalOcean planned later
- Cloud resources: do not create anything until deployment is explicitly requested. Follow `docs/DEPLOYMENT.md` at launch time.
"@
        }
    }
}

function Update-SurfaceReadme {
    param(
        [string]$ReadmePath,
        [bool]$IsActive
    )

    if (-not (Test-Path -LiteralPath $ReadmePath)) {
        return
    }

    $content = Get-Content -LiteralPath $ReadmePath -Raw
    $statusText = if ($IsActive) {
@"
## Project Surface Status

This surface is active for the current project. Keep work moving here and follow the root README for setup and verification.

"@
    } else {
@"
## Project Surface Status

This surface is deferred for the current project. Do not start work here until it is activated in the root README.

"@
    }

    $pattern = '(?s)## Project Surface Status\s*\r?\n.*?(?=\r?\n## |\z)'
    if ($content -match $pattern) {
        $content = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $statusText })
    } elseif ($content -match '(?m)^# .+\r?\n') {
        $content = [regex]::Replace($content, '(?m)^(# .+\r?\n)', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) "$($m.Value)`r`n$statusText" }, 1)
    } else {
        $content = "$statusText`r`n$content"
    }

    Set-Content -LiteralPath $ReadmePath -Value $content
}

function Update-RootReadme {
    param(
        [string]$ReadmePath,
        [string]$ResolvedProjectName,
        [string[]]$Active,
        [string[]]$AllSurfaces,
        [string]$HostingMode,
        [string]$TemplateSource,
        [string]$TemplateBranch
    )

    if (-not (Test-Path -LiteralPath $ReadmePath)) {
        return
    }

    $deferred = $AllSurfaces | Where-Object { $Active -notcontains $_ }
    $deferredText = if ($deferred.Count -gt 0) { $deferred -join ', ' } else { 'none' }
    $hostingText = Get-HostingText -HostingMode $HostingMode
    $sourceText = if ([string]::IsNullOrWhiteSpace($TemplateSource)) { 'local checkout' } else { $TemplateSource }
    $branchText = if ([string]::IsNullOrWhiteSpace($TemplateBranch)) { 'default' } else { $TemplateBranch }
    $surfaceBlock = @"
## Project Bootstrap Plan

- Project name: $ResolvedProjectName
- Template source: $sourceText
- Template branch: $branchText
- Active surfaces: $($Active -join ', ')
- Deferred surfaces: $deferredText
$hostingText
"@

    $content = Get-Content -LiteralPath $ReadmePath -Raw
    if ($content -match '(?s)## Project Bootstrap Plan\s*\r?\n.*?(?=\r?\n## |\z)') {
        $content = [regex]::Replace($content, '(?s)## Project Bootstrap Plan\s*\r?\n.*?(?=\r?\n## |\z)', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $surfaceBlock })
    } else {
        $anchor = "## Agent Intake Checklist Before Installing"
        if ($content.Contains($anchor)) {
            $content = $content.Replace($anchor, "$surfaceBlock`r`n`r`n$anchor")
        } else {
            $content = "$surfaceBlock`r`n`r`n$content"
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($ResolvedProjectName)) {
        $content = $content.Replace('# Vibe Coding Template', "# $ResolvedProjectName")
    }

    Set-Content -LiteralPath $ReadmePath -Value $content
}

function New-TextFileIfMissing {
    param(
        [string]$Path,
        [string]$Content
    )

    if (Test-Path -LiteralPath $Path) {
        return $false
    }

    $parent = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    Set-Content -LiteralPath $Path -Value $Content
    return $true
}

function Get-SurfaceGuideText {
@"
# Project Surfaces

Use only the surfaces that are active for this project.

## webapp

Use for the private browser app behind login: dashboards, account screens, tools, admin panels, and app workflows that do not need SEO.

## website

Use for public pages: landing pages, SEO pages, content, public catalog pages, pricing, docs, and link previews.

## backend

Use for API, auth, database, jobs, webhooks, integrations, uploads, permissions, and business logic that must not live in the browser.

## mobile

Use only when the product needs a real mobile app. Keep mobile deferred if the MVP is web-only.

## landing

Use for a simple marketing page when the project does not need a full public website yet.

## desktop-python

Use for a simple local computer app that runs with Python. It is not a website, mobile app, or browser extension.

"@
}

function Initialize-WorkflowDocs {
    param(
        [string]$TargetRoot,
        [string]$ResolvedProjectName,
        [string[]]$Active,
        [string[]]$AllSurfaces,
        [string]$HostingMode
    )

    $activeText = $Active -join ', '
    $deferred = $AllSurfaces | Where-Object { $Active -notcontains $_ }
    $deferredText = if ($deferred.Count -gt 0) { $deferred -join ', ' } else { 'none' }

    $created = @()

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'PRD.md') -Content @"
# $ResolvedProjectName PRD

## Product Goal

Describe what this product does and which user problem it solves.

## MVP

- [ ] Define the first user journey.
- [ ] Define the main user value.
- [ ] Define what is intentionally out of scope.

## Active Surfaces

- Active: $activeText
- Deferred: $deferredText

See `wiki/project-surfaces.md` before adding work to a deferred surface.

## Core Features

1. TBD

## Acceptance Criteria

- [ ] A new user can complete the first important workflow.
- [ ] The active surfaces can be started and checked locally.
- [ ] Important errors are visible in logs or UI.

## Open Questions

Keep this section empty before implementation. Move resolved answers into the sections above.

"@) { $created += 'PRD.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'TASKS.md') -Content @"
# Tasks

## How To Use This File

Work from top to bottom. Keep each task small and check it before moving on.

## Phase 1: Product Definition

- [ ] T001: Finish `PRD.md`
  - Result: product goal, MVP, active surfaces, and acceptance criteria are clear.
  - Verify: `PRD.md` has no unresolved product questions.

- [ ] T002: Review `PRD.md` in a fresh AI context
  - Result: missing questions are found and answered.
  - Verify: updated `PRD.md` still has no TODOs in core requirements.

## Phase 2: First Working Slice

- [ ] T003: Pick the first user journey
  - Result: one small workflow is selected for implementation.
  - Verify: the workflow can be checked manually or with a test.

- [ ] T004: Implement the first working slice
  - Result: the selected workflow works on active surfaces: $activeText.
  - Verify: run the smallest relevant local check.

## Phase 3: Quality

- [ ] T005: Run code review
  - Result: serious issues are fixed or explicitly accepted.
  - Verify: review findings have file paths and evidence.

- [ ] T006: Add tests for risky behavior
  - Result: important auth, data, money, or permission behavior is protected.
  - Verify: tests fail before the fix when possible and pass after.

"@) { $created += 'TASKS.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'wiki\project-surfaces.md') -Content (Get-SurfaceGuideText)) { $created += 'wiki/project-surfaces.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'wiki\daily-workflow.md') -Content @"
# Daily Workflow

Use this when you sit down to work on the project.

1. Check `git status`.
2. Open `PRD.md` and `TASKS.md`.
3. Pick one small open task.
4. Ask the AI agent to analyze first and change nothing.
5. Approve a small plan.
6. Let the agent implement.
7. Run the shortest useful check.
8. Run code review.
9. Commit the working change.
10. Update `TASKS.md`.

Do not start a second feature until the first one is checked or intentionally paused.

"@) { $created += 'wiki/daily-workflow.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'wiki\testing.md') -Content @"
# Testing Notes

Tests are automatic checks. They help prove that important behavior still works after changes.

Add tests when work touches:

- login or accounts;
- permissions;
- payments;
- database writes;
- important user flows;
- bug fixes that could come back;
- production code that is hard to check by hand.

Prefer end-to-end or integration tests for main user flows. Use unit tests for small rules or calculations.

"@) { $created += 'wiki/testing.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'wiki\security.md') -Content @"
# Security Checklist

Before production, check:

- secrets are not committed;
- `.env` values are not printed in logs or chat;
- users cannot access other users' data by changing an id;
- protected pages require login;
- admin actions require admin permission;
- uploads are limited by type and size;
- webhooks are verified;
- error logs do not expose private data.

"@) { $created += 'wiki/security.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'prompts\prd.md') -Content @"
# Prompt: Create PRD

Давай сделаем PRD для продукта "$ResolvedProjectName".

Сначала не пиши код. Задавай мне вопросы по одному с вариантами ответа.
Когда вопросов не останется, создай PRD.md.
В PRD.md не должно быть размышлений и открытых вопросов: только четкое ТЗ, MVP, ограничения и критерии готовности.

"@) { $created += 'prompts/prd.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'prompts\tasks.md') -Content @"
# Prompt: Create Tasks

Прочитай PRD.md и создай TASKS.md.

Разбей работу на маленькие проверяемые задачи.
Укажи порядок, зависимости и проверку для каждой задачи.
Не добавляй функциональность, которой нет в PRD.

"@) { $created += 'prompts/tasks.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'prompts\one-task.md') -Content @"
# Prompt: One Task

Возьми первую открытую задачу из TASKS.md.

Сначала ничего не меняй.
Найди связанные файлы, риски и edge cases.
Предложи минимальный план.
После согласования реализуй, проверь, запусти review и обнови TASKS.md.

"@) { $created += 'prompts/one-task.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'prompts\code-review.md') -Content @"
# Prompt: Code Review

Сделай read-only code review активных изменений.

Ищи только подтвержденные серьезные проблемы:
- регрессии;
- ошибки логики;
- security/privacy risks;
- потерю данных;
- нехватку важных тестов.

Верни severity, file:line, доказательство, риск, минимальный fix и тест.

"@) { $created += 'prompts/code-review.md' }

    if (New-TextFileIfMissing -Path (Join-Path $TargetRoot 'prompts\security-review.md') -Content @"
# Prompt: Security Review

Проведи read-only security review перед production.

Проверь auth, permissions, ID enumeration, uploads, secrets, CORS, payments/webhooks, logs and dependencies.
Верни только подтвержденные проблемы с file:line, risk, fix and verification.

"@) { $created += 'prompts/security-review.md' }

    return $created
}

$resolvedTarget = [IO.Path]::GetFullPath($TargetPath)
$resolvedActive = Resolve-Surfaces -Requested $ActiveSurfaces
$resolvedProjectName = if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    Split-Path -Leaf $resolvedTarget
} else {
    $ProjectName.Trim()
}

if ([string]::IsNullOrWhiteSpace($SourceUrl)) {
    Copy-RepoTree -Source $sourceRoot -Destination $resolvedTarget
    $sourceLabel = ''
} else {
    Clone-RepoTree -Url $SourceUrl -Destination $resolvedTarget -GitBranch $Branch -KeepRemote ([bool]$KeepTemplateRemote)
    $sourceLabel = $SourceUrl
}

Update-RootReadme `
    -ReadmePath (Join-Path $resolvedTarget 'README.md') `
    -ResolvedProjectName $resolvedProjectName `
    -Active $resolvedActive `
    -AllSurfaces $knownSurfaces `
    -HostingMode $Hosting `
    -TemplateSource $sourceLabel `
    -TemplateBranch $Branch

foreach ($surface in $knownSurfaces) {
    $readmeCandidates = switch ($surface) {
        'web' { @('web\README.md', 'webapp\README.md') }
        'website' { @('website\README.md') }
        'landing' { @('landing\README.md', 'website\README.md') }
        'desktop-python' { @('README.md') }
        default { @("$surface\README.md") }
    }

    foreach ($relativeReadme in $readmeCandidates) {
        $surfacePath = Join-Path $resolvedTarget $relativeReadme
        Update-SurfaceReadme -ReadmePath $surfacePath -IsActive ($resolvedActive -contains $surface)
    }
}

$workflowDocsCreated = @()
if (-not $SkipWorkflowDocs) {
    $workflowDocsCreated = Initialize-WorkflowDocs `
        -TargetRoot $resolvedTarget `
        -ResolvedProjectName $resolvedProjectName `
        -Active $resolvedActive `
        -AllSurfaces $knownSurfaces `
        -HostingMode $Hosting
}

Write-Output "Installed template into $resolvedTarget"
Write-Output "Project name: $resolvedProjectName"
Write-Output "Active surfaces: $($resolvedActive -join ', ')"
Write-Output "Cloud setup: $Hosting"
if (-not $SkipWorkflowDocs) {
    if ($workflowDocsCreated.Count -gt 0) {
        Write-Output "Workflow docs created: $($workflowDocsCreated -join ', ')"
    } else {
        Write-Output 'Workflow docs already existed; no workflow files overwritten.'
    }
}
if (-not [string]::IsNullOrWhiteSpace($SourceUrl) -and -not $KeepTemplateRemote) {
    Write-Output 'Template origin remote removed. Add your own project origin when publishing is needed.'
}
