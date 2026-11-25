"""Check meaningful course requirements and cross-format numeric consistency."""
import hashlib
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
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}

def check_report(relative_path, expected_text):
    report=fitz.open(ROOT/relative_path)
    assert len(report)==2,'Report exceeds the two-page requirement.'
    report_text='\n'.join(p.get_text() for p in report)
    for value in [*expected_text,'Mind the Gap','22671064','100%','45.7%','1/60','34/60','2601.12349v3']:
        assert value in report_text, f'Report missing {value}'
    assert not re.search(r'First Author|author@example|ReLER|Group 6|TODO|TBD',report_text)
    for page in report:
        assert abs(page.rect.width-595.28)<1 and abs(page.rect.height-841.89)<1
    return {'report_pages_including_references':len(report)}

def related_part(package, owner, relation):
    directory, name = posixpath.split(owner)
    links = E.fromstring(package.read(posixpath.join(directory, '_rels', name + '.rels')))
    target = next(link.get('Target') for link in links if link.get('Id') == relation)
    return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(directory, target))


def check_presentation(language, deck_path, preview_path):
    notes_file = 'notes-en.json' if language == 'en' else 'notes.json'
    notes=json.loads((ROOT/'presentation'/notes_file).read_text(encoding='utf-8'))
    assert sum(s['seconds'] for s in notes['slides'])==340
    deck = ROOT/deck_path
    z=zipfile.ZipFile(deck)
    pres=E.fromstring(z.read('ppt/presentation.xml'))
    ids=pres.find('p:sldIdLst',NS)
    assert len(ids)==11
    rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    slide_parts=[posixpath.normpath(posixpath.join('ppt',rels[s.get('{'+NS['r']+'}id')])) for s in ids]
    xmls=[E.fromstring(z.read(n)) for n in slide_parts]
    assert [i for i,s in enumerate(xmls,1) if s.get('show')=='0']==[10,11]
    images_verified = []
    manifest = json.loads((ROOT/'sources/source-manifest.json').read_text(encoding='utf-8'))
    asset_hashes = {item['file']: item['sha256'] for item in manifest['presentation_paper_assets']}
    for page, (item, part, slide) in enumerate(zip(notes['slides'], slide_parts, xmls, strict=True), 1):
        if not (expected := item.get('images')):
            continue
        pictures = slide.findall('.//p:pic', NS)
        assert len(pictures) == len(expected), page
        for picture, figure in zip(pictures, expected, strict=True):
            prop = picture.find('./p:nvPicPr/p:cNvPr', NS)
            assert prop.get('name') == figure['file'] and prop.get('descr') == figure['alt'], page
            relation = picture.find('.//a:blip', NS).get('{' + NS['r'] + '}embed')
            part_name = related_part(z, part, relation)
            asset = 'assets/paper/' + figure['file']
            digest = hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()
            assert digest == asset_hashes[asset]
            assert hashlib.sha256(z.read(part_name)).hexdigest() == digest, asset
        images_verified.append(page)
    assert images_verified == [2, 4, 6, 7]
    for table_page in [6, 7]:
        assert xmls[table_page - 1].find('.//c:chart', NS) is None, table_page
    text='\n'.join(''.join(s.itertext()) for s in xmls)
    for value in ['22671064','100%','45.7%','1/60','34/60']:
        assert value in text,f'PPT missing {value}'
    assert notes['slides'][0]['title'] in text
    if language == 'en':
        for part in xmls[1:]:
            assert not re.search(r'[\u3400-\u9fff]', ' '.join(part.xpath('.//a:t/text()', namespaces=NS)))
    notes_parts=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
    assert len(notes_parts)==11
    notes_text='\n'.join(''.join(E.fromstring(z.read(n)).itertext()) for n in notes_parts)
    assert '2601.12349v3' in notes_text, 'Speaker notes missing the source manuscript.'
    for item in notes['slides']:
        assert item['speech'] in notes_text,'Speaker notes were not embedded intact.'
    preview=fitz.open(ROOT/preview_path)
    assert len(preview)==11
    native=json.loads((ROOT/'.build'/language/'native-check.json').read_text(encoding='utf-8'))
    assert native['opened'] and native['final_file_opened_read_only'] and not native['text_fit_findings']
    assert native['paper_image_slides'] == images_verified
    assert native['final_file_sha256'] == hashlib.sha256(deck.read_bytes()).hexdigest()
    return {
        'total_slides':len(ids),'main_slides':9,'hidden_backup_slides':[10,11],
        'planned_main_seconds':340,'buffer_seconds':20,
        'paper_image_slides':images_verified,
        'embedded_paper_assets_match_crops':True,
        'all_speaker_notes_embedded':True,'native_powerpoint_opened':True,
        'preview_pages':len(preview),'status':'passed'
    }

def main():
    results = {
        'en': {**check_report('submission/report.pdf', ['Jiahao Jiang','References','Proposed defense']),
               **check_presentation('en','submission/presentation.pptx','review/presentation-preview-en.pdf')},
        'zh': {**check_report('review/report-zh.pdf', ['蒋佳豪','参考文献','防护与验证建议']),
               **check_presentation('zh','review/presentation-zh.pptx','review/presentation-preview.pdf')},
    }
    (ROOT/'.build/course-check.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Course checks passed for both languages: 2 pages, 9+2 slides, and 340-second speaker notes.')

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
