// Body content is assembled into the original ZJUI PowerPoint masters.
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

const BLUE = '#124F8D';
const ORANGE = '#9F4E12';
const INK = '#1C2633';
const GRAY = '#526273';
const RULE = '#CBD8E3';
const PALE_BLUE = '#EAF2F9';
const PALE_ORANGE = '#FCEDDC';
const FONT = '微软雅黑';
const PDF = 'https://arxiv.org/pdf/2601.12349v3';

function box(slide, name, x, y, width, height, fill = 'none', geometry = 'rect') {
  return slide.shapes.add({
    name, geometry, position: {left: x, top: y, width, height},
    fill, line: {fill: 'none', width: 0}
  });
}

function text(slide, value, x, y, width, height, pt = 18, color = INK, bold = false, align = 'left') {
  const shape = box(slide, value.replace(/\s+/g, ' ').slice(0, 44), x, y, width, height, 'none', 'textbox');
  shape.text = value;
  shape.text.style = {
    fontSize: pt * 4 / 3, typeface: FONT, color, bold, alignment: align,
    verticalAlignment: 'top', wrap: 'square', autoFit: 'none', insets: 0, lineSpacing: 1.1
  };
  return shape;
}

function slide(n, reference = '', url = null) {
  const entry = notes.slides[n - 1];
  const page = p.slides.add();
  page.hidden = !!entry.hidden;
  page.speakerNotes.text = [entry.speech, ...entry.sources].join('\n\n');
  if (n !== 1 && n !== 9) {
    text(page, entry.title, 31, 4, 720, 37, 18, '#FFFFFF', true);
    box(page, 'Footer rule', 44, 493, 872, 1, RULE);
    const source = text(page, reference, 44, 503, 840, 22, 9, GRAY);
    if (url) source.text.get(reference).link = {uri: url, isExternal: true};
    text(page, String(n), 886, 502, 29, 22, 10, GRAY, false, 'right');
  }
  return page;
}

async function paperImage(slide, n, index, x, y, width, height) {
  const {file, alt} = notes.slides[n - 1].images[index];
  const blob = new Uint8Array(await fs.readFile(path.join(ROOT, 'assets', 'paper', file)));
  slide.images.add({blob, alt, contentType: 'image/png', fit: 'contain', position: {left: x, top: y, width, height}});
}

function lead(s, value) {
  text(s, value, 44, 65, 872, 68, 22, BLUE, true);
}

function takeaway(s, value) {
  box(s, 'Takeaway bar', 44, 428, 872, 54, PALE_BLUE);
  box(s, 'Takeaway rule', 44, 428, 4, 54, BLUE);
  text(s, value, 58, 442, 841, 37, 15, BLUE, true);
}

let s = slide(1);
text(s, t('针对安卓 GUI 智能体的动作重绑定攻击', 'Action Rebinding Attacks against\nAndroid GUI Agents'), 157, 308, 650, 70, 18, BLUE, false, 'center');
text(s, t('蒋佳豪  Jiahao Jiang  ·  22671064', 'Jiahao Jiang  ·  22671064'), 157, 393, 650, 30, 15, BLUE, false, 'center');
text(s, 'Qian et al.  ·  ACM CCS 2026', 157, 430, 650, 24, 11, GRAY, false, 'center');

s = slide(2, t('Qian 等，arXiv v3 PDF 第 1 页图 1', 'Qian et al., arXiv v3 PDF, Fig. 1, p. 1'), PDF + '#page=1');
lead(s, t('发送短信的点击，为什么接听了来电？', 'How did a tap to send a text answer a call?'));
await paperImage(s, 2, 0, 44, 122, 632, 294);
box(s, 'Figure annotation divider', 692, 122, 2, 285, RULE);
text(s, t('看蓝色标记', 'Blue labels'), 712, 132, 203, 32, 15, BLUE, true);
text(s, t('智能体看到的是短信界面，决定点击发送。', 'The agent sees the text screen and plans to tap Send.'), 712, 171, 202, 87, 15);
text(s, t('看红色标记', 'Red labels'), 712, 272, 203, 32, 15, ORANGE, true);
text(s, t('到点击送达时，前台已经是来电界面。', 'The call screen is in front when the tap arrives.'), 712, 311, 202, 87, 15);
takeaway(s, t('点的位置相同，接收点击的控件已经变了。', 'The tap lands at the same position on a different control.'));

