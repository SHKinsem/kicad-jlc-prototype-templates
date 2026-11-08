param([string]$Destination)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Destination) {
    $Destination = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'KiCad\10.0\template'
}
$destinationRoot = [IO.Path]::GetFullPath($Destination)
$templateNames = @('jlc-2layer-1oz-prototype', 'jlc-4layer-1oz-prototype')
New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
foreach ($templateName in $templateNames) {
    $source = Join-Path (Join-Path $repoRoot 'templates') $templateName
    $target = Join-Path $destinationRoot $templateName
    if (Test-Path -LiteralPath $target) {
        $sourceFiles = Get-ChildItem -LiteralPath $source -File -Recurse
        $targetFiles = Get-ChildItem -LiteralPath $target -File -Recurse
        $same = $sourceFiles.Count -eq $targetFiles.Count
        foreach ($file in $sourceFiles) {
            $relative = $file.FullName.Substring($source.Length).TrimStart([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
            $peer = Join-Path $target $relative
            if (-not (Test-Path -LiteralPath $peer) -or
                (Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $peer).Hash) {
                $same = $false
            }
        }
        if (-not $same) { throw "Existing template differs; no overwrite performed: $target" }
        Write-Output "Already installed: $templateName"
        continue
    }
    Copy-Item -LiteralPath $source -Destination $target -Recurse
    Write-Output "Installed: $target"
}
