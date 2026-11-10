"""Manuscript figures: indexed structures, source-table plots and CC BY panels."""
from pathlib import Path
import csv, json, hashlib
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse
from matplotlib.lines import Line2D
import fitz

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'
INK='#202020'; GRAY='#777777'; LIGHT='#c6c6c6'
mpl.rcParams.update({
 'font.family':['Times New Roman','SimSun'],'font.size':8.5,
 'mathtext.fontset':'stix','axes.unicode_minus':False,
 'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.65,'text.color':INK,'axes.labelcolor':INK,
 'xtick.color':INK,'ytick.color':INK,'savefig.facecolor':'white',
 'xtick.major.width':.6,'ytick.major.width':.6})

def text(ax,x,y,s,size=8.5,ha='center',va='center',**kwargs):
    return ax.text(x,y,s,fontsize=size,ha=ha,va=va,zorder=5,**kwargs)

def line(ax,p,q,color=GRAY,lw=.65,**kwargs):
    ax.plot([p[0],q[0]],[p[1],q[1]],color=color,lw=lw,**kwargs)

def save(fig,name):
    # Fixed canvas preserves the declared final font sizes across panels.
    fig.savefig(OUT/(name+'.pdf'))
    fig.savefig(OUT/(name+'.png'),dpi=400)
    plt.close(fig)

def timeline():
    fig,ax=plt.subplots(figsize=(6.77,2.65))
    fig.subplots_adjust(left=.15,right=.99,top=.94,bottom=.16)
    ax.set(xlim=(2019.6,2026.5),ylim=(-.65,2.7))
    # Equal temporal spacing, including a visible 2021 column with no selected work.
    for x in range(2020,2027):ax.axvline(x,color='#e2e2e2',lw=.5,zorder=0)
    for y in [-.5,.5,1.5,2.5]:ax.axhline(y,color=LIGHT,lw=.6)
    entries=[
     (2020,2,'RAG'),(2023,2,'Toolformer\nReflexion\nMemGPT\nGenerative Agents'),
     (2024,2,'RAPTOR\nGraphRAG'),(2022,1,'ReAct'),
     (2023,1,'AutoGen\nMetaGPT'),(2023,0,'Coscientist'),
     (2024,0,'ChemCrow\nResearchAgent\nSciAgents\nAI Scientist*'),
     (2025,0,'Agent Laboratory\nAI co-scientist\nVirtual Lab\nAI Scientist-v2*'),
     (2026,0,'AI Scientist*\n期刊报告')]
    for x,y,s in entries:text(ax,x,y,s,size=7.1,linespacing=1.35)
    ax.set_yticks([0,1,2],['科研应用','交互与协作','知识与记忆'],fontsize=8.5)
    ax.set_xticks(range(2020,2027));ax.tick_params(axis='both',length=0,pad=7)
    ax.spines[['left','bottom']].set_visible(False)
    save(fig,'review-timeline')

def node(ax,x,y,label,kind='source',selected=False):
    if kind=='source':
        ax.add_patch(Rectangle((x-.25,y-.18),.5,.36,facecolor='#dcdcdc' if selected else 'white',edgecolor=INK,lw=.65,zorder=3))
    else:
        ax.add_patch(Circle((x,y),.22,facecolor='#dcdcdc' if selected else 'white',edgecolor=INK,lw=.65,zorder=3))
    text(ax,x,y,label,size=9)

