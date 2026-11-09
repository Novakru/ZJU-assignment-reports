"""Check the full review draft without misreporting authorship or experiments."""
from pathlib import Path
import hashlib
import json
import re
import fitz

ROOT=Path(__file__).resolve().parent


def body_text(source):
    text=source.split('% BODY-BEGIN',1)[1].split('% BODY-END',1)[0]
    # Exclude figures/tables, headings, citations, and references from the count.
    for env in ('figure','table','tikzpicture'):
        text=re.sub(r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}','',text,flags=re.S)
    text=re.sub(r'\\(?:section|subsection|caption|label|cite|ref)\*?(?:\[[^]]*\])?\{[^}]*\}','',text)
    text=re.sub(r'%[^\n]*','',text)
    return text


def verify():
    tex=(ROOT/'review.tex').read_text(encoding='utf-8')
    characters=len(re.findall(r'[\u4e00-\u9fff]',body_text(tex)))
    assert characters>=3000,characters
    assert r'\writingtask' not in tex and '作者待完成' not in tex
    assert tex.count(r'\begin{figure}')==3
    assert tex.count(r'\begin{table}')==2
    references=(ROOT/'review-references.tex').read_text(encoding='utf-8')
    keys=re.findall(r'\\bibitem\{([^}]+)\}',references)
    citations={key for group in re.findall(r'\\cite\{([^}]+)\}',tex) for key in group.split(',')}
    assert len(keys)==10 and citations==set(keys),(keys,citations)
    manifest=json.loads((ROOT/'review-sources.json').read_text(encoding='utf-8'))
    assert len(manifest['papers'])==10
    for paper in manifest['papers']:
        assert paper['id'] in references and paper['downloaded']
        cached=ROOT/'cache'/f'{paper["id"]}.pdf'
        if cached.exists():
            assert hashlib.sha256(cached.read_bytes()).hexdigest()==paper['sha256']
    path=ROOT/'output/pdf/multi-agent-literature-review.pdf'
    doc=fitz.open(path)
    text='\n'.join(page.get_text() for page in doc)
    for fragment in ('中文文献综述初稿','摘要','关键词','结论','参考文献'):
        assert fragment in text,fragment
    assert '文献综述写作准备' not in text
    assert '作者待完成' not in text and '待读文献后填写' not in text
    assert '作者姓名待填写' in text and '学号待填写' in text
    for paper in manifest['papers']:
        assert paper['id'] in text,paper['id']
    outside=[]
    for i,page in enumerate(doc):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:
                        outside.append([i+1,span['text']])
    assert not outside,outside
    record=dict(title='面向科研任务的多智能体系统：知识增强、记忆机制与可信性评估',
                language='zh',status='complete AI-assisted draft; author information and review pending',
                pages=len(doc),body_chinese_characters_excluding_headings_figures_tables_and_references=characters,
                minimum_body_characters=3000,body_length_requirement_satisfied=True,
                figures=3,tables=2,original_research_experiments_conducted=False,
                references=10,all_references_cited=True,reference_versions_verified=True,
                no_body_placeholders=True,source_selection='representative, not exhaustive or systematic',
                author_confirmed=False,submission_ready=False,
                pending=['author name','student ID','author review and course AI-use compliance'],
                source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                  for name in ('review.tex','review.sty','metadata.tex','review-references.tex','review-sources.json','verify_review.py')},
                pdf_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (ROOT/'review-verification.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(f'Full Chinese review: {characters} body characters, 3 figures, 2 tables, 10 cited sources; {len(doc)} PDF pages.')


if __name__=='__main__':
    verify()
