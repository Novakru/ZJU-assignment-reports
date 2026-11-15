// Author editable slide content with @oai/artifact-tool.
// tools/assemble_template.py preserves the supplied PPTX package's original
// masters and backgrounds rather than round-tripping them through an importer.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const runtime=process.env.RUNTIME_NODE_MODULES || process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if (!runtime) throw new Error('Set RUNTIME_NODE_MODULES to the bundled runtime node_modules directory.');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const notes=JSON.parse(await fs.readFile(path.join(ROOT,'presentation/notes.json'),'utf8'));
const p=Presentation.create({slideSize:{width:960,height:540}});
const BLUE='#124F8D',ORANGE='#EE8910',INK='#1C2633',GRAY='#586470',FONT='微软雅黑';
function text(s,value,x,y,w,h,pt=18,color=INK,bold=false,align='left',font=FONT) {
  const sh=s.shapes.add({geometry:'textbox',name:value.replace(/\s+/g,' ').slice(0,44),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=value;
  sh.text.style={fontSize:pt*4/3,typeface:font,color,bold,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0,lineSpacing:1.12};
  return sh;
}
function title(s,value) {text(s,value,31,4,720,37,18,'#FFFFFF',true);}
function footer(s,value,num) {text(s,value,43,506,845,20,9,GRAY);text(s,String(num),908,505,20,20,10,GRAY,false,'right');}
function table(s,values,x,y,w,h,widths,pt=17) {
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});
 t.borders.assign({fill:'#D5DEE8',width:.8});
 for(let r=0;r<values.length;r++) for(let c=0;c<values[0].length;c++) {
   const cell=t.getCell(r,c);cell.fill=r===0?BLUE:'#FFFFFF';
   cell.text.style={typeface:FONT,fontSize:pt*4/3,color:r===0?'#FFFFFF':INK,bold:r===0,alignment:c===0?'left':'center',verticalAlignment:'middle',insets:10,wrap:'square',autoFit:'none'};
 }
 return t;
}
function slide(n) {
 const s=p.slides.add();s.hidden=!!notes.slides[n-1].hidden;
 const d=notes.slides[n-1];s.speakerNotes.text=`建议时长：${d.seconds}秒\n\n${d.speech}\n\n来源（不朗读）：\n${d.sources.join('\n')}`;
 return s;
}

// 1: Original cover title is edited in place by the template assembler.
let s=slide(1);
text(s,'A Security Architecture for\nLLM-Integrated App Systems',157,310,650,62,17,BLUE,false,'center');
text(s,'蒋佳豪  Jiahao Jiang  ·  22671064',157,392,650,30,15,BLUE,false,'center');
text(s,'Trustworthy Artificial Intelligence  ·  NDSS 2026',157,430,650,23,11,GRAY,false,'center');

// 2: Threat model, using text rather than decorative cards.
s=slide(2);title(s,notes.slides[1].title);
text(s,'用户想要：比较两款打车应用的车费',47,83,865,55,25,BLUE,true);
text(s,'可信输入',49,168,340,38,21,BLUE,true);
text(s,'用户请求\n受信任的运行环境说明',49,225,360,112,21);
text(s,'不可信应用',494,168,400,38,21,BLUE,true);
text(s,'描述与 schema\n实现与返回值',494,225,402,112,21);
text(s,'风险：第三方文本影响了有权决定下一步动作的模型',49,398,847,76,21,BLUE,true);
footer(s,'来源：ACE，§II-C、§III（pp. 3–6）',2);

// 3: Native table of attack classes.
s=slide(3);title(s,notes.slides[2].title);
table(s,[['攻击方式','入口','影响'],['规划操纵','应用描述','排除正常应用'],['执行中断','应用返回值','提前结束任务'],['执行管理器劫持','应用返回值','改写其他应用的结果']],44,101,871,270,[276,205,390],19);
text(s,'共同问题：不可信文本参与了规划或执行决策',49,415,865,49,22,BLUE,true);
footer(s,'来源：ACE，§III-B–E（pp. 5–6）；前序系统 IsolateGPT，NDSS 2025',3);

