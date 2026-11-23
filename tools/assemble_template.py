"""Merge Artifact Tool content into the original ZJUI template package.

The installed Artifact Tool's template import/export creates a package that the
local PowerPoint rejects. Keeping the original master/layout parts byte-for-byte
avoids that problem and preserves the exact supplied branding. New editable
objects still come from Artifact Tool; this is an OPC package merge, not a raster
reconstruction or python-pptx authoring workflow.
"""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import posixpath
import zipfile
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'

def xml(data):
    return ET.fromstring(data)

def encode(tree):
    return ET.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)

def relname(part):
    directory, base = posixpath.split(part)
    return posixpath.join(directory, '_rels', base + '.rels')

def resolve(part, target):
    return (target.lstrip('/') if target.startswith('/') else
            posixpath.normpath(posixpath.join(posixpath.dirname(part), target)))

def assemble(language):
    build_dir = ROOT / '.build' / language
    with zipfile.ZipFile(ROOT/'assets/zjui-template.pptx') as z:
        original = {n:z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(build_dir/'content.pptx') as z:
        content = {n:z.read(n) for n in z.namelist()}
    output = dict(original)
    # Remove only original slide parts; all masters, layouts, themes and artwork
    # remain exactly as supplied. Unused template assets are harmless.
    for n in list(output):
        if n.startswith('ppt/slides/'):
            del output[n]
    types = xml(original['[Content_Types].xml'])
    for node in list(types):
        if node.get('PartName','').startswith('/ppt/slides/'):
            types.remove(node)
    types_by_name = {n.get('PartName'):n.get('ContentType')
                     for n in xml(content['[Content_Types].xml'])
                     if ET.QName(n).localname == 'Override'}
    for node in xml(content['[Content_Types].xml']):
        if ET.QName(node).localname == 'Default':
            if not any(n.get('Extension') == node.get('Extension') for n in types):
                types.append(deepcopy(node))

    def override(part, kind):
        if not any(n.get('PartName') == '/'+part for n in types):
            ET.SubElement(types, '{'+CT+'}Override', PartName='/'+part, ContentType=kind)

    mapping = {}
    def copy_part(source):
        if source in mapping:
            return mapping[source]
        if source not in content:
            raise KeyError(f'Missing content relationship target: {source}')
        directory, name = posixpath.split(source)
        dest = posixpath.join(directory, 'ace_'+name)
        mapping[source] = dest
        output[dest] = content[source]
        if '/'+source in types_by_name:
            override(dest, types_by_name['/'+source])
        relations = relname(source)
        if relations in content:
            rs = xml(content[relations])
            for rel in rs:
                if rel.get('TargetMode') != 'External':
                    new_target = copy_part(resolve(source, rel.get('Target')))
                    rel.set('Target', posixpath.relpath(new_target, posixpath.dirname(dest)))
            output[relname(dest)] = encode(rs)
        return dest

    pres = xml(original['ppt/presentation.xml'])
    rels = xml(original['ppt/_rels/presentation.xml.rels'])
    for rel in list(rels):
        if rel.get('Type','').endswith('/slide'):
            rels.remove(rel)
    slide_list = pres.find('p:sldIdLst', NS)
    for node in list(slide_list):
        slide_list.remove(node)
    notes_file = 'notes-en.json' if language == 'en' else 'notes.json'
    data = json.loads((ROOT/'presentation'/notes_file).read_text(encoding='utf-8'))
    template_indices = [1,3,3,3,3,3,3,3,10,3,3]
    for index, template_index in enumerate(template_indices, 1):
        source_part = f'ppt/slides/slide{index}.xml'
        base_part = f'ppt/slides/slide{template_index}.xml'
        dest_part = f'ppt/slides/slide{index}.xml'
        slide = xml(original[base_part])
        tree = slide.find('p:cSld/p:spTree', NS)
        # Empty template title boxes give way to authored full-width titles.
        if template_index == 3:
            for node in list(tree):
                if ET.QName(node).localname == 'sp':
                    tree.remove(node)
        if index == 1:
            for text in slide.findall('.//a:t', NS):
                if text.text == 'Title':
                    text.text = data['slides'][0]['title']
                    run = text.getparent()
                    prop = run.find('a:rPr', NS)
                    if prop is None:
                        prop = ET.Element('{'+NS['a']+'}rPr')
                        run.insert(0,prop)
                    prop.set('sz','2500'); prop.set('b','1')
        slide.set('show', '0' if data['slides'][index-1].get('hidden') else '1')
        for node in list(slide):
            if ET.QName(node).localname in {'transition','timing'}:
                slide.remove(node)
        rs = xml(original.get(relname(base_part),
                 ('<Relationships xmlns="'+REL+'"/>').encode()))
        for rel in list(rs):
            if any(rel.get('Type','').endswith('/'+t) for t in
                   ['notesSlide','comments','tags']):
                rs.remove(rel)
        relation_map = {}
        source_rel_part = relname(source_part)
        if source_rel_part in content:
            for rel in xml(content[source_rel_part]):
                if any(rel.get('Type','').endswith('/'+t) for t in
                       ['notesSlide','slideLayout','comments','tags']):
                    continue
                new_rel = deepcopy(rel)
                new_id = 'ace_'+rel.get('Id')
                relation_map[rel.get('Id')] = new_id
                new_rel.set('Id',new_id)
                if new_rel.get('TargetMode') != 'External':
                    target = copy_part(resolve(source_part,new_rel.get('Target')))
                    new_rel.set('Target',posixpath.relpath(target,'ppt/slides'))
                rs.append(new_rel)
        authored = xml(content[source_part]).find('p:cSld/p:spTree', NS)
        for shape in authored:
            if ET.QName(shape).localname in {'nvGrpSpPr','grpSpPr'}:
                continue
            shape = deepcopy(shape)
            for node in shape.iter():
                for attr in list(node.attrib):
                    if attr.startswith('{'+NS['r']+'}') and node.attrib[attr] in relation_map:
                        node.set(attr,relation_map[node.attrib[attr]])
            tree.append(shape)
        for shape_id, node in enumerate(slide.findall('.//p:cNvPr',NS),1):
            node.set('id',str(shape_id))
        output[dest_part] = encode(slide)
        output[relname(dest_part)] = encode(rs)
        override(dest_part,'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
        rid = f'ace_slide_{index}'
        ET.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=NS['r']+'/slide',Target=f'slides/slide{index}.xml')
        node = ET.SubElement(slide_list,'{'+NS['p']+'}sldId',id=str(255+index))
        node.set('{'+NS['r']+'}id',rid)

    # Literal table cell formatting is explicit; include any referenced table
    # style definitions without replacing the original template's styles.
    if 'ppt/tableStyles.xml' in content:
        if 'ppt/tableStyles.xml' in output:
            old = xml(output['ppt/tableStyles.xml']); new = xml(content['ppt/tableStyles.xml'])
            known = {n.get('styleId') for n in old}
            for style in new:
                if style.get('styleId') not in known: old.append(deepcopy(style))
            output['ppt/tableStyles.xml'] = encode(old)
    output['ppt/presentation.xml'] = encode(pres)
    output['ppt/_rels/presentation.xml.rels'] = encode(rels)
    output['[Content_Types].xml'] = encode(types)
    dest = build_dir/'presentation-assembled.pptx'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name, blob in output.items():
            z.writestr(name,blob)
    print(f'Original template preserved; assembled {len(template_indices)} editable slides.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    assemble(parser.parse_args().language)