s = slide(3, t('根据 Qian 等图 1 和第 4 节整理', 'Reading of Qian et al., Fig. 1 and Section 4'), PDF + '#page=4');
lead(s, t('智能体按旧界面作决定，系统按当前界面接收输入。', 'Planning uses the old screen. Input goes to the live one.'));
const observeX = 249;
const dispatchX = 819;
const switchX = 557;
box(s, 'Observation to dispatch interval', observeX, 156, dispatchX - observeX, 3, ORANGE);
box(s, 'Observation bracket', observeX, 149, 3, 18, ORANGE);
box(s, 'Dispatch bracket', dispatchX, 149, 3, 18, ORANGE);
text(s, t('观察到执行的时间差', 'Observation-to-action gap'), 340, 172, 389, 34, 16, ORANGE, true, 'center');
text(s, t('智能体', 'Agent'), 44, 232, 128, 34, 15, BLUE, true);
box(s, 'Agent time lane', 174, 244, 736, 2, RULE);
const stages = t(['观察（检查）','依据已见界面推理','分发（使用）'],
                 ['Observe (check)','Reason from old view','Dispatch (use)']);
[observeX, 523, dispatchX].forEach((x, i) => {
  box(s, stages[i] + ' marker', x - 7, 238, 15, 15, BLUE, 'ellipse');
  text(s, stages[i], x - 133, 263, 266, 45, 15, BLUE, true, 'center');
});
text(s, t('前台界面', 'Foreground'), 44, 329, 128, 34, 15, BLUE, true);
box(s, 'Messaging screen interval', 174, 314, switchX - 174, 61, PALE_BLUE);
box(s, 'Call screen interval', switchX, 314, 353, 61, PALE_ORANGE);
box(s, 'Foreground change marker', switchX, 310, 3, 68, ORANGE);
text(s, t('短信界面', 'Text message screen'), 196, 332, 339, 35, 16, BLUE, true, 'center');
text(s, t('来电界面', 'Incoming call'), 583, 332, 301, 35, 16, ORANGE, true, 'center');
text(s, t('视觉原子性要求动作所依据的界面一直有效到执行。', 'Visual atomicity requires the observed state to stay valid through dispatch.'), 44, 388, 872, 36, 14, GRAY);
takeaway(s, t('观察时检查的是短信界面，执行时用到的是来电界面。这就是 TOCTOU。',
              'The check sees the text screen. The use hits the call screen. This is TOCTOU.'));

s = slide(4, t('Qian 等，arXiv v3 PDF 第 4 页图 2，任务和结果节选', 'Qian et al., arXiv v3 PDF, Fig. 2, p. 4. Task and outcome excerpts.'), PDF + '#page=4');
lead(s, t('用户只委托了记笔记，图中的结果却是购买完成。', 'The user asks for a note. The figure ends with a purchase.'));
text(s, t('用户委托的任务', 'What the user asked for'), 44, 134, 591, 38, 17, BLUE, true);
await paperImage(s, 4, 0, 44, 174, 594, 79);
text(s, t('操作能力来自哪里？', 'Who can send the input?'), 47, 267, 587, 39, 17, BLUE, true);
box(s, 'Authority divider', 658, 133, 2, 267, RULE);
text(s, t('图中的结果', 'Outcome in Fig. 2'), 683, 122, 230, 28, 15, ORANGE, true, 'center');
await paperImage(s, 4, 1, 719, 157, 160, 254);
text(s, t('发送输入的是已经具备跨应用操作能力的智能体。作者用原型检验这种能力会不会越过用户授权。',
          'The agent already sends input across apps. The authors test where that authority can take an action.'),
     47, 314, 587, 83, 16, GRAY);
takeaway(s, t('输入换了接收者，实际动作可能超出用户授权的任务。',
              'A change of recipient can take the action outside the authorized task.'));

s = slide(5, t('Qian 等，arXiv v3 PDF §7.1–7.4，表 2–4', 'Qian et al., arXiv v3 PDF, Sections 7.1–7.4 and Tables 2–4'), PDF + '#page=8');
lead(s, t('作者在 6 个安卓智能体上测试了 15 个代表性任务。',
          'Six Android agents faced 15 representative tasks.'));