// 4: Original architecture figure, with native explanatory text below it.
s=slide(4);title(s,notes.slides[3].title);
const bytes=await fs.readFile(path.join(ROOT,'assets/ace-architecture.png'));
s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:'ACE Fig. 3: abstract planning, concrete matching, and rule-based isolated execution.',fit:'contain',position:{left:43,top:83,width:874,height:290}});
text(s,'抽象规划',49,389,260,33,19,BLUE,true);text(s,'仅使用可信信息',49,429,275,42,17);
text(s,'具体匹配',358,389,260,33,19,BLUE,true);text(s,'逐对匹配，检查信息流',358,429,285,42,17);
text(s,'受控执行',670,389,250,33,19,BLUE,true);text(s,'固定程序、隔离\n最小权限',670,429,250,64,17);
footer(s,'图源：ACE，Fig. 3（p. 7），仅裁去图外正文；机制：§IV-B–E',4);

// 5: Editable code excerpt and explanatory policy.
s=slide(5);title(s,notes.slides[4].title);
text(s,'data = load_bank_details()\nsend_email(content=data)',48,121,505,119,19,INK);
text(s,'financial 标签',587,111,319,40,22,BLUE,true);
text(s,'邮件应用只有 personal 许可',587,174,319,70,18);
text(s,'拒绝这个具体计划',587,264,319,43,23,ORANGE,true);
text(s,'标签沿中间变量传播，并跟踪分支条件引入的隐式依赖',49,352,852,78,23,BLUE,true);
text(s,'前提：标签、分析、运行时与隔离机制正确执行策略',49,455,866,33,15,GRAY);
footer(s,'来源：ACE，§IV-F、Fig. 5、App. A（pp. 9–11、14–16）',5);

// 6: Security denominator and useful completion remain explicit.
s=slide(6);title(s,notes.slides[5].title);
text(s,'100%',48,103,348,118,67,BLUE,true);
text(s,'InjecAgent 安全分',53,231,350,43,22,BLUE,true);
text(s,'1,054 个测试\n未调用指定攻击者工具',53,293,360,86,20);
table(s,[['模型配置','总体工具调用成功率'],['GPT-4o','83.6%'],['GPT-4o / o3-mini','85.3%']],441,111,473,214,[225,248],17);
text(s,'ASB 主文仍记载 3 次攻击者工具调用，\n作者将其判为与任务相关',441,364,473,75,17);
text(s,'模拟工具的调用成功，不等同于最终答案正确',49,465,857,34,17,BLUE,true);
footer(s,'来源：ACE，§V-B、Table II（pp. 11–12）；指标口径见备份页',6);

// 7: Native chart, fully editable percentages with zero baseline.
s=slide(7);title(s,notes.slides[6].title);
text(s,'GPT-4.1 最终正确率',49,80,470,34,18,BLUE,true);
const chart=s.charts.add('bar',{position:{left:39,top:124,width:487,height:281},categories:['单工具','多工具','关系数据'],series:[{name:'最终正确率',values:[.95,.80,.857],valuesFormatCode:'0.0%',fill:BLUE}],hasLegend:false,barOptions:{direction:'column',grouping:'clustered',gapWidth:90},chartFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaFill:'#FFFFFF',xAxis:{textStyle:{typeface:FONT,fontSize:17},majorGridlines:{fill:'none',width:0}},yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{typeface:FONT,fontSize:15},majorGridlines:{fill:'#DCE4ED',width:.6}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{typeface:FONT,fontSize:18,color:BLUE}}});
text(s,'多工具任务',583,93,319,39,21,BLUE,true);
text(s,'20.95 秒',583,154,319,58,34,BLUE,true);text(s,'平均每次查询耗时',584,218,312,32,17);
text(s,'US$0.27',583,284,319,58,34,BLUE,true);text(s,'原文实验记录的 API 费用',584,350,312,59,17);
text(s,'仍有任务失败；开销比较需要相同模型、工具与计费范围',49,448,856,57,19,BLUE,true);
footer(s,'来源：ACE，Tables III–IV（pp. 12–13）；费用是论文历史测量值',7);

