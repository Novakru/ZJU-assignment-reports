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
const BLUE = '#124F8D', ORANGE = '#B85C00', INK = '#1C2633', GRAY = '#586470';
const LIGHT_BLUE = '#EAF2F9', LIGHT_ORANGE = '#FFF0E0', RULE = '#CDD9E5', FONT = '微软雅黑';

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

function mark(page, name, x, y, width, height, fill, geometry = 'rect') {
  return page.shapes.add({
    name, geometry, position: {left: x, top: y, width, height},
    fill, line: {fill: 'none', width: 0}
  });
}

function arrow(page, x, y, width, height, color = BLUE, direction = 'rightArrow') {
  mark(page, 'Flow direction', x, y, width, height, color, direction);
}

function takeaway(page, value, y = 430) {
  mark(page, 'Takeaway rule', 46, y + 1, 4, 44, BLUE);
  text(page, value, 61, y, 851, 64, 17, BLUE, true);
}

const categoryAxis = {textStyle: {typeface: FONT, fontSize: 16, fill: GRAY}};
const gridAxis = {
  min: 0, textStyle: {typeface: FONT, fontSize: 15, fill: GRAY},
  majorGridlines: {fill: RULE, width: 0.6}
};
const chartStyle = {
  hasLegend: false, chartFill: '#FFFFFF', chartLine: {fill: 'none', width: 0},
  plotAreaFill: '#FFFFFF'
};

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

s = slide(2, t('来电情境示意，参见 Qian 等图 1、第 4 节', 'Illustration of a call interruption. Qian et al., Figure 1 and Section 4.'));
text(s, t('智能体决定点击后，来电换掉了前台界面。', 'A call takes over before the planned tap lands.'), 46, 76, 865, 48, 20, BLUE, true);
const phones = await fs.readFile(path.join(ROOT, 'assets', 'call-interruption.png'));
s.images.add({
  blob: new Uint8Array(phones), contentType: 'image/png',
  alt: notes.slides[1].illustration_alt,
  fit: 'contain', position: {left: 64, top: 119, width: 538, height: 275}
});
text(s, t('观察时：笔记界面','Observed: Notes'), 115, 396, 235, 42, 15, BLUE, true, 'center');
text(s, t('执行时：来电界面','At dispatch: Call'), 315, 396, 245, 42, 15, ORANGE, true, 'center');
mark(s, 'Illustration separator', 627, 152, 2, 257, RULE);
text(s, t('同一个点击位置，\n两个不同的控件。','Same tap position.\nDifferent controls.'), 656, 182, 258, 83, 19, ORANGE, true);
text(s, t('视觉原子性','Visual atomicity'), 656, 285, 258, 36, 16, BLUE, true);
text(s, t('智能体所见的界面，在动作送达时仍然有效。','The screen the agent saw still applies when the tap arrives.'), 656, 324, 258, 110, 16);

s = slide(3, t('来源：Qian 等，第 3–4 节', 'Qian et al., Sections 3–4'));
text(s, t('用户授权了一项任务，智能体可以跨应用操作。', 'The user delegates a task. The agent can send input across apps.'), 46, 81, 868, 65, 20, BLUE, true);
const actors = t(
  [['用户','指定任务范围'],['GUI 智能体','读取屏幕并发出输入'],['Android','向当前目标派发输入']],
  [['User','Defines the task'],['GUI agent','Reads the screen and sends input'],['Android','Routes input to the current target']]
);
actors.forEach(([heading, description], i) => {
  const x = 46 + i * 303;
  mark(s, heading + ' divider', x, 194, 222, 4, BLUE);
  text(s, heading, x, 210, 245, 40, 20, BLUE, true);
  text(s, description, x, 257, 246, 71, 17);
  if (i < actors.length - 1) arrow(s, x + 242, 216, 37, 18);
});
mark(s, 'Threat model emphasis', 46, 348, 868, 108, LIGHT_ORANGE);
text(s, t('论文的对手模型','Threat model'), 63, 365, 255, 34, 16, ORANGE, true);
text(s, t('对手控制一个已安装应用。论文假设它没有申请危险权限。','An adversary controls an installed app with no dangerous Android permissions.'), 63, 403, 832, 47, 16);

