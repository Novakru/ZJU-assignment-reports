"""Evidence-bound vector figures for the scholarly review.

Schematics are analytical illustrations, not observed data. Published graph
panels retain their original vector content, scales, and licence attribution.
"""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch,Rectangle,Circle,Polygon,FancyBboxPatch
from matplotlib.lines import Line2D
import fitz

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'
BLUE='#245B8A';TEAL='#287D78';ORANGE='#BA6931';INK='#24323E';GRAY='#697681';PALE='#EDF2F6'
mpl.rcParams.update({'font.family':'Microsoft YaHei','font.size':9,'axes.unicode_minus':False,
 'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.65,'text.color':INK,'axes.labelcolor':INK,'xtick.color':GRAY,'ytick.color':GRAY,
 'savefig.facecolor':'white'})

def text(ax,x,y,s,size=9,color=INK,ha='center',va='center',weight='normal',**kw):
    return ax.text(x,y,s,fontsize=size,color=color,ha=ha,va=va,fontweight=weight,**kw)
def line(ax,x,y,**kw):ax.plot(x,y,**({'color':GRAY,'lw':.8}|kw))
def arrow(ax,a,b,color=GRAY,rad=0,lw=1,style='-|>'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=10,linewidth=lw,
      color=color,connectionstyle=f'arc3,rad={rad}',shrinkA=2,shrinkB=2))
def box(ax,x,y,w,h,label,edge=BLUE,face='white',size=9):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.01,rounding_size=0.06',
      edgecolor=edge,facecolor=face,lw=.8));text(ax,x,y,label,size=size)
def panel(ax,letter,title):
    text(ax,.0,1.04,letter,size=12,ha='left',weight='bold',transform=ax.transAxes)
    text(ax,.075,1.04,title,size=10,ha='left',weight='bold',transform=ax.transAxes)
def canvas(width=6.77,height=3.3):
    fig,ax=plt.subplots(figsize=(width,height));fig.subplots_adjust(left=.025,right=.98,top=.94,bottom=.07)
    ax.set(xlim=(-.65,17.2),ylim=(0,8));ax.axis('off');return fig,ax
def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'));fig.savefig(OUT/(name+'.png'),dpi=300);plt.close(fig)
def doc(ax,x,y,label,scale=1,color=BLUE):
    for dx,dy in [(.12,.12),(.06,.06),(0,0)]:
        ax.add_patch(Rectangle((x+dx,y+dy),.68*scale,.86*scale,facecolor='white',edgecolor=color,lw=.7))
    for yy in [.2,.38,.56]:line(ax,[x+.12*scale,x+.54*scale],[y+yy*scale,y+yy*scale],color=color,lw=.6)
    if label:text(ax,x+.34*scale,y-.24,label,size=8)

def timeline():
    fig,ax=canvas(height=3.45)
    years=[2020,2022,2023,2024,2025,2026];xs=[.9,3.55,6.2,8.85,11.5,14.2]
    line(ax,[.6,16.6],[3.95,3.95],color=BLUE,lw=1.4)
    for yr,x in zip(years,xs):
        ax.scatter(x,3.95,s=36,color=BLUE,zorder=3);text(ax,x,4.35,str(yr),size=10,weight='bold')
    items=[(.9,6.05,'RAG','外部知识进入生成过程',BLUE),
      (3.55,1.9,'ReAct','推理—行动—观察',BLUE),
      (6.2,6.2,'Toolformer\nReflexion','工具学习与反馈记忆',BLUE),
      (6.2,1.4,'AutoGen\nMetaGPT','角色分工与协作协议',TEAL),
      (8.85,6.2,'GraphRAG\nRAPTOR','图与层次检索',BLUE),
      (8.85,1.4,'ResearchAgent\nSciAgents','文献关联与假设生成',TEAL),
      (11.5,6.2,'Agent\nLaboratory','研究流程与人机协作',TEAL),
      (11.5,1.4,'AI co-scientist\nVirtual Lab','候选演化与实验验证',TEAL),
      (14.2,6.2,'The AI Scientist\n2026期刊稿','系统实验与同行评审',ORANGE)]
    for x,y,title,sub,c in items:
        line(ax,[x,x],[3.95,5.2 if y>4 else 2.6],color=c,lw=.7)
        text(ax,x,y,title,size=8.2,color=c,weight='bold');text(ax,x,y-.77,sub,size=7.3)
    # Explicitly schematic chronology: missing 2021 is not a quantitative gap.
    text(ax,16.7,3.85,'时间',size=8,ha='right',va='top')
    text(ax,.15,7.55,'能力积累：检索与工具',size=9,color=BLUE,ha='left',weight='bold')
    text(ax,6.7,7.55,'组织演进：协作与科研流程',size=9,color=TEAL,ha='left',weight='bold')
    save(fig,'review-timeline')

