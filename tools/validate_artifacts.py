"""Check meaningful course requirements and cross-format numeric consistency."""
from io import BytesIO
import json
from pathlib import Path
import posixpath
import re
import sys
import zipfile
import fitz
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart',
    's':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def main():
    report=fitz.open(ROOT/'submission/report.pdf')
    assert len(report)==2,'Report exceeds the two-page requirement.'
    report_text='\n'.join(p.get_text() for p in report)
    for value in ['Jiahao Jiang','22671064','83.6%','85.3%','85.7%','20.95','0.27']:
        assert value in report_text, f'Report missing {value}'
    assert 'References' in report_text
    assert 'follow-up' in report_text
    assert not re.search(r'First Author|author@example|ReLER|Group 6|TODO|TBD',report_text)
    for page in report:
        assert abs(page.rect.width-595.28)<1 and abs(page.rect.height-841.89)<1
    notes=json.loads((ROOT/'presentation/notes.json').read_text(encoding='utf-8'))
    assert sum(s['seconds'] for s in notes['slides'])==340
    z=zipfile.ZipFile(ROOT/'submission/presentation.pptx')
    pres=E.fromstring(z.read('ppt/presentation.xml'))
    ids=pres.find('p:sldIdLst',NS)
    assert len(ids)==11
    rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    slide_parts=[posixpath.normpath(posixpath.join('ppt',rels[s.get('{'+NS['r']+'}id')])) for s in ids]
    xmls=[E.fromstring(z.read(n)) for n in slide_parts]
    assert [i for i,s in enumerate(xmls,1) if s.get('show')=='0']==[10,11]
    for i in [3,6]:assert xmls[i-1].find('.//a:tbl',NS) is not None
    assert xmls[6].find('.//c:chart',NS) is not None
    text='\n'.join(''.join(s.itertext()) for s in xmls)
    for value in ['22671064','83.6%','85.3%','100%','1,054','20.95','US$0.27']:
        assert value in text,f'PPT missing {value}'
    notes_parts=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
    assert len(notes_parts)==11
    notes_text='\n'.join(''.join(E.fromstring(z.read(n)).itertext()) for n in notes_parts)
    for item in notes['slides']:
        assert item['speech'] in notes_text,'Speaker notes were not embedded intact.'
    charts=[n for n in z.namelist() if n.endswith('.xml') and '/charts/' in n and '/_rels/' not in n]
    quantitative=[]
    for name in charts:
        chart=E.fromstring(z.read(name))
        if chart.find('.//c:barChart',NS) is not None:
            quantitative.append(chart)
    assert len(quantitative)==1
    c=quantitative[0]
    values=[float(v.text) for v in c.findall('.//c:ser/c:val/c:numRef/c:numCache/c:pt/c:v',NS)]
    assert values==[.95,.80,.857],values
    assert c.find('.//c:valAx/c:scaling/c:min',NS).get('val')=='0'
    assert c.find('.//c:valAx/c:scaling/c:max',NS).get('val')=='1'
    workbooks=[n for n in z.namelist() if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')]
    assert len(workbooks)==1
    wb=zipfile.ZipFile(BytesIO(z.read(workbooks[0])))
    numeric=[]
    for name in wb.namelist():
        if name.startswith('xl/worksheets/') and name.endswith('.xml'):
            tree=E.fromstring(wb.read(name))
            numeric.extend(float(cell.find('s:v',NS).text) for cell in tree.findall('.//s:c',NS)
                           if cell.get('t') not in {'s','str','inlineStr'} and cell.find('s:v',NS) is not None)
    assert numeric==[.95,.80,.857],numeric
    preview=fitz.open(ROOT/'review/presentation-preview.pdf')
    assert len(preview)==11
    native=json.loads((ROOT/'.build/native-check.json').read_text(encoding='utf-8'))
    assert native['opened'] and not native['text_fit_findings']
    (ROOT/'.build/course-check.json').write_text(json.dumps({
        'report_pages_including_references':len(report),'report_word_count':len(report_text.split()),
        'total_slides':len(ids),'main_slides':9,'hidden_backup_slides':[10,11],
        'planned_main_seconds':340,'buffer_seconds':20,
        'native_table_slides':[3,6],'native_chart_slides':[7],
        'chart_cache_and_embedded_workbook_agree':True,
        'all_speaker_notes_embedded':True,'native_powerpoint_opened':True,
        'preview_pages':len(preview),'status':'passed'
    },ensure_ascii=False,indent=2),encoding='utf-8')
    print('Course checks passed: 2-page English report; 9+2 slides; 340-second notes; native editable chart and tables.')

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
