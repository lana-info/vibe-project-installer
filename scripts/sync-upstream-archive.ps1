[CmdletBinding()]
param(
    [string]$ArchivePath = 'D:\WorkOS\vibe-upstream-archive',

    [string]$SourceUrl = 'https://github.com/di-sukharev/vibe.git'
)

$ErrorActionPreference = 'Stop'

$resolvedArchivePath = [IO.Path]::GetFullPath($ArchivePath)
$parent = Split-Path -Parent $resolvedArchivePath
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

if (-not (Test-Path -LiteralPath $resolvedArchivePath)) {
    git clone $SourceUrl $resolvedArchivePath
    if ($LASTEXITCODE -ne 0) {
        throw "git clone failed for $SourceUrl"
    }
} else {
    if (-not (Test-Path -LiteralPath (Join-Path $resolvedArchivePath '.git'))) {
        throw "Archive path exists but is not a git checkout: $resolvedArchivePath"
    }

    $origin = git -C $resolvedArchivePath remote get-url origin
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read origin for archive: $resolvedArchivePath"
    }

    if ($origin.Trim() -ne $SourceUrl) {
        throw "Archive origin is '$($origin.Trim())', expected '$SourceUrl'."
    }

    git -C $resolvedArchivePath fetch --all --prune
    if ($LASTEXITCODE -ne 0) {
        throw "git fetch failed for archive: $resolvedArchivePath"
    }
}

$branches = git -C $resolvedArchivePath branch -r
if ($LASTEXITCODE -ne 0) {
    throw "Could not list archive branches: $resolvedArchivePath"
}

Write-Output "Upstream archive ready: $resolvedArchivePath"
Write-Output "Source: $SourceUrl"
Write-Output "Remote branches:"
$branches | ForEach-Object { Write-Output "  $($_.Trim())" }