def framework():
    fig,ax=canvas(height=4.0)
    stages=[(1.65,'问题形成'),(6.0,'方案与实现'),(10.35,'观察与分析'),(14.7,'论证与交流')]
    for x,s in stages:
        text(ax,x,7.65,s,size=10,weight='bold');box(ax,x,6.65,3.35,.9,
          {'问题形成':'文献证据 → 研究假设','方案与实现':'任务分解 → 工具执行','观察与分析':'结果检查 → 计划修订','论证与交流':'证据综合 → 限定结论'}[s],size=8.6)
    for a,b in zip(stages,stages[1:]):arrow(ax,(a[0]+1.75,6.65),(b[0]-1.75,6.65),color=BLUE)
    for x in [1.65,6.,10.35,14.7]:arrow(ax,(x,5.15),(x,6.12),color=TEAL)
    ax.add_patch(Rectangle((.05,3.75),16.55,1.45,facecolor=PALE,edgecolor='none'))
    text(ax,.4,4.78,'协作与控制',ha='left',weight='bold',color=TEAL)
    text(ax,8.9,4.78,'角色分工  ·  通信拓扑  ·  搜索调度  ·  交接与终止',size=9.5)
    text(ax,.4,4.12,'共享研究状态',ha='left',weight='bold',color=TEAL)
    text(ax,9.0,4.12,'问题 / 候选  |  计划 / 配置  |  数据 / 日志  |  支持 / 反证',size=8.8)
    for x,label,sub in [(2.6,'知识获取','RAG · 层次检索 · 图结构'),(8.25,'长期记忆','经历 · 反思 · 分层存储'),(13.9,'外部环境','程序 · 专用模型 · 实验仪器')]:
        box(ax,x,2.2,4.6,1.55,label+'\n'+sub,edge=BLUE,face='white',size=9)
        arrow(ax,(x,3.0),(x,3.65),color=BLUE)
    ax.add_patch(Rectangle((.05,.18),16.55,.68,facecolor='#F5EEE7',edgecolor='none'))
    text(ax,8.3,.52,'贯穿全流程的评价：来源支持 ｜ 实验有效性 ｜ 可复现性 ｜ 资源与人工投入',size=9,color=ORANGE)
    arrow(ax,(14.7,6.1),(10.4,5.25),color=ORANGE,rad=-.25)
    save(fig,'review-framework')

