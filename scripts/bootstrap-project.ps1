[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$ProjectName,

    [string[]]$ActiveSurfaces,

    [string]$SourceUrl,

    [string]$Branch = '',

    [ValidateSet('none', 'custom', 'digitalocean', 'yandex')]
    [string]$Hosting = 'custom',

    [switch]$KeepTemplateRemote
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Split-Path -Parent $scriptRoot
$knownSurfaces = @('web', 'mobile', 'backend', 'landing')

function Resolve-Surfaces {
    param([string[]]$Requested)

    if ($Requested -and $Requested.Count -gt 0) {
        $normalized = $Requested | ForEach-Object {
            $value = $_.Trim().ToLowerInvariant()
            switch ($value) {
                'full' { 'full-stack' }
                'fullstack' { 'full-stack' }
                'api' { 'backend' }
                'backend/api' { 'backend' }
                default { $value }
            }
        } | Where-Object { $_ }

        foreach ($surface in $normalized) {
            if ($surface -eq 'full-stack') {
                return $knownSurfaces
            }
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
        git clone --depth 1 $Url $Destination
    } else {
        git clone --depth 1 --branch $GitBranch $Url $Destination
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
- Hosting mode: none
- Deployment scope: local development only. Do not configure cloud resources until deployment is explicitly requested.
"@
        }
        'custom' {
@"
- Hosting mode: custom/provider-neutral
- Deployment scope: choose the provider later from product needs, budget, region, database, file storage, and operations requirements.
- Do not assume DigitalOcean or Yandex Cloud unless the project README is updated with that choice.
"@
        }
        'digitalocean' {
@"
- Hosting mode: DigitalOcean
- Deployment scope: follow `docs/DEPLOYMENT.md`, generate specs with `bun run deploy:do:specs`, and keep generated specs under `.scratch/deploy`.
"@
        }
        'yandex' {
@"
- Hosting mode: Yandex Cloud
- Deployment scope: follow `docs/YANDEX_CLOUD.md` and use `yc`/Yandex services only after the account, folder, domains, and credentials are confirmed.
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
        'landing' { @('landing\README.md', 'website\README.md') }
        default { @("$surface\README.md") }
    }

    foreach ($relativeReadme in $readmeCandidates) {
        $surfacePath = Join-Path $resolvedTarget $relativeReadme
        Update-SurfaceReadme -ReadmePath $surfacePath -IsActive ($resolvedActive -contains $surface)
    }
}

Write-Output "Installed vibe template into $resolvedTarget"
Write-Output "Project name: $resolvedProjectName"
Write-Output "Active surfaces: $($resolvedActive -join ', ')"
Write-Output "Hosting mode: $Hosting"
if (-not [string]::IsNullOrWhiteSpace($SourceUrl) -and -not $KeepTemplateRemote) {
    Write-Output 'Template origin remote removed. Add your own project origin when publishing is needed.'
}
