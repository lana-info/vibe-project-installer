[CmdletBinding()]
param(
    [string]$ArchiveRoot = 'D:\WorkOS',

    [string]$Template = 'all'
)

$ErrorActionPreference = 'Stop'

$archives = @{
    'vibe' = @{
        Path = 'vibe-upstream-archive'
        Url = 'https://github.com/di-sukharev/vibe.git'
    }
    'chrome-extension' = @{
        Path = 'vite-web-extension-upstream-archive'
        Url = 'https://github.com/JohnBra/vite-web-extension.git'
    }
}

function Sync-Archive {
    param(
        [string]$Name,
        [string]$ArchivePath,
        [string]$SourceUrl
    )

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

    $head = git -C $resolvedArchivePath rev-parse --short HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read archive HEAD: $resolvedArchivePath"
    }

    Write-Output "Archive ready: $Name"
    Write-Output "Path: $resolvedArchivePath"
    Write-Output "Source: $SourceUrl"
    Write-Output "HEAD: $head"
    Write-Output "Remote branches:"
    $branches | ForEach-Object { Write-Output "  $($_.Trim())" }
    Write-Output ""
}

$selected = if ($Template -eq 'all') {
    $archives.Keys
} else {
    if (-not $archives.ContainsKey($Template)) {
        throw "Unknown template '$Template'. Use one of: all, $($archives.Keys -join ', ')."
    }
    @($Template)
}

foreach ($name in $selected) {
    $archive = $archives[$name]
    Sync-Archive -Name $name -ArchivePath (Join-Path $ArchiveRoot $archive.Path) -SourceUrl $archive.Url
}