def knowledge_memory():
    fig,axes=plt.subplots(1,3,figsize=(6.77,3.2));fig.subplots_adjust(left=.04,right=.99,top=.84,bottom=.12,wspace=.2)
    for ax in axes:ax.set(xlim=(0,5),ylim=(-.65,6));ax.axis('off')
    a=axes[0];panel(a,'a','片段与层次检索')
    for x in [.3,1.7,3.1]:doc(a,x,.4,'原文片段',scale=.8)
    for x in [.65,2.05,3.45]:arrow(a,(x,1.4),(2.3,2.25),color=BLUE)
    box(a,2.3,2.6,3.2,.7,'聚类与中间摘要',size=8.5);arrow(a,(2.3,3.0),(2.3,3.7))
    box(a,2.3,4.15,3.2,.7,'多层摘要检索',size=8.5)
    text(a,2.3,5.25,'RAG / RAPTOR',size=9,color=BLUE,weight='bold')
    text(a,2.3,-.48,'信息抽象层次',size=8.5,color=GRAY)
    a=axes[1];panel(a,'b','关系与社区检索')
    coords=[(.8,1.1),(1.8,.6),(2.,2.),(3.5,1.0),(3.8,2.5),(2.9,3.0)]
    for i,j in [(0,1),(0,2),(1,2),(2,3),(3,4),(4,5),(5,2)]:line(a,[coords[i][0],coords[j][0]],[coords[i][1],coords[j][1]],color='#A9B5BF')
    for i,(x,y) in enumerate(coords):a.scatter(x,y,s=75,facecolor=BLUE if i<3 else TEAL,edgecolor='white',zorder=3)
    arrow(a,(2.4,3.2),(2.4,3.7));box(a,2.4,4.15,3.6,.7,'社区摘要与全局综合',size=8)
    text(a,2.4,5.25,'GraphRAG',size=9,color=TEAL,weight='bold');text(a,2.4,-.48,'颜色区分社区；边表示关系',size=8,color=GRAY)
    a=axes[2];panel(a,'c','经历与反思记忆')
    labels=[('观察','原文 / 数据'),('解释','候选 / 反思'),('状态','待验 / 支持 / 否定')]
    for yy,(lab,sub) in zip([.8,2.25,3.7],labels):
        a.add_patch(Rectangle((.55,yy-.38),3.8,.86,facecolor=PALE,edgecolor='none'))
        text(a,.8,yy,lab,size=8.5,ha='left',weight='bold');text(a,3.0,yy,sub,size=7.8)
    arrow(a,(4.35,3.6),(4.35,.9),color=ORANGE,rad=-.4)
    text(a,2.5,5.25,'MemGPT / Reflexion',size=9,color=ORANGE,weight='bold')
    text(a,2.5,-.48,'研究状态及其修订',size=8.5,color=GRAY)
    save(fig,'review-knowledge-memory')

def topologies():
    fig,axes=plt.subplots(1,3,figsize=(6.77,2.9));fig.subplots_adjust(left=.04,right=.98,top=.82,bottom=.17,wspace=.15)
    for a in axes:a.set(xlim=(0,5),ylim=(0,5));a.axis('off')
    a=axes[0];panel(a,'a','流程型协作')
    for x,lab in zip([.6,2.35,4.1],['检索','实现','核验']):box(a,x,2.7,1.15,.9,lab,size=8.5)
    arrow(a,(1.2,2.7),(1.75,2.7),color=BLUE);arrow(a,(2.95,2.7),(3.5,2.7),color=BLUE)
    arrow(a,(4.1,2.15),(2.35,2.15),rad=-.6,color=ORANGE)
    text(a,2.35,.7,'交付物明确；错误可能逐级传递',size=8)
    a=axes[1];panel(a,'b','中心调度型协作')
    nodes=[(.65,.9),(4.2,.9),(.65,3.8),(4.2,3.8)]
    for pos,lab in zip(nodes,['检索','执行','生成','审查']):
        v=np.array((2.4,2.35))-np.array(pos);u=v/np.linalg.norm(v)
        arrow(a,np.array(pos)+u*.64,np.array((2.4,2.35))-u*.95,color=TEAL,style='<->');box(a,*pos,1.1,.8,lab,edge=TEAL,size=8.3)
    box(a,2.4,2.35,1.6,1.0,'协调代理',edge=TEAL,face=PALE,size=8.5)
    text(a,2.45,-.03,'资源统一分配；依赖中心判断',size=8)
    a=axes[2];panel(a,'c','讨论型协作')
    nodes=[(2.45,4.15),(.85,1.25),(4.05,1.25)]
    for i,j in [(0,1),(1,2),(2,0)]:
        p=np.array(nodes[i]);q=np.array(nodes[j]);u=(q-p)/np.linalg.norm(q-p)
        arrow(a,p+u*.6,q-u*.6,color=BLUE,style='<->')
    for i,pos in enumerate(nodes):
        a.add_patch(Circle(pos,.52,facecolor='white',edgecolor=BLUE,lw=.9));text(a,*pos,'代理'+str(i+1),size=8.2)
    text(a,2.45,2.25,'候选与批评',size=8.5,color=TEAL)
    text(a,2.45,-.03,'扩大视角；需防相关错误与冗余',size=8)
    save(fig,'review-topologies')

