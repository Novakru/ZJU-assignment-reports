"""Build both reading reports using the shared XeLaTeX template."""
from pathlib import Path
import shutil
import subprocess
import fitz

ROOT = Path(__file__).resolve().parents[1]

def main():
    build = ROOT / '.build' / 'report'
    build.mkdir(parents=True, exist_ok=True)
    destinations = {'report': 'submission/report.pdf', 'report-zh': 'review/report-zh.pdf'}
    for stem in destinations:
        command = ['latexmk', '-xelatex', '-interaction=nonstopmode', '-halt-on-error',
                   '-outdir=../.build/report', f'{stem}.tex']
        result = subprocess.run(command, cwd=ROOT/'report', stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        (build/f'{stem}-build-output.txt').write_bytes(result.stdout)
        if result.returncode:
            print(result.stdout.decode('utf-8', errors='replace')[-6000:])
            raise SystemExit(result.returncode)
        with fitz.open(build/f'{stem}.pdf') as document:
            if len(document) != 2 or any(not page.get_text().strip() for page in document):
                raise RuntimeError(f'{stem} must have exactly two nonblank pages.')
    for stem, destination in destinations.items():
        target = ROOT/destination
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(build/f'{stem}.pdf', target)
    print('English and Chinese reports compiled: two pages each, including references.')

if __name__ == '__main__':
    main()
