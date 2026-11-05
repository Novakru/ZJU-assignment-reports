param([string]$PythonCommand = 'python', [switch]$RunExperiments)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if ($RunExperiments) {
        & $PythonCommand 'experients/assignment2/run_experiments.py'
        if ($LASTEXITCODE -ne 0) { throw 'Experiments failed.' }
    }
    & $PythonCommand 'experients/assignment2/checks.py'
    if ($LASTEXITCODE -ne 0) { throw 'Behavioral verification failed.' }
    & $PythonCommand 'report/generate.py'
    if ($LASTEXITCODE -ne 0) { throw 'Report data generation failed.' }
} finally { Pop-Location }
Push-Location $PSScriptRoot
try {
    for ($pass = 1; $pass -le 2; $pass++) {
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error report.tex
        if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass $pass failed." }
    }
    $issues = Select-String -LiteralPath report.log -Pattern 'Overfull|Missing character|undefined references|LaTeX Font Warning|Package .+ Warning'
    if ($issues) {
        $issues | ForEach-Object { Write-Warning $_.Line }
        throw 'Resolve layout, reference, or font warnings before accepting the PDF.'
    }
    Copy-Item -LiteralPath report.pdf -Destination ../submission/report.pdf -Force
    $sourceHashes = [ordered]@{}
    foreach ($relativePath in @('report/report.tex', 'report/assignment.sty', 'report/student-info.tex',
                                'report/generate.py', 'submission/solve.py', 'submission/uttt.py',
                                'experients/assignment2/results.json')) {
        $sourceHashes[$relativePath] = (Get-FileHash -LiteralPath (Join-Path $repoRoot $relativePath) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $humanLog = Join-Path $repoRoot 'experients/assignment2/human_games.json'
    $humanGames = 0
    if (Test-Path -LiteralPath $humanLog) {
        $humanGames = @(Get-Content -LiteralPath $humanLog -Raw -Encoding UTF8 | ConvertFrom-Json).Count
    }
    $record = [ordered]@{
        template_base = 'main@cc1fa9c and assignment1-cs1050 coursework layout'
        behavioral_checks_passed = $true
        xelatex_passes = 2
        latex_layout_or_reference_issues = $false
        human_games = $humanGames
        human_requirement_satisfied = ($humanGames -ge 10)
        report_pdf_sha256 = (Get-FileHash -LiteralPath report.pdf -Algorithm SHA256).Hash.ToLowerInvariant()
        source_sha256 = $sourceHashes
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $repoRoot 'experients/assignment2/build.json'),
                          (($record | ConvertTo-Json -Depth 4) + "`n"), $utf8)
    Write-Output 'Built report/report.pdf and submission/report.pdf'
} finally { Pop-Location }