box(s, 'End-to-end finding background', 44, 147, 310, 253, PALE_BLUE);
text(s, '≥10/15', 65, 159, 276, 84, 46, BLUE, true);
text(s, t('各智能体达成的攻击目标', 'Attack goals reached by every tested agent'), 66, 250, 260, 75, 17, BLUE, true);
text(s, t('其中两个达到 15/15。', 'Two agents reached all 15.'), 66, 342, 264, 55, 15, INK);
const comparisons = t(
  [[ '端到端结果', '指定结果是否发生？原文表 2 逐任务记录。' ],
   [ '分环节测可靠性', '先看单步错投，再单独测多步中的接受与恢复。' ],
   [ '确认框对照', '保持确认任务，比较两种先前上下文。' ]],
  [[ 'End-to-end outcomes', 'Did the specified outcome occur? See Table 2.' ],
   [ 'Reliability by stage', 'Measure single taps, acceptance, and recovery.' ],
   [ 'Confirmation test', 'Compare two contexts for one confirmation.' ]]
);
for (const [i, [heading, detail]] of comparisons.entries()) {
  const y = 142 + i * 91;
  box(s, heading + ' separator', 383, y, 533, 1, RULE);
  text(s, heading, 383, y + 9, 532, 34, 17, BLUE, true);
  text(s, detail, 383, y + 46, 532, 46, 15);
}
takeaway(s, t('攻击是否达成目标、智能体是否恢复、确认框是否通过，是三种观察结果。',
              'Task outcomes, recovery rates, and confirmations measure different things.'));

s = slide(6, t('原表：Qian 等，arXiv v3 PDF 第 8 页表 3；单步数据见 §7.3.1',
               'Original table: Qian et al., arXiv v3 PDF, Table 3, p. 8. Single action: Section 7.3.1.'), PDF + '#page=8');
lead(s, t('多步流程需要保留界面进度，也依赖智能体恢复。', 'Multi-step workflows depend on state and recovery.'));
text(s, t('多步测试', 'Multi-step test'), 44, 128, 545, 33, 16, BLUE, true);
await paperImage(s, 6, 0, 44, 168, 600, 171);
box(s, 'Recovery column underline', 493, 341, 148, 4, ORANGE);
text(s, t('中列是接受页面预期动作，右列是返回原任务应用。',
          'Middle: followed the UI cue. Right: returned to the task app.'),
     44, 362, 590, 45, 14, GRAY);
box(s, 'Separate single-action check', 665, 127, 2, 271, RULE);
text(s, t('单次动作', 'Single-action test'), 685, 131, 226, 38, 16, BLUE, true);
text(s, '100%', 684, 170, 228, 83, 46, BLUE, true);
text(s, t('6 个受测智能体\n作者报告的成功率', 'Reported rate across six agents in the test setup'), 685, 265, 222, 100, 16);
takeaway(s, t('多步实验选用保留界面状态的应用，回到任务应用的比例仍有两个是 45.7%。',
              'Even with state-preserving apps, two agents recovered only 45.7% of the time.'));

s = slide(7, t('原表：Qian 等，arXiv v3 PDF 第 9 页表 4；右侧为六行汇总',
                'Original table: Qian et al., arXiv v3 PDF, Table 4, p. 9. Totals at right sum all six rows.'), PDF + '#page=9');
lead(s, t('确认任务相同，模型先前看到的上下文不同。', 'Same confirmation task, different preceding context.'));
await paperImage(s, 7, 0, 44, 136, 600, 232);
text(s, t('每个智能体在每种条件下做 10 次。', 'Ten trials per agent in each condition.'), 44, 383, 601, 36, 14, GRAY);
box(s, 'Pooled counts divider', 666, 129, 2, 274, RULE);
text(s, t('普通上下文', 'Generic context'), 685, 132, 225, 35, 16, BLUE, true);
text(s, '1/60', 685, 170, 224, 64, 33, BLUE, true);
text(s, t('意图对齐（IAS）', 'Intent alignment (IAS)'), 685, 258, 229, 37, 15, ORANGE, true);
text(s, '34/60', 685, 297, 228, 66, 33, ORANGE, true);
takeaway(s, t('确认由模型判断时，前序上下文会影响它是否接受。',
              'What the agent saw earlier affected whether it accepted the confirmation.'));

s = slide(8, t('阅读报告的防护建议，机制依据为论文第 4 节',
                'Defense proposed in the reading report. See Qian et al., Section 4 for the mechanism.'), PDF + '#page=4');
lead(s, t('如果来电已经接管前台，这次发送就应该停下。',
          'If a call takes over, discard the old Send tap.'));