def sciencebench():
    with (ROOT/'data/scienceagentbench.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
    fig,axes=plt.subplots(1,2,figsize=(6.77,3.2),gridspec_kw={'width_ratios':[1.2,1]})
    fig.subplots_adjust(left=.21,right=.97,top=.74,bottom=.18,wspace=.36)
    a=axes[0]
    text(a,0,1.32,'a  执行与任务完成',size=10,ha='left',weight='bold',transform=a.transAxes)
    y=np.array([0,1,2,3.5,4.5,5.5]);sr=np.array([float(r['success_rate']) for r in rows]);ver=np.array([float(r['valid_execution_rate']) for r in rows])
    a.hlines(y,sr,ver,color='#B6C1CA',lw=1.5);a.scatter(ver,y,s=25,marker='o',facecolors='white',edgecolors=BLUE,label='有效执行率 VER',zorder=3)
    a.scatter(sr,y,s=25,marker='s',color=TEAL,label='任务成功率 SR',zorder=3)
    for yy,s,v in zip(y,sr,ver):
        text(a,s-2.2,yy,f'{s:.1f}',size=7,ha='right');text(a,v+2.2,yy,f'{v:.1f}',size=7,ha='left')
    a.set_yticks(y,['GPT-4o · Direct','GPT-4o · OpenHands','GPT-4o · Self-Debug','Sonnet · Direct','Sonnet · OpenHands','Sonnet · Self-Debug'],fontsize=7.4);a.invert_yaxis();a.set_xlim(0,105);a.set_xticks([0,25,50,75,100]);a.set_xlabel('比例（%）',fontsize=9);a.grid(axis='x',alpha=.18);a.tick_params(axis='y',length=0)
    a.legend(loc='lower left',bbox_to_anchor=(-.02,1.03),frameon=False,fontsize=7.5)
    a=axes[1]
    text(a,0,1.32,'b  成功率与调用成本',size=10,ha='left',weight='bold',transform=a.transAxes)
    colors={'Direct':GRAY,'OpenHands':ORANGE,'Self-Debug':TEAL}
    for r in rows:
        x=float(r['api_cost_usd']);yy=float(r['success_rate']);marker='o' if r['model']=='GPT-4o' else 's'
        a.scatter(x,yy,s=38,marker=marker,color=colors[r['framework']],edgecolor='white',lw=.4,zorder=3)
        if r['model']=='Claude-3.5-Sonnet':text(a,x,yy+2.1,{'Direct':'直接生成','OpenHands':'OpenHands','Self-Debug':'Self-Debug'}[r['framework']],size=7.2)
    a.set_xscale('log');a.set_xlim(.007,1.8);a.set_ylim(0,40);a.set_xticks([.01,.1,1],['0.01','0.1','1']);a.set_yticks([0,10,20,30,40]);a.set_xlabel('API费用（美元/任务，对数轴）',fontsize=8);a.set_ylabel('任务成功率（%）',fontsize=8);a.grid(alpha=.18)
    a.legend(handles=[Line2D([],[],marker='o',color='none',markerfacecolor=BLUE,label='GPT-4o'),Line2D([],[],marker='s',color='none',markerfacecolor=BLUE,label='Claude 3.5 Sonnet')],loc='lower left',bbox_to_anchor=(-.03,1.03),frameon=False,fontsize=7.5)
    save(fig,'review-sciencebench')

def audit():
    with (ROOT/'data/audit.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(6.77,2.7));fig.subplots_adjust(left=.23,right=.96,top=.83,bottom=.23)
    for i,r in enumerate(rows):
        a=float(r['paper_only']);b=float(r['with_artifacts']);ax.plot([a,b],[i,i],lw=2,color='#B5C1C9',zorder=1)
        ax.scatter(a,i,s=42,marker='o',facecolor='white',edgecolor=GRAY,zorder=3);ax.scatter(b,i,s=42,marker='s',color=BLUE,zorder=3)
        text(ax,a-2.3,i,f'{a:.0f}',size=8,ha='right');text(ax,b+2.3,i,f'{b:.0f}',size=8,ha='left')
    ax.set_yticks(range(5),[r['category'] for r in rows],fontsize=8.5);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xticks([0,20,40,60,80,100]);ax.set_xlabel('方法学缺陷识别准确率（%）');ax.grid(axis='x',alpha=.18);ax.tick_params(axis='y',length=0)
    ax.legend(handles=[Line2D([],[],marker='o',color='none',markeredgecolor=GRAY,markerfacecolor='white',label='仅论文'),Line2D([],[],marker='s',color='none',markerfacecolor=BLUE,label='论文 + 日志 + 代码')],loc='lower left',bbox_to_anchor=(0,1.02),frameon=False,ncol=2,fontsize=8.5)
    save(fig,'review-audit')

def evidence_cycle():
    fig,ax=canvas(height=3.0)
    names=[(1.7,4.5,'提出候选','文献关联与新假设'),(6.2,4.5,'区分解释','预期结果与反例'),(10.7,4.5,'获取观察','计算或实体实验'),(15.2,4.5,'修订结论','支持范围与不确定性')]
    for x,y,title,sub in names:
        ax.add_patch(Circle((x,y),.65,facecolor=PALE,edgecolor=TEAL,lw=1));text(ax,x,y,title,size=9,weight='bold')
        text(ax,x,y-1.3,sub,size=8.4)
    for a,b in zip(names,names[1:]):arrow(ax,(a[0]+.8,4.5),(b[0]-.8,4.5),color=TEAL)
    arrow(ax,(15.2,5.3),(1.7,5.3),color=BLUE,rad=.19)
    text(ax,8.4,6.95,'反证更新研究状态，影响下一轮检索与实验选择',size=9,color=BLUE)
    line(ax,[.9,16],[1.8,1.8],color='#CAD3DA')
    text(ax,2.7,.85,'探索：扩大候选空间',size=9,color=BLUE)
    text(ax,8.45,.85,'核验：提高区分能力',size=9,color=TEAL)
    text(ax,14.1,.85,'治理：限定资源与权限',size=9,color=ORANGE)
    save(fig,'review-evidence-cycle')

def original_spectra():
    """Extract unchanged vector panels from a CC BY 4.0 article PDF."""
    source=ROOT/'cache/coscientist-2023.pdf'
    if not source.exists():
        # Use previously extracted assets in a source-only checkout.
        assert (OUT/'coscientist-suzuki.pdf').exists() and (OUT/'coscientist-sonogashira.pdf').exists()
        return
    doc=fitz.open(source)
    for name,clip in [('coscientist-suzuki',(395,376,477,528)),('coscientist-sonogashira',(478,376,561,528))]:
        out=fitz.open();page=out.new_page(width=clip[2]-clip[0],height=clip[3]-clip[1]);page.show_pdf_page(page.rect,doc,5,clip=fitz.Rect(clip));out.save(OUT/(name+'.pdf'),garbage=4,deflate=True)

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for fn in [timeline,framework,knowledge_memory,topologies,sciencebench,audit,evidence_cycle,original_spectra]:fn()
    manifest={'scheme':'vector analytical schematics, two redrawn data figures, unchanged licensed source panels',
      'data_sources':{'review-sciencebench':{'url':'https://arxiv.org/abs/2410.05080v3','locator':'Table 3, PDF p.8',
       'selection':'all three framework conditions for GPT-4o and Claude-3.5-Sonnet, without expert knowledge',
       'n_tasks':102,'attempts_per_task':3,
       'aggregation':'best of three independent runs per task; prioritized SR, VER, CBS, lower cost; average selected runs',
       'uncertainty':'selected-run point estimates from Table 3; not three-run means or invented intervals'},
       'review-audit':{'url':'https://arxiv.org/abs/2509.08713v2','locator':'Section 6.2 and Table 11, pp.16-18',
       'n':100,'per_category':20,'positive_negative_ratio':'1:1; some defects injected by original authors'}},
      'licensed_panels':{'url':'https://doi.org/10.1038/s41586-023-06792-0','original':'Fig.5i and Fig.5j, PDF p.6',
       'license':'CC BY 4.0 https://creativecommons.org/licenses/by/4.0/',
       'processing':'PDF page clipping only, unchanged vector content; panel layout rearranged in the review'},
      'schematics':'Analytical illustrations; no positions, areas or arrow widths encode measured effect sizes',
      'data_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.csv')},
      'figure_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.pdf')}}
    (ROOT/'figure-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