def knowledge():
    fig,axes=plt.subplots(1,3,figsize=(6.77,3.0))
    fig.subplots_adjust(left=.035,right=.99,top=.91,bottom=.06,wspace=.16)
    for a in axes:a.set(xlim=(-.3,4.1),ylim=(-.75,5.5));a.axis('off')
    # a: selected fragments share one flat index.
    a=axes[0];text(a,0,5.25,'(a)  片段检索',size=9,ha='left')
    for i,y in enumerate([1.1,1.8,2.5,3.2,3.9]):
        a.add_patch(Rectangle((.35,y-.22),1.2,.44,facecolor='#dfdfdf' if i in [1,3] else 'white',edgecolor=INK,lw=.65))
        text(a,.95,y,rf'$d_{i+1}$',size=10)
    text(a,3.1,2.5,r'$q$',size=12)
    for y in [1.8,3.2]:a.annotate('',xy=(1.65,y),xytext=(2.85,2.5),arrowprops={'arrowstyle':'->','lw':.75,'linestyle':'--','color':INK})
    text(a,1.95,.25,'查询选择源片段',size=8)
    # b: a tree of summaries and leaves; dashed query reaches multiple levels.
    a=axes[1];text(a,0,5.25,'(b)  RAPTOR',size=9,ha='left')
    leaves=[(.35,1.25),(1.25,1.25),(2.15,1.25),(3.05,1.25)]
    mids=[(.8,2.65),(2.6,2.65)]
    for i,p in enumerate(leaves):line(a,p,mids[i//2])
    for p in mids:line(a,p,(1.7,4.05))
    for i,p in enumerate(leaves):node(a,*p,rf'$d_{i+1}$',selected=i==2)
    for i,p in enumerate(mids):node(a,*p,rf'$s_{i+1}$','summary',selected=i==0)
    node(a,1.7,4.05,r'$s_3$','summary')
    text(a,3.55,3.65,r'$q$',size=12)
    for p in [(.8,2.65),(2.15,1.25)]:
        a.annotate('',xy=(p[0]+.25,p[1]+.1),xytext=(3.4,3.45),arrowprops={'arrowstyle':'->','lw':.7,'linestyle':'--','color':INK})
    text(a,1.8,.25,'摘要与源片段可跨层选择',size=8)
    # c: entity graph -> community reports -> query-focused answer (global mode).
    a=axes[2];text(a,0,5.25,'(c)  GraphRAG（全局）',size=9,ha='left')
    coords=[(.35,1.0),(1.15,.7),(.95,1.8),(2.2,1.25),(3.05,.9),(2.85,1.95)]
    for i,j in [(0,1),(1,2),(2,0),(2,3),(3,4),(4,5),(5,3)]:line(a,coords[i],coords[j])
    for i,p in enumerate(coords):node(a,*p,rf'$e_{i+1}$','entity')
    a.add_patch(Ellipse((.78,1.28),1.7,2,fill=False,edgecolor=GRAY,ls=':',lw=.75))
    a.add_patch(Ellipse((2.65,1.43),1.7,2,fill=False,edgecolor=GRAY,ls=':',lw=.75))
    for x in [.8,2.65]:
        a.annotate('',xy=(x,3.05),xytext=(x,2.48),arrowprops={'arrowstyle':'->','lw':.7})
        text(a,x,3.4,'社区摘要',size=7.7)
    text(a,1.75,4.45,'语料级查询 q',size=8)
    line(a,(1.75,4.12),(.8,3.72),ls='--');line(a,(1.75,4.12),(2.65,3.72),ls='--')
    text(a,1.8,.05,'实体关系按社区组织',size=8)
    text(axes[0],0,-.5,'阴影：选中的记录    实线：索引关系    虚线：查询选择',size=7.8,ha='left')
    save(fig,'review-knowledge-memory')

def sciencebench():
    rows=list(csv.DictReader((ROOT/'data/scienceagentbench.csv').open(encoding='utf-8')))
    fig,axes=plt.subplots(1,2,figsize=(6.77,2.95))
    fig.subplots_adjust(left=.12,right=.97,top=.81,bottom=.23,wspace=.42)
    markers={'Direct':'o','OpenHands':'s','Self-Debug':'^'}
    style={'GPT-4o':{'color':GRAY,'ls':':'},'Claude-3.5-Sonnet':{'color':INK,'ls':'-'}}
    a=axes[0]
    a.plot([0,100],[0,100],color=LIGHT,lw=.7,zorder=0)
    text(a,46,49,'VER = SR',size=7.3,rotation=43,color=GRAY)
    for model in style:
        subset=[r for r in rows if r['model']==model]
        st=style[model]
        for r in subset:
            x=float(r['success_rate']);y=float(r['valid_execution_rate'])
            a.scatter(x,y,s=29,marker=markers[r['framework']],facecolors='white' if model=='GPT-4o' else INK,edgecolors=st['color'],lw=.8,zorder=3)
            if model=='Claude-3.5-Sonnet' and r['framework']=='Self-Debug':
                a.annotate(f'{x:.1f}, {y:.1f}',(x,y),xytext=(5,0),textcoords='offset points',fontsize=7,ha='left')
    a.set(xlim=(0,100),ylim=(0,100),xticks=[0,25,50,75,100],yticks=[0,25,50,75,100])
    a.set_xlabel('任务成功率 SR / %');a.set_ylabel('有效执行率 VER / %')
    a.set_title('(a)',loc='left',fontsize=10,pad=8)
    a=axes[1]
    for model in style:
        subset=[r for r in rows if r['model']==model]
        xs=[float(r['api_cost_usd']) for r in subset];ys=[float(r['success_rate']) for r in subset]
        for x,y,r in zip(xs,ys,subset):
            a.scatter(x,y,s=29,marker=markers[r['framework']],facecolors='white' if model=='GPT-4o' else INK,edgecolors=style[model]['color'],lw=.8,zorder=3)
        # No connecting lines: framework choice is categorical.
    a.set_xscale('log');a.set(xlim=(.007,1.8),ylim=(0,40),yticks=[0,10,20,30,40])
    a.set_xticks([.01,.1,1],['0.01','0.1','1'])
    a.set_xlabel('API费用 / (美元/任务)');a.set_ylabel('任务成功率 SR / %')
    a.set_title('(b)',loc='left',fontsize=10,pad=8)
    handles=[Line2D([],[],marker=m,color='none',markeredgecolor=INK,markerfacecolor='white',label=k,markersize=4) for k,m in markers.items()]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,1.0),ncol=3,frameon=False,fontsize=8,handletextpad=.4,columnspacing=1.5)
    text(axes[0],.0,-.34,'空心：GPT-4o    实心：Claude 3.5 Sonnet',ha='left',size=8,transform=axes[0].transAxes)
    save(fig,'review-sciencebench')

