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
        Branches = @('master', 'mobile')
    }
    'chrome-extension' = @{
        Path = 'vite-web-extension-upstream-archive'
        Url = 'https://github.com/JohnBra/vite-web-extension.git'
        Branches = @('main')
    }
    'design-shadcn-ui' = @{
        Path = 'design-shadcn-ui-archive'
        Url = 'https://github.com/shadcn-ui/ui.git'
        Branches = @('main')
    }
    'design-magic-ui' = @{
        Path = 'design-magic-ui-archive'
        Url = 'https://github.com/magicuidesign/magicui.git'
        Branches = @('main')
    }
    'design-origin-ui' = @{
        Path = 'design-origin-ui-archive'
        Url = 'https://github.com/shadcn/originui.git'
        Branches = @('main')
    }
    'design-react-native-reusables' = @{
        Path = 'design-react-native-reusables-archive'
        Url = 'https://github.com/founded-labs/react-native-reusables.git'
        Branches = @('main')
    }
}

function Sync-Archive {
    param(
        [string]$Name,
        [string]$ArchivePath,
        [string]$SourceUrl,
        [string[]]$LocalBranches = @()
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

    foreach ($branch in $LocalBranches) {
        $remoteBranch = "origin/$branch"
        git -C $resolvedArchivePath rev-parse --verify --quiet $remoteBranch | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Expected archive branch '$remoteBranch' was not found in $resolvedArchivePath"
        }

        $currentBranch = git -C $resolvedArchivePath branch --show-current
        if ($LASTEXITCODE -ne 0) {
            throw "Could not read current archive branch in $resolvedArchivePath"
        }

        if ($currentBranch.Trim() -eq $branch) {
            git -C $resolvedArchivePath merge --ff-only $remoteBranch | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "Could not fast-forward current archive branch '$branch' in $resolvedArchivePath"
            }
        } else {
            git -C $resolvedArchivePath branch --force $branch $remoteBranch | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "Could not update local archive branch '$branch' in $resolvedArchivePath"
            }
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
    if ($LocalBranches.Count -gt 0) {
        Write-Output "Local fallback branches: $($LocalBranches -join ', ')"
    }
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
    Sync-Archive -Name $name -ArchivePath (Join-Path $ArchiveRoot $archive.Path) -SourceUrl $archive.Url -LocalBranches $archive.Branches
}
