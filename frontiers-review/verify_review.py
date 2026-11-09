"""Validate the review's length, provenance, citations, identity and rendered PDF."""
from pathlib import Path
import hashlib
import json
import re
import fitz

ROOT=Path(__file__).resolve().parent

def expand_inputs(source):
    def replace(match):
        name=match.group(1)
        if name in ('metadata.tex','review-references.tex'):
            return match.group(0)
        path=ROOT/name
        assert path.is_file(),name
        return expand_inputs(path.read_text(encoding='utf-8'))
    return re.sub(r'\\input\{([^}]+)\}',replace,source)

def body_text(source):
    text=source.split('% BODY-BEGIN',1)[1].split('% BODY-END',1)[0]
    for env in ('figure','figure*','table','table*','tikzpicture','equation'):
        text=re.sub(r'\\begin\{'+re.escape(env)+r'\}.*?\\end\{'+re.escape(env)+r'\}','',text,flags=re.S)
    text=re.sub(r'\\(?:section|subsection|caption|label|cite|ref)\*?(?:\[[^]]*\])?\{[^}]*\}','',text)
    return re.sub(r'%[^\n]*','',text)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    tex=expand_inputs((ROOT/'review.tex').read_text(encoding='utf-8'))
    characters=len(re.findall(r'[\u4e00-\u9fff]',body_text(tex)))
    assert characters>=3000,characters
    assert r'\writingtask' not in tex and '作者待完成' not in tex
    figures=len(re.findall(r'\\begin\{figure\*?\}',tex))
    tables=len(re.findall(r'\\begin\{table\*?\}',tex))
    assert (figures,tables)==(4,3),(figures,tables)
    references=(ROOT/'review-references.tex').read_text(encoding='utf-8')
    keys=re.findall(r'\\bibitem\{([^}]+)\}',references)
    citations={key for group in re.findall(r'\\cite\{([^}]+)\}',tex+'\n'+references) for key in group.split(',')}
    assert len(keys)==16 and citations==set(keys),(keys,citations)
    manifest=json.loads((ROOT/'review-sources.json').read_text(encoding='utf-8'))
    assert len(manifest['papers'])==15
    assert len({p['id'] for p in manifest['papers']})==15
    for paper in manifest['papers']:
        identifier=paper.get('doi') or paper['id']
        assert identifier in references and paper['downloaded'],identifier
        cached=ROOT/'cache'/f'{paper["id"]}.pdf'
        if cached.exists():assert sha(cached)==paper['sha256'],paper['id']
    path=ROOT/'output/pdf/multi-agent-literature-review.pdf'
    doc=fitz.open(path);text='\n'.join(page.get_text() for page in doc)
    for fragment in ('多智能体系统综述','关键词','结论','参考文献','资料与工具说明','蒋佳豪','22671064'):
        assert fragment in text,fragment
    assert '待填写' not in text and '作者待完成' not in text
    assert doc.metadata['author']=='蒋佳豪',doc.metadata
    assert '\ufffd' not in text
    for paper in manifest['papers']:
        assert (paper.get('doi') or paper['id']) in re.sub(r'\s+','',text),paper['id']
    outside=[]
    for i,page in enumerate(doc):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:
                        outside.append([i+1,span['text']])
    assert not outside,outside
    for fig in ('react-task-dependence','audit-with-artifacts'):
        figure=fitz.open(ROOT/'figures'/f'{fig}.pdf')
        assert len(figure)==1 and len(figure[0].get_text())>80
    provenance=json.loads((ROOT/'figure-provenance.json').read_text(encoding='utf-8'))
    for name,digest in provenance['data_sha256'].items():assert sha(ROOT/'data'/name)==digest
    for name,digest in provenance['figure_sha256'].items():assert sha(ROOT/'figures'/name)==digest
    record=dict(title='面向科研任务的多智能体系统综述：知识、记忆与协作的机制及证据边界',
      author='蒋佳豪',student_id='22671064',identity_supplied_by_user=True,
      language='zh',status='substantially revised AI-assisted narrative review; author review pending',
      pages=len(doc),body_chinese_characters_excluding_headings_figures_tables_equations_and_references=characters,
      minimum_body_characters=3000,body_length_requirement_satisfied=True,
      figures=figures,tables=tables,primary_studies=15,tool_references=1,
      references=len(keys),all_references_cited=True,original_experiments_conducted=False,
      primary_fulltexts_retrieved=True,source_selection='purposeful narrative, not systematic or exhaustive',
      template='unmodified official AAS class with a separate ZJUI course adaptation package',
      known_template_warning='caption identifies ccaption-modified AAS captions as unknown; explicit caption settings visually audited',
      technical_packaging_complete=True,author_review_confirmed=False,submission_ready=False,
      pending=['author review and compliance with course rules on AI assistance'],
      source_sha256={p.name:sha(p) for p in list(ROOT.glob('review*.tex'))+
         list(ROOT.glob('figure-*.tex'))+list(ROOT.glob('table-*.tex'))+
         [ROOT/'aas.cls',ROOT/'picins.sty',ROOT/'journal-review.sty',ROOT/'metadata.tex',
          ROOT/'verify_review.py',ROOT/'figure-provenance.json',ROOT/'review-sources.json']},
      pdf_sha256=sha(path))
    (ROOT/'review-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Review: {characters} Chinese body characters, {figures} figures, {tables} tables, {len(keys)} references; {len(doc)} pages.')

if __name__=='__main__':verify()