def audit():
    rows=list(csv.DictReader((ROOT/'data/audit.csv').open(encoding='utf-8')))
    fig,ax=plt.subplots(figsize=(6.77,2.8))
    fig.subplots_adjust(left=.24,right=.96,top=.85,bottom=.22)
    y=np.arange(len(rows))
    paper=[int(float(r['paper_only'])*int(r['n_per_category'])/100) for r in rows]
    artifacts=[int(float(r['with_artifacts'])*int(r['n_per_category'])/100) for r in rows]
    ax.barh(y-.16,paper,height=.28,color='white',edgecolor=GRAY,lw=.75,label='仅论文')
    ax.barh(y+.16,artifacts,height=.28,color='#777777',edgecolor=INK,lw=.6,label='论文、日志与代码')
    for i,(x,z) in enumerate(zip(paper,artifacts)):
        text(ax,x+.28,i-.16,str(x),ha='left',size=8)
        text(ax,z+.28,i+.16,str(z),ha='left',size=8)
    ax.set_yticks(y,[r['category'] for r in rows],fontsize=8.5);ax.invert_yaxis()
    ax.set_xlim(0,20);ax.set_xticks([0,5,10,15,20]);ax.set_xlabel('识别正确的案例数 / 20')
    ax.tick_params(axis='y',length=0,pad=7)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),frameon=False,ncol=2,fontsize=8)
    save(fig,'review-audit')

def original_panels():
    source=ROOT/'cache/coscientist-2023.pdf'
    specs=[('coscientist-suzuki',5,(395,376,477,528)),
           ('coscientist-sonogashira',5,(478,376,561,528)),
           ('coscientist-architecture',1,(39,48,565,383))]
    if not source.exists():
        assert all((OUT/(name+'.pdf')).exists() for name,_,_ in specs)
        return
    doc=fitz.open(source)
    for name,n,clip in specs:
        out=fitz.open();page=out.new_page(width=clip[2]-clip[0],height=clip[3]-clip[1])
        page.show_pdf_page(page.rect,doc,n,clip=fitz.Rect(clip))
        out.save(OUT/(name+'.pdf'),garbage=4,deflate=True)

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for fn in [timeline,knowledge,sciencebench,audit,original_panels]:fn()
    names=['review-timeline','review-knowledge-memory','review-sciencebench','review-audit',
           'coscientist-suzuki','coscientist-sonogashira','coscientist-architecture']
    manifest={
      'scheme':'two mechanism/index figures, two source-table plots, and two licensed source-figure composites',
      'data_sources':{
        'review-sciencebench':{'url':'https://arxiv.org/abs/2410.05080v3','locator':'Table 3, PDF p.8',
         'selection':'all three frameworks, GPT-4o and Claude-3.5-Sonnet, no expert knowledge',
         'n_tasks':102,'attempts_per_task':3,
         'aggregation':'best of three independent runs per task; SR, VER, CBS, lower cost priority; average selected runs',
         'uncertainty':'Table 3 selected-run estimates; no invented intervals'},
        'review-audit':{'url':'https://arxiv.org/abs/2509.08713v2','locator':'Section 6.2 and Table 11, pp.16-18',
         'n':100,'per_category':20,'positive_negative_ratio':'1:1; some defects injected',
         'transformation':'correct_count = accuracy_percent * n_per_category / 100; exact integer conversion'}},
      'licensed_panels':{'url':'https://doi.org/10.1038/s41586-023-06792-0',
        'original':'Fig.1abc PDF p.2 and Fig.5i/5j PDF p.6',
        'license':'CC BY 4.0 https://creativecommons.org/licenses/by/4.0/',
        'processing':'page clips only; source labels, photographs, curves, axes unchanged'},
      'schematics':'index topology is explanatory; chronology has true equal year spacing; no measured performance encoding',
      'data_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.csv')},
      'figure_sha256':{name+'.pdf':hashlib.sha256((OUT/(name+'.pdf')).read_bytes()).hexdigest() for name in names}}
    (ROOT/'figure-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
