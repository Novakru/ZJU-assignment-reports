import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL=process.env.PRESENTATIONS_SKILL_DIR;
const PYTHON=process.env.PRESENTATIONS_PYTHON;
if(!SKILL || !PYTHON)throw new Error('Set PRESENTATIONS_SKILL_DIR and PRESENTATIONS_PYTHON.');
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const source=path.join(ROOT,'assets/zjui-template.pptx');
const candidate=process.argv[2]||'.build/presentation-assembled.pptx';
const destination=process.argv[3]||'.build/finalized/presentation-checked.pptx';
const receiptId=createHash('sha256').update(path.resolve(ROOT,destination)).digest('hex').slice(0,16);
await fs.mkdir(path.dirname(path.resolve(ROOT,destination)),{recursive:true});
await fs.mkdir(path.join(ROOT,'.build/checks'),{recursive:true});
const result=await finalizePresentation({
 workspaceDir:ROOT,candidatePath:path.resolve(ROOT,candidate),finalPath:path.resolve(ROOT,destination),
 pythonExecutable:PYTHON,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','9144000,5143500','--validate-bullet-geometry','--validate-heading-fit'],
 requiredNativeChartOwnerSlides:[6,7],
 materializeLiteralChartWorkbooks:candidate.includes('assembled'),
 fontPolicy:{basis:'reference',families:['微软雅黑','黑体','Arial','Calibri'],referencePath:source,referenceSha256:createHash('sha256').update(await fs.readFile(source)).digest('hex'),scriptFonts:{ea:'微软雅黑'}},
 verifyArtifactToolImport:true,
 receiptPath:path.join(ROOT,'.build/checks',path.basename(destination)+'.'+receiptId+'.validation.json')
});
console.log(JSON.stringify(result));
