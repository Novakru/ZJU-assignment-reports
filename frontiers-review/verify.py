"""Verify preparation artifacts; never label prompts as completed coursework."""
from pathlib import Path
import hashlib
import json
import re
import fitz

ROOT=Path(__file__).resolve().parent


def verify():
    source=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    assert len(source['papers'])==8
    for paper in source['papers']:
        assert paper['downloaded'],paper
        cached=ROOT/'cache'/f'{paper["id"]}.pdf'
        if cached.exists():
            assert hashlib.sha256(cached.read_bytes()).hexdigest()==paper['sha256']
    records={}
    for name in ('literature-review-layout','reading-and-writing-guide'):
        path=ROOT/'output/pdf'/f'{name}.pdf'
        doc=fitz.open(path)
        text='\n'.join(p.get_text() for p in doc)
        assert '工程技术前沿' in text
        assert '蒋佳豪' in text and '22671064' in text
        assert '非提交稿' in text
        for paper in source['papers']:
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
        records[name]=dict(pages=len(doc),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           chinese_characters_including_prompts=len(re.findall(r'[\u4e00-\u9fff]',text)),
                           submission_ready=False)
    report=dict(artifacts=records,course='工程技术前沿',language='zh',sources_verified=8,
                original_body_requirement=3000,original_body_complete=False,
                pending=['supporting artifacts are writing guides, not the completed review'],
                course_prohibits_direct_ai_generated_submission=True,
                template_base='MP2@9a46ef1 cover principles and official ZJUI vector identity; rewritten for personal review',
                required_submit_deadline='2026-11-20 23:59 Asia/Shanghai',peer_review_deadline='2026-12-05',
                finalized_submission_created=False)
    (ROOT/'verification.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print('Verified eight sources, two Chinese PDFs, explicit draft labels, and page boundaries.')


if __name__=='__main__':
    verify()
