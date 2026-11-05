param([string]$PythonCommand = 'python', [switch]$RunExperiments)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if ($RunExperiments) {
        & $PythonCommand -B 'experients/assignment2/run_experiments.py'
        if ($LASTEXITCODE -ne 0) { throw 'Experiments failed.' }
    }
    if ($RunExperiments -or -not (Test-Path -LiteralPath 'experients/assignment2/extra_results.json')) {
        & $PythonCommand -B 'experients/assignment2/run_extra.py'
        if ($LASTEXITCODE -ne 0) { throw 'Global-rule experiment failed.' }
    }
    & $PythonCommand -B 'experients/assignment2/checks.py'
    if ($LASTEXITCODE -ne 0) { throw 'Behavioral verification failed.' }
    & $PythonCommand -B 'experients/assignment2/check_extra.py'
    if ($LASTEXITCODE -ne 0) { throw 'Global-rule verification failed.' }
    foreach ($language in @('zh', 'en')) {
        & $PythonCommand -B 'report/generate.py' --language $language
        if ($LASTEXITCODE -ne 0) { throw "Report data generation failed: $language" }
    }
} finally { Pop-Location }
Push-Location $PSScriptRoot
try {
    foreach ($stem in @('report', 'report-en')) {
        for ($pass = 1; $pass -le 2; $pass++) {
            & xelatex -interaction=nonstopmode -halt-on-error -file-line-error "$stem.tex"
            if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass $pass failed: $stem" }
        }
        $issues = Select-String -LiteralPath "$stem.log" -Pattern 'Overfull|Missing character|undefined references|LaTeX Font Warning|Package .+ Warning'
        if ($issues) {
            $issues | ForEach-Object { Write-Warning $_.Line }
            throw "Resolve layout, reference, or font warnings: $stem"
        }
    }
    Copy-Item -LiteralPath report.pdf -Destination ../submission/report.pdf -Force
    $sourceHashes = [ordered]@{}
    foreach ($relativePath in @('report/report.tex', 'report/report-en.tex', 'report/assignment.sty', 'report/student-info.tex',
                                'report/build.ps1',
                                'report/generate.py', 'submission/solve.py', 'submission/uttt.py',
                                'experients/assignment2/results.json', 'experients/assignment2/extra_results.json',
                                'experients/assignment2/run_extra.py', 'experients/assignment2/check_extra.py',
                                'experients/assignment2/human-notes.json')) {
        $sourceHashes[$relativePath] = (Get-FileHash -LiteralPath (Join-Path $repoRoot $relativePath) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $humanLog = Join-Path $repoRoot 'experients/assignment2/human_games.json'
    $humanGames = 0
    if (Test-Path -LiteralPath $humanLog) {
        $humanGames = @(Get-Content -LiteralPath $humanLog -Raw -Encoding UTF8 | ConvertFrom-Json).Count
        $sourceHashes['experients/assignment2/human_games.json'] = (Get-FileHash -LiteralPath $humanLog -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $record = [ordered]@{
        template_base = 'main@cc1fa9c and assignment1-cs1050 coursework layout'
        behavioral_checks_passed = $true
        xelatex_passes_per_language = 2
        languages = @('zh', 'en')
        latex_layout_or_reference_issues = $false
        human_games = $humanGames
        human_requirement_satisfied = ($humanGames -ge 10)
        global_rule_checks_passed = $true
        extra_games = @((Get-Content -LiteralPath (Join-Path $repoRoot 'experients/assignment2/extra_results.json') -Raw -Encoding UTF8 | ConvertFrom-Json).games).Count
        report_pdf_sha256 = (Get-FileHash -LiteralPath report.pdf -Algorithm SHA256).Hash.ToLowerInvariant()
        english_pdf_sha256 = (Get-FileHash -LiteralPath report-en.pdf -Algorithm SHA256).Hash.ToLowerInvariant()
        course = 'ECE2013'
        term = 'Fall 2026'
        group = 6
        contribution_allocation = 'proposed; pending group confirmation'
        source_sha256 = $sourceHashes
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $repoRoot 'experients/assignment2/build.json'),
                          (($record | ConvertTo-Json -Depth 4) + "`n"), $utf8)
    Write-Output 'Built Chinese report/report.pdf, English report/report-en.pdf, and submission/report.pdf (Chinese).'
} finally { Pop-Location }
