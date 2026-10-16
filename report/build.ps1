param(
    [string]$PythonCommand = 'python'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    & $PythonCommand 'experients/assignment1/run.py'
    if ($LASTEXITCODE -ne 0) { throw 'Experiment or verification failed.' }
} finally {
    Pop-Location
}

Push-Location $PSScriptRoot
try {
    # Two passes resolve total page count and internal links.
    for ($pass = 1; $pass -le 2; $pass++) {
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error report.tex
        if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass $pass failed." }
    }
    $layoutProblems = Select-String -LiteralPath 'report.log' -Pattern 'Overfull|Missing character|undefined references|LaTeX Font Warning|Package .+ Warning'
    if ($layoutProblems) {
        $layoutProblems | ForEach-Object { Write-Warning $_.Line }
        throw 'Resolve the LaTeX layout/reference/font warnings before accepting the PDF.'
    }

    # Separate final artifact record avoids a circular hash in the PDF manifest.
    $record = [ordered]@{
        command = 'powershell -NoProfile -File report/build.ps1'
        experiments_passed = $true
        xelatex_passes = 2
        latex_warnings_or_overflow = $false
        report_pdf_sha256 = (Get-FileHash -LiteralPath 'report.pdf' -Algorithm SHA256).Hash.ToLowerInvariant()
        manifest_sha256 = (Get-FileHash -LiteralPath '../experients/assignment1/results/manifest.json' -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $recordJson = ($record | ConvertTo-Json) + "`n"
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path $repoRoot 'experients/assignment1/results/build.json'), $recordJson, $utf8)
    Write-Output "Built: $(Join-Path $PSScriptRoot 'report.pdf')"
    if (Select-String -LiteralPath 'student-info.tex' -Pattern '\[YOUR (NAME|STUDENT ID)\]' -Quiet) {
        Write-Warning 'Fill in Name and Student ID in report/student-info.tex before submission.'
    }
} finally {
    Pop-Location
}
