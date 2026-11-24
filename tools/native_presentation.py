"""Add presenter notes and verify/export the deck with installed PowerPoint."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import win32com.client

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='.build/finalized/presentation-checked.pptx')
    parser.add_argument('--output', default='.build/presentation-native.pptx')
    parser.add_argument('--render-dir', default='review/previews')
    parser.add_argument('--pdf', default='review/presentation-preview.pdf')
    parser.add_argument('--render-only',action='store_true')
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    args = parser.parse_args()
    english = args.language == 'en'
    notes_file = 'notes-en.json' if english else 'notes.json'
    notes = json.loads((ROOT/'presentation'/notes_file).read_text(encoding='utf-8'))
    report_path = ROOT/'.build'/args.language/'native-check.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    source = (ROOT/args.input).resolve()
    dest = (ROOT/args.output).resolve()
    images = (ROOT/args.render_dir).resolve()
    pdf = (ROOT/args.pdf).resolve()
    for directory in [dest.parent, images, pdf.parent]:
        directory.mkdir(parents=True,exist_ok=True)
    app = win32com.client.DispatchEx('PowerPoint.Application')
    pres = None
    findings = []
    try:
        # WithWindow=False avoids displaying an application window.
        pres = app.Presentations.Open(str(source),bool(args.render_only),False,False)
        if pres.Slides.Count != len(notes['slides']):
            raise RuntimeError('Unexpected slide count in native PowerPoint.')
        if args.render_only:
            pres.Export(str(images),'PNG',1600,900)
            print_range=pres.PrintOptions.Ranges.Add(1,pres.Slides.Count)
            pres.ExportAsFixedFormat(str(pdf),2,1,False,1,1,True,print_range,1)
            checked_charts = {}
            for slide_number, expected, maximum in [
                (6, [0.457, 1, 0.457, 1, 1], 1),
                (7, [1, 34], 60),
            ]:
                charts = [shape.Chart for shape in pres.Slides(slide_number).Shapes if shape.HasChart]
                assert len(charts) == 1, f'Expected one chart on slide {slide_number}.'
                chart = charts[0]
                values = list(chart.SeriesCollection(1).Values)
                assert values == expected, (slide_number, values)
                axis = chart.Axes(2)
                assert axis.MinimumScale == 0 and axis.MaximumScale == maximum
                checked_charts[slide_number] = {'values': values, 'axis': [0, maximum]}
            report=json.loads(report_path.read_text(encoding='utf-8'))
            report.update({'final_file_opened_read_only':True,
                           'final_file_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                           'native_charts':checked_charts})
            report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print('Final PPTX opened read-only; chart values, zero baseline and every slide exported.')
            return
        for i, item in enumerate(notes['slides'],1):
            slide = pres.Slides(i)
            if alt := item.get('illustration_alt'):
                pictures = [shape for shape in slide.Shapes if shape.Type == 13]
                assert len(pictures) == 1, f'Expected one illustration on slide {i}.'
                pictures[0].AlternativeText = alt
            slide.SlideShowTransition.Hidden = bool(item.get('hidden',False))
            slide.SlideShowTransition.AdvanceOnClick = True
            slide.SlideShowTransition.AdvanceOnTime = False
            slide.SlideShowTransition.AdvanceTime = item['seconds']
            timing = (f"Suggested time: {item['seconds']} seconds" if english
                      else f"建议时长：{item['seconds']}秒")
            source_label = 'Sources' if english else '来源（不朗读）'
            note = '\r\r'.join([timing, item['speech'], source_label + '\r' + '\r'.join(item['sources'])])
            body = None
            for shape in slide.NotesPage.Shapes:
                try:
                    if shape.Type == 14 and shape.PlaceholderFormat.Type == 2:
                        body = shape
                        break
                except Exception:
                    pass
            if body is None:
                raise RuntimeError(f'Missing notes body on slide {i}.')
            body.TextFrame.TextRange.Text = note
            # Native text bounds provide a useful fit check, separate from the
            # structural OOXML validator. The supplied cover/closing are retained.
            if i not in {1,9}:
                for shape in slide.Shapes:
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        measured = shape.TextFrame2.TextRange
                        if measured.BoundHeight > shape.Height + 3:
                            findings.append({'slide':i,'shape':shape.Name,
                                             'height':round(shape.Height,2),
                                             'text_height':round(measured.BoundHeight,2)})
        pres.BuiltInDocumentProperties('Title').Value = notes['slides'][0]['title']
        pres.BuiltInDocumentProperties('Author').Value = 'Jiahao Jiang' if english else 'Jiahao Jiang / 蒋佳豪'
        pres.BuiltInDocumentProperties('Subject').Value = 'Trustworthy Artificial Intelligence, ZJUI, 22671064'
        pres.SaveAs(str(dest),24)  # ppSaveAsOpenXMLPresentation
        report = {'application':'Microsoft PowerPoint','version':str(app.Version),
                  'opened':True,'slide_count':pres.Slides.Count,
                  'hidden_slides':[i for i,s in enumerate(notes['slides'],1) if s.get('hidden')],
                  'main_speech_seconds':sum(s['seconds'] for s in notes['slides']),
                  'text_fit_findings':findings,'preview_includes_hidden_slides':True}
        report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        if findings:
            raise RuntimeError(f'Native text-fit findings: {findings}')
        print(f'PowerPoint {app.Version}: saved notes for all {pres.Slides.Count} slides.')
    finally:
        if pres is not None:
            pres.Close()
        app.Quit()

if __name__ == '__main__':
    if hasattr(sys.stdout,'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
