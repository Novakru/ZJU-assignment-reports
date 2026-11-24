"""Refresh native numeric caches from the exact embedded worksheet cells.

PowerPoint may serialize numbers differently in the cache and embedded sheet.
Keep the two representations identical while preserving the chart data and style.
"""
from io import BytesIO
from pathlib import Path
import posixpath
import re
import sys
import zipfile
from lxml import etree as E

NS={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    's':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def resolve(part,target):
    return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part),target))

def refresh(source,dest):
    with zipfile.ZipFile(source) as z: parts={n:z.read(n) for n in z.namelist()}
    changes=0
    for name in list(parts):
        if not (name.endswith('.xml') and '/charts/' in name and '/_rels/' not in name):continue
        chart=E.fromstring(parts[name])
        external=chart.find('c:externalData',NS)
        if external is None:continue
        relpath=posixpath.join(posixpath.dirname(name),'_rels',posixpath.basename(name)+'.rels')
        rels={r.get('Id'):r.get('Target') for r in E.fromstring(parts[relpath])}
        wbpart=resolve(name,rels[external.get('{'+NS['r']+'}id')])
        wb=zipfile.ZipFile(BytesIO(parts[wbpart]))
        wr={r.get('Id'):r.get('Target') for r in E.fromstring(wb.read('xl/_rels/workbook.xml.rels'))}
        sheets={s.get('name'):resolve('xl/workbook.xml',wr[s.get('{'+NS['r']+'}id')])
                for s in E.fromstring(wb.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS)}
        for ref in chart.findall('.//c:numRef',NS):
            formula=ref.find('c:f',NS).text
            m=re.fullmatch(r"(?:'([^']+)'|([^!]+))!\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)",formula)
            if not m:raise ValueError(f'Unsupported chart range: {formula}')
            sheet=m[1] or m[2]
            if m[3]!=m[5]:raise ValueError('Expected a single numeric column.')
            tree=E.fromstring(wb.read(sheets[sheet]))
            cells={c.get('r'):c.find('s:v',NS).text for c in tree.findall('.//s:c',NS) if c.find('s:v',NS) is not None}
            for point in ref.findall('c:numCache/c:pt',NS):
                address=f'{m[3]}{int(m[4])+int(point.get("idx"))}'
                node=point.find('c:v',NS)
                exact=cells[address]
                if node.text!=exact:
                    assert abs(float(node.text)-float(exact))<1e-12,'Refuse a material data change.'
                    node.text=exact;changes+=1
        parts[name]=E.tostring(chart,xml_declaration=True,encoding='UTF-8',standalone=True)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    print(f'Refreshed {changes} numeric cache serializations from their embedded workbook.')

if __name__=='__main__':
    refresh(Path(sys.argv[1]),Path(sys.argv[2]))
