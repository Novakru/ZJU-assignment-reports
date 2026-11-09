"""Redraw two published tables, without pooling studies or inventing uncertainty."""
from pathlib import Path
import csv
import hashlib
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
mpl.rcParams.update({'font.family':'Microsoft YaHei','font.size':9.5,
 'axes.unicode_minus':False,'pdf.fonttype':42,'ps.fonttype':42,
 'axes.spines.top':False,'axes.spines.right':False,
 'axes.labelcolor':'#24282C','text.color':'#24282C',
 'xtick.color':'#41474D','ytick.color':'#41474D',
 'axes.linewidth':.6,'savefig.facecolor':'white'})

def read(stem):
    with (ROOT/'data'/f'{stem}.csv').open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def save(fig,stem):
    for ext in ('pdf','png'):
        fig.savefig(ROOT/'figures'/f'{stem}.{ext}',dpi=300)
    plt.close(fig)

def react():
    rows=read('react')
    names=['直接回答','CoT','CoT-SC','Act','ReAct','CoT-SC → ReAct','ReAct → CoT-SC']
    fig,axes=plt.subplots(1,2,figsize=(6.77,2.85),layout='constrained')
    for ax,key,title,panel in zip(axes,['hotpotqa_em','fever_accuracy'],
        ['HotpotQA：严格匹配率（%）','FEVER：准确率（%）'],['a','b']):
        vals=np.array([float(r[key]) for r in rows]);y=np.arange(len(rows))
        ax.hlines(y,0,vals,color='#D6DCE2',linewidth=2)
        for i,v in enumerate(vals):
            ax.scatter(v,i,s=32,marker='D' if i>=5 else 'o',
                color='#003F88' if i==4 else ('#28786B' if i>=5 else '#717B85'),zorder=3)
            ax.text(v+1.3,i,f'{v:.1f}',va='center',fontsize=8.8)
        ax.set_yticks(y,names if panel=='a' else ['']*len(y));ax.invert_yaxis()
        ax.set_xlim(0,80);ax.set_xticks([0,20,40,60,80]);ax.grid(axis='x',alpha=.2)
        ax.set_title(title,fontsize=10.2,pad=9)
        ax.text(-.05,1.09,panel,transform=ax.transAxes,fontweight='bold',fontsize=12)
        ax.tick_params(axis='y',length=0)
    save(fig,'react-task-dependence')

def audit():
    rows=read('audit');fig,ax=plt.subplots(figsize=(6.77,2.65),layout='constrained')
    y=np.arange(len(rows));a=np.array([float(r['paper_only']) for r in rows]);b=np.array([float(r['with_artifacts']) for r in rows])
    ax.hlines(y,a,b,color='#A6ADB4',linewidth=1.5)
    ax.scatter(a,y,s=40,facecolors='white',edgecolors='#717B85',label='仅审查论文',zorder=3)
    ax.scatter(b,y,s=40,marker='s',color='#003F88',label='论文、轨迹日志与代码',zorder=3)
    for yy,aa,bb in zip(y,a,b):
        ax.text(aa-2,yy,f'{aa:.0f}',ha='right',va='center',fontsize=9)
        ax.text(bb+2,yy,f'{bb:.0f}',ha='left',va='center',fontsize=9)
    ax.set_yticks(y,[r['category'] for r in rows]);ax.invert_yaxis()
    ax.set_xlim(0,100);ax.set_xticks([0,20,40,60,80,100]);ax.set_xlabel('方法学问题识别准确率（%）')
    ax.grid(axis='x',alpha=.2);ax.tick_params(axis='y',length=0)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),frameon=False,ncol=2,fontsize=9)
    ax.margins(y=.17);save(fig,'audit-with-artifacts')

if __name__=='__main__':
    (ROOT/'figures').mkdir(exist_ok=True);react();audit()
    manifest={'type':'redrawn published tables; not new experiments',
      'react':{'source':'https://arxiv.org/abs/2210.03629v3','locator':'Table 1, PDF p.5',
       'model':'PaLM-540B','metrics':['HotpotQA exact match (%)','FEVER accuracy (%)'],
       'sampling_note':'CoT-SC uses 21 trajectories; tool access and inference cost differ across conditions',
       'transformation':'Seven prompting rows copied verbatim; supervised SoTA excluded because not a prompting condition'},
      'audit':{'source':'https://arxiv.org/abs/2509.08713v2','locator':'Section 6.2 and Table 11, PDF pp.16-18',
       'n':100,'design':'20 examples per category, 10 positive and 10 negative; some problems injected by authors',
       'auditor':'gemini-2.5-flash-preview-05-20','transformation':'Accuracy columns copied; no pooling or inferred confidence intervals'},
      'uncertainty':'Original point estimates only; no invented error bars; no causal or cross-system ranking',
      'matplotlib_version':mpl.__version__,
      'data_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.csv')},
      'figure_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'figures').glob('*.pdf')}}
    (ROOT/'figure-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