// 8: Personal critique and an explicitly proposed experiment.
s=slide(8);title(s,notes.slides[7].title);
text(s,'可信基础',48,91,213,40,21,BLUE,true);text(s,'标签、环境说明与编排器需要正确',294,94,604,58,19);
text(s,'形式化保证',48,179,213,40,21,BLUE,true);text(s,'Python 子集与运行时的隐私健全性\n尚无形式化保证',294,176,604,78,19);
text(s,'覆盖范围',48,283,213,40,21,BLUE,true);text(s,'多轮交互仍是未来工作',294,285,604,42,19);
text(s,'拟议实验：固定模型，分别移除三项机制',48,368,851,40,21,BLUE,true);
text(s,'抽象规划、信息流检查、worker 隔离\n同时记录越权、真实泄露、任务正确率与延迟',48,421,865,76,18);
footer(s,'原文限制：ACE §IV-B；扩展版 App. C（pp. 16–17）。消融为个人建议，尚未开展。',8);

// 9: Keep the supplied closing slide intact.
s=slide(9);

// 10–11: Hidden backup slides, accessible in the presenter view.
s=slide(10);title(s,notes.slides[9].title);
text(s,'为什么固定计划仍然能有分支？',47,83,866,35,20,BLUE,true);
text(s,'固定允许的程序结构，执行时仍可沿已定义条件分支',47,128,866,46,18);
text(s,'为什么安全分不能代替任务正确率？',47,207,866,35,20,BLUE,true);
text(s,'InjecAgent 测的是工具调用，不检查最终答案\n匹配、条件执行与总体成功采用不同口径',47,252,866,76,18);
text(s,'ASB 应怎样解读？',47,365,866,35,20,BLUE,true);
text(s,'主文：3 次工具调用被判为任务相关\n扩展表 VII：按模型报告 99.95%、99.85% 的原始安全平均分',47,410,866,76,17);
footer(s,'来源：ACE §IV-C、§V-B；扩展版 Table VII、VIII。保留原始度量与作者判定。',10);

s=slide(11);title(s,notes.slides[10].title);
text(s,'Li et al.  ACE.  NDSS 2026',47,82,867,35,21,BLUE,true);
let link=text(s,'doi.org/10.14722/ndss.2026.230352',47,127,867,30,16);link.text.get(link.text.toString()).link={uri:'https://doi.org/10.14722/ndss.2026.230352',isExternal:true};
text(s,'扩展版（App. C、F）：arxiv.org/abs/2504.20984v3',47,167,867,35,16);
text(s,'Wu et al.  IsolateGPT.  NDSS 2025',47,236,867,35,21,BLUE,true);
text(s,'doi.org/10.14722/ndss.2025.241131',47,280,867,30,16);
text(s,'Zhan et al.  InjecAgent.  Findings of ACL 2024',47,349,867,35,21,BLUE,true);
text(s,'aclanthology.org/2024.findings-acl.624/',47,394,867,31,16);
text(s,'架构图：ACE Fig. 3。实验数据：ACE Tables II–IV。',47,461,867,30,14,GRAY);
footer(s,'架构图与结果采用 ACE 正式论文；形式化限制与 ASB 明细采用作者扩展版本',11);

await fs.mkdir(path.join(ROOT,'.build'),{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'.build/content.pptx'));
await fs.writeFile(path.join(ROOT,'.build/content-inspect.ndjson'),(await p.inspect({kind:'slide,textbox,chart,table',maxChars:30000})).ndjson);
console.log(`Authored ${p.slides.items.length} slides; native table slides 3, 6; native chart slide 7.`);
