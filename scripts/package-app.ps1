[CmdletBinding()]
param(
    [string]$OutputDir = '',
    [string]$PackageName = 'vibe-project-installer-portable',
    [switch]$KeepStaging
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $repoRoot 'dist'
}
$resolvedOutputDir = [IO.Path]::GetFullPath($OutputDir)
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stagingRoot = Join-Path $resolvedOutputDir "$PackageName-$timestamp"
$zipPath = "$stagingRoot.zip"

$excludeDirs = @(
    '.git',
    '.agents',
    '.codex',
    '.obsidian',
    '.scratch',
    'dist',
    'node_modules',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    'coverage'
)

$excludeFiles = @(
    '*.pyc',
    '*.pyo',
    '.DS_Store',
    'Thumbs.db'
)

function Test-ExcludedPath {
    param([string]$RelativePath)

    $parts = $RelativePath -split '[\\/]'
    foreach ($part in $parts) {
        if ($excludeDirs -contains $part) {
            return $true
        }
    }

    $leaf = Split-Path -Leaf $RelativePath
    foreach ($pattern in $excludeFiles) {
        if ($leaf -like $pattern) {
            return $true
        }
    }

    return $false
}

if (-not (Test-Path -LiteralPath $resolvedOutputDir)) {
    New-Item -ItemType Directory -Path $resolvedOutputDir -Force | Out-Null
}

if (Test-Path -LiteralPath $stagingRoot) {
    Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $stagingRoot -Force | Out-Null

function Copy-PackageTree {
    param(
        [string]$SourceDir,
        [string]$DestinationDir
    )

    Get-ChildItem -LiteralPath $SourceDir -Force | ForEach-Object {
        $relativePath = $_.FullName.Substring($repoRoot.Length).TrimStart('\', '/')
        if (Test-ExcludedPath -RelativePath $relativePath) {
            return
        }

        $destination = Join-Path $DestinationDir $_.Name
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
            Copy-PackageTree -SourceDir $_.FullName -DestinationDir $destination
        } else {
            Copy-Item -LiteralPath $_.FullName -Destination $destination -Force
        }
    }
}

Copy-PackageTree -SourceDir $repoRoot -DestinationDir $stagingRoot

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -LiteralPath $stagingRoot -DestinationPath $zipPath -Force

Write-Output "Package created: $zipPath"
if ($KeepStaging) {
    Write-Output "Staging folder: $stagingRoot"
} else {
    Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}