s = slide(4, t('概念时间线，据 Qian 等第 4、5.1 节整理', 'Conceptual timeline based on Qian et al., Sections 4 and 5.1'));
text(s, t('智能体按界面 A 规划，输入却由界面 B 接收。','The agent plans from screen A. Screen B receives the tap.'), 46, 78, 864, 50, 20, BLUE, true);
const start = 252, change = 560, end = 814;
mark(s, 'Observation-to-action gap', start, 152, end - start, 4, ORANGE);
mark(s, 'Observation tick', start, 144, 3, 20, ORANGE);
mark(s, 'Dispatch tick', end, 144, 3, 20, ORANGE);
text(s, t('观察到执行的时间差','Observation-to-action gap'), 308, 164, 452, 34, 16, ORANGE, true, 'center');
text(s, t('智能体','Agent'), 46, 234, 122, 33, 16, BLUE, true);
mark(s, 'Agent lane', 167, 250, 733, 2, RULE);
const steps = t(['观察 A','依据 A 推理','派发输入'],['Observe A','Reason from A','Dispatch']);
[start, 491, end].forEach((x, i) => {
  mark(s, steps[i] + ' marker', x - 7, 244, 15, 15, BLUE, 'ellipse');
  text(s, steps[i], x - 94, 269, 188, 32, 16, BLUE, true, 'center');
});
text(s, t('前台界面','Foreground'), 46, 329, 127, 31, 16, BLUE, true);
mark(s, 'Screen A interval', 169, 315, change - 169, 53, LIGHT_BLUE);
mark(s, 'Screen B interval', change, 315, 340, 53, LIGHT_ORANGE);
mark(s, 'Foreground switches here', change, 308, 3, 65, ORANGE);
text(s, t('界面 A','Screen A'), 290, 331, 148, 32, 16, BLUE, true, 'center');
text(s, t('界面 B','Screen B'), 657, 331, 145, 32, 16, ORANGE, true, 'center');
text(s, t('时间','Time'), 798, 391, 68, 28, 12, GRAY, false, 'right');
arrow(s, 875, 399, 25, 11, GRAY);
takeaway(s, t('动作重绑定源于检查与使用之间的竞态（TOCTOU）。','Action rebinding is a time-of-check to time-of-use (TOCTOU) race.'), 439);

s = slide(5, t('来源：Qian 等，第 6、7.3–7.4 节', 'Qian et al., Sections 6 and 7.3–7.4'));
const questions = t(
  [['任务恢复需要什么？','应用保留界面状态','智能体从中断中恢复'],
   ['模型会通过确认吗？','确认看起来符合任务','模型判断是否接受']],
  [['What lets the task resume?','The app retains its state','The agent resumes after interruption'],
   ['Will the agent accept?','The dialog appears relevant','The agent decides whether to accept']]
);
for (const [i, [question, state, result]] of questions.entries()) {
  const y = 109 + i * 150;
  const color = i === 0 ? BLUE : ORANGE;
  const pale = i === 0 ? LIGHT_BLUE : LIGHT_ORANGE;
  text(s, question, 46, y, 850, 40, 20, color, true);
  mark(s, question + ' first condition', 46, y + 52, 370, 57, pale);
  mark(s, question + ' decision', 494, y + 52, 420, 57, pale);
  text(s, state, 61, y + 67, 338, 37, 15, INK, true, 'center');
  if (i === 0) {
    text(s, '+', 431, y + 60, 47, 44, 22, BLUE, true, 'center');
  } else {
    arrow(s, 438, y + 72, 35, 16, color);
  }
  text(s, result, 506, y + 67, 395, 37, 15, INK, true, 'center');
}
takeaway(s, t('确认实验中的意图对齐策略（IAS），让弹窗在上下文中看起来更符合任务。',
              'Intent alignment strategy (IAS) makes the dialog look relevant.'), 429);

s = slide(6, t('来源：Qian 等，第 7.3.1–7.3.2 节，表 1', 'Qian et al., Sections 7.3.1–7.3.2 and Table 1'));
text(s, t('单步动作重绑定','Single-action rebinding'), 46, 109, 341, 45, 19, BLUE, true);
text(s, '100%', 46, 156, 338, 110, 64, BLUE, true);
text(s, t('6 个智能体\n论文报告的受测结果','6 agents\nRate in the tested setup'), 47, 283, 294, 89, 17);
mark(s, 'Separate experiments', 379, 105, 2, 276, RULE);
text(s, t('多步实验中的自动恢复率','Auto-recovery in the multi-step test'), 410, 87, 503, 65, 17, BLUE, true);
s.charts.add('bar', {
  ...chartStyle,
  position: {left: 405, top: 141, width: 507, height: 253},
  categories: ['AutoGLM', 'mobiagent', 'mobile-use', 'Droidrun', 'Mobile-Agent-v3'],
  series: [{name: t('自动恢复率','Auto-recovery'), values: [0.457, 1, 0.457, 1, 1], valuesFormatCode: '0.0%', fill: BLUE}],
  barOptions: {direction: 'bar', grouping: 'clustered', gapWidth: 70},
  xAxis: categoryAxis,
  yAxis: {...gridAxis, max: 1, majorUnit: 0.25, numberFormatCode: '0%'},
  dataLabels: {showValue: true, position: 'inEnd', numberFormatCode: '0.0%', textStyle: {typeface: FONT, fontSize: 15, color: '#FFFFFF', bold: true}}
});
takeaway(s, t('自动恢复只是多步流程的一环。实验选用的是会保留界面状态的应用。',
              'The recovery test used apps that retain their UI state.'), 429);

