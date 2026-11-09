param([string]$PythonCommand='python')
$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Force -Path 'tmp/pdfs','output/pdf' | Out-Null
    foreach ($stem in @('report','materials')) {
        for ($pass=1; $pass -le 2; $pass++) {
            & xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=tmp/pdfs "$stem.tex"
            if ($LASTEXITCODE -ne 0) { throw "XeLaTeX failed: $stem pass $pass" }
        }
        $issues=Select-String -LiteralPath "tmp/pdfs/$stem.log" -Pattern 'Overfull|Missing character|undefined references|LaTeX Font Warning|Package .+ Warning'
        if ($issues) {
            $issues | ForEach-Object { Write-Warning $_.Line }
            throw "Resolve PDF layout or references: $stem"
        }
    }
    Copy-Item -LiteralPath 'tmp/pdfs/report.pdf' -Destination 'output/pdf/literature-review-layout.pdf' -Force
    Copy-Item -LiteralPath 'tmp/pdfs/materials.pdf' -Destination 'output/pdf/reading-and-writing-guide.pdf' -Force
    & $PythonCommand -B verify.py
    if ($LASTEXITCODE -ne 0) { throw 'Artifact verification failed.' }
    $review=Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'review'
    New-Item -ItemType Directory -Force -Path $review | Out-Null
    Copy-Item -LiteralPath 'output/pdf/literature-review-layout.pdf' -Destination (Join-Path $review 'literature-review-layout.pdf') -Force
    Copy-Item -LiteralPath 'output/pdf/reading-and-writing-guide.pdf' -Destination (Join-Path $review 'reading-and-writing-guide.pdf') -Force
    Write-Output 'Built two Chinese preparation PDFs. These are not submission-ready coursework.'
} finally { Pop-Location }