box(s, 'Observed target', 44, 140, 274, 144, PALE_BLUE);
text(s, t('观察时绑定目标', 'Bind at observation'), 59, 155, 244, 36, 16, BLUE, true, 'center');
text(s, t('应用、窗口与状态版本', 'App, window, and state version'), 61, 200, 238, 64, 15, INK, false, 'center');
box(s, 'Action handed to dispatcher', 330, 200, 36, 18, BLUE, 'rightArrow');
box(s, 'Final input check', 378, 140, 270, 144, PALE_BLUE);
text(s, t('分发时校验', 'Check at dispatch'), 390, 155, 245, 36, 16, BLUE, true, 'center');
text(s, t('当前界面还能接收这项操作吗？', 'Is this still the intended target?'), 393, 200, 241, 65, 15, INK, false, 'center');
box(s, 'Check result branch', 650, 207, 30, 2, BLUE);
box(s, 'Check result stem', 679, 173, 2, 79, BLUE);
box(s, 'Dispatch branch', 680, 168, 29, 12, BLUE, 'rightArrow');
box(s, 'Retry branch', 680, 246, 29, 12, ORANGE, 'rightArrow');
box(s, 'Match', 710, 139, 205, 67, PALE_BLUE);
text(s, t('一致才执行', 'Match: dispatch'), 723, 157, 179, 41, 15, BLUE, true);
box(s, 'Mismatch', 710, 215, 205, 68, PALE_ORANGE);
text(s, t('已变就丢弃并重看', 'Changed: drop and observe'), 723, 228, 179, 51, 14, ORANGE, true);
box(s, 'Approval rule', 44, 313, 871, 2, RULE);
text(s, t('不可逆操作', 'Irreversible actions'), 44, 331, 219, 37, 16, BLUE, true);
text(s, t('让用户确认具体动作及目标。', 'Require the user to approve the exact action and target.'), 265, 331, 648, 42, 16);
text(s, t('验证建议：在模拟界面中同时测错投、误取消、完成率与时延。',
          'Test in a mock GUI and measure wrong deliveries, false cancellations, completion, and delay.'), 44, 387, 872, 35, 13, GRAY);
takeaway(s, t('执行安全还取决于输入送达时，目标是否仍是用户授权的那个。',
              'Safe execution depends on where the input actually lands.'));

slide(9);

s = slide(10, t('Qian 等，arXiv v3 PDF §7.2–7.4，表 2–4', 'Qian et al., arXiv v3 PDF, Sections 7.2–7.4 and Tables 2–4'), PDF + '#page=8');
const metrics = t(
  [['端到端达成数','表 2 对 15 项代表性任务逐项记录是否达到指定结果。'],
   ['多步自动恢复','表 3 记录能否回到任务应用。应用保留状态是实验前提。'],
   ['确认通过次数','表 4 每行是一个智能体，每种条件 10 次，汇总后每列 60 次。']],
  [['End-to-end outcomes','Table 2 checks the outcome of each of 15 representative tasks.'],
   ['Multi-step auto recovery','Table 3 measures return to the task app. The tested apps retained UI state.'],
   ['Confirmations accepted','Table 4 gives 10 trials per agent and condition, or 60 in each pooled column.']]
);
for (const [i, [heading, detail]] of metrics.entries()) {
  const y = 85 + i * 125;
  text(s, heading, 44, y, 872, 42, 19, BLUE, true);
  text(s, detail, 44, y + 51, 872, 62, 17);
}

s = slide(11, t('本 PPT 的页码和图表号以 arXiv v3 PDF 为准', 'Slides use the page and table numbering in the arXiv v3 PDF.'));
text(s, 'Yi Qian et al. · ACM CCS 2026', 44, 84, 872, 43, 20, BLUE, true);
text(s, 'Mind the Gap: Action Rebinding Attacks against Android GUI Agents', 44, 140, 872, 56, 18);
const paper = t('arXiv v3 PDF 原文', 'arXiv v3 PDF');
text(s, paper, 44, 210, 850, 35, 16).text.get(paper).link = {uri: PDF, isExternal: true};
const listing = t('ACM CCS 2026 官方录用名单', 'ACM CCS 2026 accepted papers');
text(s, listing, 44, 252, 850, 35, 16).text.get(listing).link = {
  uri: 'https://www.sigsac.org/ccs/CCS2026/program/accepted-papers.html', isExternal: true
};
box(s, 'Reference divider', 44, 304, 872, 1, RULE);
text(s, t('图 1 为作者示意图，图 2 选取任务和结果两个片段。\n多步恢复和确认实验分别是 PDF 表 3、4，HTML 版对应表 1、2。',
          'Fig. 1 shows the call example. Fig. 2 excerpts show the task and outcome.\nPDF Tables 3 and 4 correspond to HTML Tables 1 and 2.'),
     44, 328, 872, 96, 16);

await fs.mkdir(buildDir, {recursive: true});
await (await PresentationFile.exportPptx(p)).save(path.join(buildDir, 'content.pptx'));
console.log('Authored ' + p.slides.items.length + ' slides.');