s = slide(7, t('来源：Qian 等，第 7.4 节表 2，各条件汇总六行数据', 'Qian et al., Section 7.4, Table 2. Counts sum the six rows per condition.'));
text(s, t('智能体接受确认的次数','Confirmations accepted by agents'), 46, 79, 587, 45, 19, BLUE, true);
s.charts.add('bar', {
  ...chartStyle,
  position: {left: 46, top: 124, width: 562, height: 298},
  categories: t(['普通上下文','意图对齐上下文'], ['Generic context','Intent-aligned context']),
  series: [{name: t('通过次数','Accepted'), values: [1, 34], valuesFormatCode: '0', fill: BLUE, points: [{idx: 1, fill: ORANGE}]}],
  barOptions: {direction: 'column', grouping: 'clustered', gapWidth: 110},
  xAxis: {...categoryAxis, textStyle: {...categoryAxis.textStyle, fontSize: 17}},
  yAxis: {...gridAxis, max: 60, majorUnit: 15, numberFormatCode: '0'},
  dataLabels: {showValue: true, position: 'outEnd', numberFormatCode: '0', textStyle: {typeface: FONT, fontSize: 19, color: BLUE}}
});
mark(s, 'Sample size separator', 630, 138, 2, 267, RULE);
text(s, t('每种条件 60 次','60 trials per condition'), 653, 148, 258, 65, 18, BLUE, true);
text(s, t('6 个智能体各做 10 次\n使用同一种确认任务','6 agents × 10 trials\nOne confirmation task'), 653, 218, 259, 70, 15);
text(s, '1/60', 653, 305, 105, 62, 24, BLUE, true);
text(s, '34/60', 773, 305, 137, 62, 24, ORANGE, true);
takeaway(s, t('同一种任务中，上下文影响了模型的确认判断。各智能体的结果有差别。',
              'Context affected acceptance. The size of the effect varied by agent.'), 441);

s = slide(8, t('阅读报告提出的防护与评估建议', 'Defensive controls and evaluation proposed in the reading report'));
text(s, t('把动作绑定到可信的应用、窗口和界面状态版本。',
          'Bind each action to its app, window, and UI state version.'), 46, 81, 865, 62, 20, BLUE, true);
mark(s, 'Dispatch check', 46, 198, 293, 94, LIGHT_BLUE);
text(s, t('分发时核对','Check at dispatch'), 63, 211, 257, 38, 18, BLUE, true, 'center');
text(s, t('当前状态仍与观察一致？','Does the state still match?'), 63, 254, 257, 33, 14, INK, false, 'center');
mark(s, 'Decision stem', 339, 244, 57, 3, BLUE);
mark(s, 'Decision branch', 395, 189, 3, 115, BLUE);
arrow(s, 397, 182, 47, 16);
arrow(s, 397, 297, 47, 16, ORANGE);
mark(s, 'Matching state', 445, 153, 469, 77, LIGHT_BLUE);
text(s, t('一致：发送到已绑定目标','Match: send to the bound target'), 464, 172, 431, 47, 17, BLUE, true);
mark(s, 'Stale state', 445, 269, 469, 77, LIGHT_ORANGE);
text(s, t('已变：丢弃旧动作，重新观察','Changed: drop the tap and observe again'), 464, 287, 433, 55, 17, ORANGE, true);
takeaway(s, t('不可逆操作还需用户独立确认，批准要绑定到具体动作及其目标。',
              'For irreversible actions, get user approval for the exact action and target.'), 386);
text(s, t('评估：输入错投、任务完成、误取消与时延','Measure misdirected input, task completion, false cancellations, and delay.'), 61, 463, 850, 32, 13, GRAY);

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
