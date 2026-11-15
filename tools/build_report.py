"""Build the English report using the repository's XeLaTeX template family."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import fitz

ROOT = Path(__file__).resolve().parents[1]

def main():
    build = ROOT / '.build' / 'report'
    build.mkdir(parents=True, exist_ok=True)
    command = ['latexmk', '-xelatex', '-interaction=nonstopmode', '-halt-on-error',
               '-outdir=../.build/report', 'report.tex']
    result = subprocess.run(command, cwd=ROOT/'report', stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    (build/'build-output.txt').write_bytes(result.stdout)
    if result.returncode:
        print(result.stdout.decode('utf-8', errors='replace')[-6000:])
        raise SystemExit(result.returncode)
    pdf = build / 'report.pdf'
    document = fitz.open(pdf)
    if len(document) != 2:
        raise RuntimeError(f'Course limit: expected two pages, found {len(document)}.')
    for page in document:
        if not page.get_text().strip():
            raise RuntimeError('Blank report page.')
    (ROOT/'submission').mkdir(exist_ok=True)
    shutil.copyfile(pdf, ROOT/'submission/report.pdf')
    print('English report compiled: 2 pages, including references.')

if __name__ == '__main__':
    main()
