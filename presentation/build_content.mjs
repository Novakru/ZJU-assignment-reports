// Reuse the ZJUI masters through tools/assemble_template.py.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const runtime = process.env.RUNTIME_NODE_MODULES || process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if (!runtime) throw new Error('Set RUNTIME_NODE_MODULES to the bundled runtime node_modules directory.');
const {Presentation, PresentationFile} = await import(pathToFileURL(path.join(runtime, '@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const language = process.argv[2] ?? 'zh';
if (!['zh', 'en'].includes(language)) throw new Error('Expected language zh or en.');
const t = (zh, en) => language === 'en' ? en : zh;
const notes = JSON.parse(await fs.readFile(path.join(ROOT, t('presentation/notes.json', 'presentation/notes-en.json')), 'utf8'));
const buildDir = path.join(ROOT, '.build', language);
const p = Presentation.create({slideSize: {width: 960, height: 540}});
const BLUE = '#124F8D', ORANGE = '#B85C00', INK = '#1C2633', GRAY = '#586470', FONT = '微软雅黑';

function text(slide, value, x, y, width, height, pt = 18, color = INK, bold = false, align = 'left') {
  const shape = slide.shapes.add({
    geometry: 'textbox', name: value.replace(/\s+/g, ' ').slice(0, 44),
    position: {left: x, top: y, width, height}, fill: 'none', line: {fill: 'none', width: 0}
  });
  shape.text = value;
  shape.text.style = {
    fontSize: pt * 4 / 3, typeface: FONT, color, bold, alignment: align,
    verticalAlignment: 'top', wrap: 'square', autoFit: 'none', insets: 0, lineSpacing: 1.12
  };
  return shape;
}

function table(slide, values, widths, {top = 115, height = 246, pt = 16} = {}) {
  const grid = slide.tables.add({
    rows: values.length, columns: values[0].length,
    left: 46, top, width: 868, height, values, columnWidths: widths
  });
  grid.borders.assign({fill: '#D5DEE8', width: .8});
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[0].length; c++) {
      const cell = grid.getCell(r, c);
      cell.fill = r === 0 ? BLUE : '#FFFFFF';
      cell.text.style = {
        typeface: FONT, fontSize: pt * 4 / 3, color: r === 0 ? '#FFFFFF' : INK,
        bold: r === 0, alignment: 'left', verticalAlignment: 'middle',
        insets: 10, wrap: 'square', autoFit: 'none'
      };
    }
  }
}

function slide(n, reference = '') {
  const entry = notes.slides[n - 1];
  const page = p.slides.add();
  page.hidden = !!entry.hidden;
  page.speakerNotes.text = [entry.speech, ...entry.sources].join('\n\n');
  if (n !== 1 && n !== 9) {
    text(page, entry.title, 31, 4, 720, 37, 18, '#FFFFFF', true);
    text(page, reference, 46, 506, 842, 20, 9, GRAY);
    text(page, String(n), 908, 505, 20, 20, 10, GRAY, false, 'right');
  }
  return page;
}
function label(page, title, description, x, y, width) {
  text(page, title, x, y, width, 37, 19, BLUE, true);
  text(page, description, x, y + 45, width, 90, 17);
}
function link(page, label, url, x, y) {
  const shape = text(page, label, x, y, 850, 36, 15);
  shape.text.get(label).link = {uri: url, isExternal: true};
}

let s = slide(1);
text(s, t('针对安卓 GUI 智能体的动作重绑定攻击', 'Action Rebinding Attacks against\nAndroid GUI Agents'), 157, 308, 650, 69, 18, BLUE, false, 'center');
text(s, t('蒋佳豪  Jiahao Jiang  ·  22671064', 'Jiahao Jiang  ·  22671064'), 157, 393, 650, 30, 15, BLUE, false, 'center');
text(s, 'Qian et al.  ·  ACM CCS 2026', 157, 430, 650, 23, 11, GRAY, false, 'center');

s = slide(2, t('来源：Qian 等，图 1、第 4 节', 'Qian et al., Figure 1 and Section 4'));
text(s, t('智能体准备点击时，来电切换了前台界面', 'An incoming call changes the screen before a planned tap.'), 46, 104, 868, 110, 28, BLUE, true);
label(s, t('规划时的问题','At planning time'), t('之前的界面上，用户要点哪个控件？','Which control fits the task on the observed screen?'), 46, 249, 410);
label(s, t('执行时的问题','At dispatch time'), t('现在由哪个窗口接收这次输入？','Which window will receive the input now?'), 507, 249, 405);
text(s, t('视觉原子性：相关界面在输入送达前保持有效', 'Visual atomicity assumes the observed context stays valid until dispatch.'), 46, 428, 870, 66, 18, BLUE, true);

s = slide(3, t('来源：Qian 等，第 3–4 节', 'Qian et al., Sections 3–4'));
table(s, t(
  [['角色','权限或职责'],['用户','授权一项任务及其操作范围'],['GUI 智能体','观察界面并跨应用发送输入'],['已安装的对手应用','在论文假设中无需安卓危险权限']],
  [['Actor','Authority or role'],['User','Authorizes the task and its scope'],['GUI agent','Reads the screen and sends input across apps'],['Adversary-controlled app','Requires no dangerous Android permissions in this model']]
), [308,560], {height: 254});
text(s, t('输入送错目标时，智能体原有的权限可能被用在授权范围之外。', 'A stale input can act outside the scope of the user task.'), 46, 407, 865, 75, 18, BLUE, true);

s = slide(4, t('示意图据 Qian 等第 4、5.1 节整理', 'Conceptual diagram based on Qian et al., Sections 4 and 5.1'));
label(s, t('1  观察','1  Observe'), t('读取界面 A\n识别当前控件','Read screen A\nand identify a control'), 46, 118, 244);
label(s, t('2  推理','2  Reason'), t('根据界面 A 决定动作\n此时界面可能变化','Plan from screen A\nThe screen may change'), 356, 118, 257);
label(s, t('3  执行','3  Dispatch'), t('当前界面 B 接收输入\n动作目标发生错位','Screen B receives the input\nThe target can differ'), 660, 118, 262);
text(s, '→', 296, 175, 50, 50, 25, BLUE, true);
text(s, '→', 610, 175, 50, 50, 25, BLUE, true);
text(s, t('动作重绑定是一种检查与使用之间的竞态（TOCTOU）。','Action rebinding is a time-of-check to time-of-use race.'), 46, 348, 870, 65, 23, BLUE, true);
text(s, t('即使模型正确识别了界面 A，输入仍可能到达不同的控件。','Even perfect recognition of screen A leaves the dispatch target uncertain.'), 46, 433, 870, 60, 16, GRAY);

s = slide(5, t('来源：Qian 等，第 6、7.3–7.4 节', 'Qian et al., Sections 6 and 7.3–7.4'));
label(s, t('任务恢复','Task recovery'), t('异常以后，是否继续取决于界面状态和恢复策略。','Continuation depends on the interface state and how the agent recovers.'), 46, 123, 410);
label(s, t('模型确认','Agent confirmation'), t('先前看到的界面会影响模型对后续确认框的判断。','Earlier screen content can make a later confirmation look relevant.'), 507, 123, 410);
text(s, t('意图对齐策略（IAS）检验了界面上下文对模型判断的影响。', 'The paper tests an intent alignment strategy (IAS) at confirmation.'), 46, 310, 860, 80, 21, BLUE, true);
text(s, t('授权仍需核对具体动作及其目标。','An authorization check needs the specific action and its target.'), 46, 417, 860, 62, 16, GRAY);

s = slide(6, t('来源：Qian 等，第 7.3.1–7.3.2 节，表 1', 'Qian et al., Sections 7.3.1–7.3.2 and Table 1'));
table(s, t(
  [['指标','范围','观察结果'],['单步动作重绑定','6 个受测智能体','100%'],['多步自动恢复','表 1 的 5 个智能体','45.7%–100%']],
  [['Outcome','Scope','Observation'],['Single-action rebinding','6 tested agents','100%'],['Multi-step auto-recovery','5 agents in Table 1','45.7%–100%']]
), [335,295,238], {top: 113, height: 246, pt: 16});
text(s, t('恢复只是多步流程的一环，实验选用了会保留界面状态的应用。','Recovery is one stage of a chain. The study selected apps that retain UI state.'), 46, 409, 865, 72, 18, BLUE, true);

s = slide(7, t('来源：Qian 等，第 7.4 节表 2，各条件汇总六行数据', 'Qian et al., Section 7.4, Table 2. Counts sum the six rows per condition.'));
text(s, t('模型通过确认的次数','Confirmations accepted by agents'), 46, 80, 530, 37, 18, BLUE, true);
s.charts.add('bar', {
  position: {left: 46, top: 125, width: 508, height: 280},
  categories: t(['普通上下文','意图对齐上下文'], ['Generic context','Intent-aligned context']),
  series: [{name: t('通过次数','Accepted'), values:[1,34], valuesFormatCode:'0', fill: BLUE}],
  hasLegend:false, barOptions:{direction:'column', grouping:'clustered', gapWidth:110},
  chartFill:'#FFFFFF', chartLine:{fill:'none', width:0}, plotAreaFill:'#FFFFFF',
  xAxis:{textStyle:{typeface:FONT,fontSize:17}},
  yAxis:{min:0,max:60,majorUnit:15,numberFormatCode:'0',textStyle:{typeface:FONT,fontSize:15},
         majorGridlines:{fill:'#DCE4ED',width:.6}},
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0',textStyle:{typeface:FONT,fontSize:19,color:BLUE}}
});
label(s, t('每种条件 60 次','60 trials per condition'), t('6 个智能体各试验 10 次\n使用同一种确认任务','6 agents × 10 trials\nOne confirmation task'), 594, 148, 325);
text(s, '1/60   →   34/60', 593, 298, 330, 55, 25, ORANGE, true);
text(s, t('汇总结果描述的是这项确认实验，具体表现因智能体而异。','The pooled counts describe this test. Acceptance varied across agents.'), 46, 437, 869, 64, 17, BLUE, true);

s = slide(8, t('阅读报告提出的防护与评估建议', 'Defensive controls and evaluation proposed in the reading report'));
const controls = t(
  [['动作绑定','记录应用、窗口和状态版本'],['分发时核验','一旦状态失效，丢弃旧动作并重新观察'],['用户独立确认','将高风险操作的批准绑定到具体目标']],
  [['Bind the action','Record the app, window, and state version'],['Check at dispatch','Discard stale actions and observe again'],['Require approval','Bind user approval to the exact high-risk operation']]
);
controls.forEach(([heading, description], i) => {
  text(s, heading, 46, 105 + i * 83, 292, 49, 18, BLUE, true);
  text(s, description, 348, 106 + i * 83, 567, 66, 17);
});
text(s, t('验证指标：输入错投、任务完成、误取消与附加时延','Measure wrong-context input, task completion, false cancellations, and delay.'), 46, 423, 868, 74, 17, BLUE, true);

slide(9);

s = slide(10, t('来源：Qian 等，第 7.3–7.4 节，表 1–2', 'Qian et al., Sections 7.3–7.4 and Tables 1–2'));
for (const [i, [heading, description]] of t(
  [['100% 衡量什么？','受测设置下的单步重绑定。'],['45.7%–100% 衡量什么？','表 1 中五个智能体的自动恢复环节。'],['1/60 和 34/60 怎样得到？','分别对表 2 两种条件的六行结果求和。']],
  [['What does 100% measure?','Single-action rebinding in the tested setup.'],['What does 45.7%–100% measure?','The auto-recovery stage for five agents in Table 1.'],['How were 1/60 and 34/60 computed?','Sum the six agent rows in each condition of Table 2.']]
).entries()) {
  label(s, heading, description, 46, 90 + i * 128, 869);
}

s = slide(11, t('各节、图表与数据均按 arXiv v3 引用', 'Sections, tables, and numbers refer to arXiv v3.'));
text(s, 'Yi Qian et al.', 46, 93, 860, 40, 22, BLUE, true);
text(s, 'Mind the Gap: Action Rebinding Attacks against Android GUI Agents', 46, 145, 866, 76, 19);
link(s, t('原文与版本记录','Paper and version history'), 'https://arxiv.org/abs/2601.12349v3', 46, 236);
link(s, t('ACM CCS 2026 官方录用名单','ACM CCS 2026 accepted papers'), 'https://www.sigsac.org/ccs/CCS2026/program/accepted-papers.html', 46, 296);
text(s, t('研究问题：第 3–5 节\n实验：第 7 节表 1–2','Threat and mechanism: Sections 3–5\nEvaluation: Section 7, Tables 1–2'), 46, 371, 850, 100, 17);

await fs.mkdir(buildDir, {recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(buildDir, 'content.pptx'));
console.log(`Authored ${p.slides.items.length} editable slides.`);
