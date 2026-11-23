"""Rebuild and validate all coursework deliverables in the local repository."""
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(command, env=None, label='build'):
    result = subprocess.run([str(x) for x in command], cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logs = ROOT/'.build/logs'
    logs.mkdir(parents=True, exist_ok=True)
    (logs/(label+'.txt')).write_bytes(result.stdout)
    if result.returncode:
        print(result.stdout.decode('utf-8',errors='replace')[-8000:])
        raise SystemExit(result.returncode)
    print(label + ': complete')

def runtime_environment():
    env = os.environ.copy()
    modules = env.get('RUNTIME_NODE_MODULES') or env.get('CODEX_PRIMARY_RUNTIME_NODE_MODULES')
    if not modules:
        # WindowsApps permits access to the active package but can hide directory
        # enumeration. Resolve it from bundled executables already on PATH first.
        for binary in ['pdftoppm','pdfinfo','git']:
            executable=shutil.which(binary)
            if executable:
                for parent in Path(executable).parents:
                    candidate=parent/'dependencies/node/node_modules'
                    if (candidate/'@oai/artifact-tool').is_dir():
                        modules=str(candidate)
                        break
            if modules: break
    if not modules:
        candidates = sorted(Path(r'C:\Program Files\WindowsApps').glob(
            'OpenAI.CodexPrimaryRuntime.*/dependencies/node/node_modules'),reverse=True)
        if not candidates:
            raise RuntimeError('Codex bundled Node runtime not found. Set RUNTIME_NODE_MODULES.')
        modules = str(candidates[0])
    env['RUNTIME_NODE_MODULES'] = modules
    node = Path(modules).parent/'bin/node.exe'
    if not node.exists():
        found = shutil.which('node')
        if not found: raise RuntimeError('Node executable not found.')
        node = Path(found)
    if not env.get('PRESENTATIONS_SKILL_DIR'):
        base = Path.home()/'.codex/plugins/cache/openai-primary-runtime/presentations'
        candidates = sorted(base.glob('*/skills/presentations'),reverse=True)
        if not candidates: raise RuntimeError('Bundled presentation skill not found.')
        env['PRESENTATIONS_SKILL_DIR'] = str(candidates[0])
    env['PRESENTATIONS_PYTHON'] = sys.executable
    env['PYTHONIOENCODING'] = 'utf-8'
    return env,node

def write_speaker_notes(language):
    english = language == 'en'
    notes_file = 'notes-en.json' if english else 'notes.json'
    data = json.loads((ROOT/'presentation'/notes_file).read_text(encoding='utf-8'))
    total = sum(item['seconds'] for item in data['slides'])
    lines = (['ACE English speaker notes', 'Jiahao Jiang / 22671064',
              f'Main presentation: {total} seconds with {360-total} seconds for transitions.',
              'Slides 10 and 11 are hidden backup slides.', ''] if english else
             ['ACE 中文展示讲稿', '蒋佳豪 / Jiahao Jiang / 22671064',
              f'正式部分 {total} 秒，预留 {360-total} 秒切页。',
              '第 10、11 页为隐藏备份页。', ''])
    elapsed=0
    for i,item in enumerate(data['slides'],1):
        if item.get('hidden'):
            timing='Backup' if english else '问答备份'
        else:
            start=elapsed;elapsed+=item['seconds']
            timing=f'{start//60}:{start%60:02d}–{elapsed//60}:{elapsed%60:02d}'
        page_label = f'Slide {i}' if english else f'第 {i} 页'
        lines.extend([f'{page_label}  {item["title"]}  ({timing})',item['speech'],'',
                      'Sources' if english else '参考来源',*item['sources'],'',''])
    (ROOT/'review').mkdir(exist_ok=True)
    with (ROOT/f'review/speaker-notes-{language}.txt').open('w',encoding='utf-8-sig',newline='\n') as handle:
        handle.write('\n'.join(lines).rstrip()+'\n')

def build_presentation(language, env, node, temporary):
    temporary.mkdir()
    language_args = ['--language', language]
    run([node,'presentation/build_content.mjs',language],env,f'slide-content-{language}')
    run([sys.executable,'tools/assemble_template.py',*language_args],env,f'template-assembly-{language}')
    assembled = ROOT/'.build'/language/'presentation-assembled.pptx'
    checked = temporary/'checked.pptx'
    run([node,'tools/finalize_presentation.mjs',assembled,checked],env,f'pptx-structural-check-{language}')
    native = temporary/'native.pptx'
    run([sys.executable,'tools/native_presentation.py','--input',checked,'--output',native,
         *language_args],env,f'powerpoint-native-check-{language}')
    refreshed = temporary/'refreshed.pptx'
    run([sys.executable,'tools/refresh_chart_cache.py',native,refreshed],env,f'chart-cache-refresh-{language}')
    final = temporary/'final.pptx'
    run([node,'tools/finalize_presentation.mjs',refreshed,final],env,f'pptx-final-check-{language}')
    if refreshed.read_bytes()!=final.read_bytes():
        raise RuntimeError('Finalization changed the verified chart data.')
    english = language == 'en'
    destination = 'submission/presentation.pptx' if english else 'review/presentation-zh.pptx'
    preview = 'review/presentation-preview-en.pdf' if english else 'review/presentation-preview.pdf'
    run([sys.executable,'tools/native_presentation.py','--input',final,'--render-only',*language_args,
         '--render-dir',f'review/previews/{language}','--pdf',preview],env,f'final-powerpoint-preview-{language}')
    shutil.copyfile(final,ROOT/destination)
    write_speaker_notes(language)

def main():
    env,node=runtime_environment()
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
    temporary=ROOT/'.build/validated'/stamp
    temporary.mkdir(parents=True,exist_ok=False)
    run([sys.executable,'tools/build_report.py'],env,'report')
    for language in ['en', 'zh']:
        build_presentation(language, env, node, temporary/language)
    run([sys.executable,'tools/validate_artifacts.py'],env,'deliverable-check')
    print('Built English submission files and Chinese review files.')

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
