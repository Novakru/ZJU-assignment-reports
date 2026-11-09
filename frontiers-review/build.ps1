param([string]$PythonCommand='python')
$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Force -Path 'tmp/pdfs','output/pdf' | Out-Null
    & $PythonCommand -B format_references.py
    if ($LASTEXITCODE -ne 0) { throw 'Reference ordering failed.' }
    & $PythonCommand -B make_review_diagrams.py
    if ($LASTEXITCODE -ne 0) { throw 'Published-data figure generation failed.' }
    foreach ($stem in @('report','materials','review')) {
        $passes=if ($stem -eq 'review') {3} else {2}
        for ($pass=1; $pass -le $passes; $pass++) {
            & xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=tmp/pdfs "$stem.tex"
            if ($LASTEXITCODE -ne 0) { throw "XeLaTeX failed: $stem pass $pass" }
        }
        $issues=Select-String -LiteralPath "tmp/pdfs/$stem.log" -Pattern 'Overfull|Missing character|undefined references|LaTeX Font Warning|Package .+ Warning'
        # The official AAS class combines ccaption and caption. It intentionally
        # uses standard caption defaults; our adaptation sets the final style.
        $issues=$issues | Where-Object { $_.Line -notmatch '^Package caption Warning: Unknown document class' }
        if ($issues) {
            $issues | ForEach-Object { Write-Warning $_.Line }
            throw "Resolve PDF layout or references: $stem"
        }
    }
    Copy-Item -LiteralPath 'tmp/pdfs/report.pdf' -Destination 'output/pdf/literature-review-layout.pdf' -Force
    Copy-Item -LiteralPath 'tmp/pdfs/materials.pdf' -Destination 'output/pdf/reading-and-writing-guide.pdf' -Force
    Copy-Item -LiteralPath 'tmp/pdfs/review.pdf' -Destination 'output/pdf/multi-agent-literature-review.pdf' -Force
    $metadata=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'metadata.tex'),[Text.Encoding]::UTF8)
    $author=[regex]::Match($metadata,'\\newcommand\{\\AuthorName\}\{([^}]+)\}').Groups[1].Value
    $student=[regex]::Match($metadata,'\\newcommand\{\\StudentID\}\{([^}]+)\}').Groups[1].Value
    if (-not $author -or $student -notmatch '^\d+$') { throw 'Missing author or student ID.' }
    $filename="$author$student.pdf"
    Copy-Item -LiteralPath 'tmp/pdfs/review.pdf' -Destination (Join-Path 'output/pdf' $filename) -Force
    & $PythonCommand -B verify.py
    if ($LASTEXITCODE -ne 0) { throw 'Artifact verification failed.' }
    & $PythonCommand -B verify_review.py
    if ($LASTEXITCODE -ne 0) { throw 'Complete review verification failed.' }
    $review=Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'review'
    New-Item -ItemType Directory -Force -Path $review | Out-Null
    Copy-Item -LiteralPath 'output/pdf/literature-review-layout.pdf' -Destination (Join-Path $review 'literature-review-layout.pdf') -Force
    Copy-Item -LiteralPath 'output/pdf/reading-and-writing-guide.pdf' -Destination (Join-Path $review 'reading-and-writing-guide.pdf') -Force
    Copy-Item -LiteralPath 'output/pdf/multi-agent-literature-review.pdf' -Destination (Join-Path $review 'multi-agent-literature-review.pdf') -Force
    Copy-Item -LiteralPath 'tmp/pdfs/review.pdf' -Destination (Join-Path $review $filename) -Force
    $submission=Join-Path (Split-Path -Parent $review) 'submission'
    New-Item -ItemType Directory -Force -Path $submission | Out-Null
    Copy-Item -LiteralPath 'tmp/pdfs/review.pdf' -Destination (Join-Path $submission $filename) -Force
    Write-Output 'Built the revised journal-style review, packaged the correctly named PDF, and retained supporting materials separately. Author review remains pending.'
} finally { Pop-Location }
