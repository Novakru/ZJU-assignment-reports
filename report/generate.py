"""Generate LaTeX tables and vector boards from recorded experiment results."""
from pathlib import Path
import json
import statistics
import sys
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib import colors

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'experients' / 'assignment2'
GENERATED = ROOT / 'report' / 'generated'
LANGUAGE = 'zh'
FIGURES = ROOT / 'report' / 'figures'
sys.path.insert(0, str(ROOT / 'submission'))
from uttt import ultimateTicTacToe, globalTicTacToe, LINES


def write(name, text):
    (GENERATED / name).write_bytes((text + '\n').encode('utf-8'))


def tr(zh, en):
    return en if LANGUAGE == 'en' else zh


def tex_text(value):
    replacements={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$',
                  '#':r'\#','_':r'\_','{':r'\{','}':r'\}',
                  '~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(replacements.get(char,char) for char in value).replace('\n',r'\par ')


def tabular(name, columns, rows, alignment):
    lines = [r'\begin{tabular}{' + alignment + '}', r'\toprule',
             ' & '.join(map(str, columns)) + r' \\', r'\midrule']
    lines.extend(' & '.join(map(str, row)) + r' \\' for row in rows)
    lines.extend([r'\bottomrule', r'\end{tabular}'])
    write(name, '\n'.join(lines))


def draw_board(name, board, tiling=False, global_rule=False):
    size = 20
    nr, nc = len(board), len(board[0])
    c = canvas.Canvas(str(FIGURES / name), pagesize=(nc*size, nr*size), invariant=1)
    palette = ['#ffffff','#d8e4ed','#ecdbcf','#dce7d7','#eae3c8','#e1dcee',
               '#e9d8de','#d3e5e3','#e7ded0','#d9dff0','#e5e7cc','#eddbd7','#d5e3ec']
    statuses = None
    if global_rule:
        game = globalTicTacToe()
        game.board = board
        statuses = game.localStatus()
    for r, row in enumerate(board):
        for col, cell in enumerate(row):
            x, y = col*size, (nr-r-1)*size
            shade = palette[int(cell) % len(palette)] if tiling else '#ffffff'
            if statuses:
                shade = {'X':'#f4e5e3','O':'#e2ecf7','D':'#ececec','_':'#ffffff'}[statuses[(r//3)*3+col//3]]
            if tiling and not cell:
                shade = '#5c626b'
            c.setFillColor(colors.HexColor(shade))
            c.setStrokeColor(colors.HexColor('#c6ccd4'))
            c.setLineWidth(.35)
            c.rect(x, y, size, size, fill=1, stroke=1)
            if cell not in ('_', 0):
                ink = '#222222' if tiling else ('#a43c38' if cell == 'X' else '#003f88')
                c.setFillColor(colors.HexColor(ink))
                c.setFont('Times-Roman', 12)
                c.drawCentredString(x+size/2, y+size*.28, str(cell))
    c.setStrokeColor(colors.HexColor('#33465d'))
    c.setLineWidth(1)
    c.rect(0, 0, nc*size, nr*size, fill=0, stroke=1)
    if tiling:
        for r, row in enumerate(board):
            for col, cell in enumerate(row):
                x, y = col*size, (nr-r-1)*size
                if col+1 < nc and row[col+1] != cell:
                    c.line(x+size,y,x+size,y+size)
                if r+1 < nr and board[r+1][col] != cell:
                    c.line(x,y,x+size,y)
    else:
        c.setLineWidth(1.6)
        for i in (3, 6):
            c.line(i*size, 0, i*size, nr*size)
            c.line(0, i*size, nc*size, i*size)
        for br in (0,3,6):
            for bc in (0,3,6):
                for line in LINES:
                    coords = [(br+i//3, bc+i%3) for i in line]
                    values = [board[r][col] for r,col in coords]
                    if values[0] != '_' and len(set(values)) == 1:
                        c.setStrokeColor(colors.HexColor('#a43c38' if values[0]=='X' else '#003f88'))
                        c.setLineWidth(1.8)
                        (r0,c0),_,(r1,c1)=coords
                        c.line((c0+.5)*size,(8.5-r0)*size,(c1+.5)*size,(8.5-r1)*size)
        if statuses:
            for line in LINES:
                values = [statuses[i] for i in line]
                if values[0] in ('X','O') and len(set(values)) == 1:
                    c.setStrokeColor(colors.HexColor('#a43c38' if values[0]=='X' else '#003f88'))
                    c.setLineWidth(3.5)
                    a,b = line[0],line[-1]
                    c.line((3*(a%3)+1.5)*size,(7.5-3*(a//3))*size,
                           (3*(b%3)+1.5)*size,(7.5-3*(b//3))*size)
    c.showPage()
    c.save()


def figures(name, records, prefix, labels):
    lines = [r'\begin{figure}[htbp]', r'\centering']
    for i, (record, label) in enumerate(zip(records, labels)):
        filename = f'{prefix}-{i+1}.pdf'
        draw_board(filename, record['boards'][-1], global_rule=prefix=='extra')
        lines.extend([r'\begin{subfigure}[t]{.46\linewidth}', r'\centering',
                      r'\includegraphics[height=48mm]{figures/' + filename + '}',
                      r'\caption{' + label + '}', r'\end{subfigure}'])
        if i % 2 == 0 and i+1 < len(records):
            lines.append(r'\hfill')
        elif i+1 < len(records):
            lines.append(r'\par\medskip')
    captions = {'predefined':tr('预定义智能体的最终棋盘。','Final boards of the predefined agents.'),
                'designed':tr('自定义智能体对局的代表终盘。','Representative final boards of the designed agent.'),
                'human':tr('真人对战的代表终盘。','Representative final boards of the human games.'),
                'extra':tr('全局三连规则的代表终盘。','Representative final boards under the global-line rule.'),
                'simulated':tr('模拟对手实验的代表终盘（非真人）。','Representative synthetic-opponent boards (not human play).'),
                'depthpredefined':tr('更深搜索的预定义智能体代表终盘。','Predefined-agent final boards with deeper search.')}
    lines.extend([r'\caption{' + captions[prefix] + '}', r'\end{figure}'])
    write(name, '\n'.join(lines))


def ending(record):
    game = ultimateTicTacToe()
    game.board = [row[:] for row in record['boards'][-3]]
    idx = game._destination(record['moves'][-3])
    choices = game.legalMoves(idx)
    winner_x = record['winner'] == 1
    safe = 0
    for r,c in choices:
        game.board[r][c] = 'O' if winner_x else 'X'
        own_win = game.checkWinner() == -record['winner']
        allows = False
        if not own_win:
            for rr,cc in game.legalMoves(game._destination((r,c))):
                game.board[rr][cc] = 'X' if winner_x else 'O'
                allows |= game.checkWinner() == record['winner']
                game.board[rr][cc] = '_'
        safe += own_win or not allows
        game.board[r][c] = '_'
    return len(choices), safe


def human_layout(humans):
    """Render a complete data-entry layout; placeholders are never results."""
    rows=[]
    count=max(10,len(humans))
    for i in range(count):
        if i<len(humans):
            g=humans[i]
            rows.append([i+1,g['start_board'],'X' if g['max_first'] else 'O',len(g['moves']),
                         {1:tr('真人','Human'),-1:tr('智能体','Agent'),0:tr('平局','Draw')}[g['winner']],
                         f"{g['total_nodes']:,}",tr('已记录','Recorded')])
        else:
            rows.append([i+1,'---','---','---','---','---',tr('待录入','Pending')])
    tabular('human-table.tex',tr(['局次','起点','先手','步数','胜方','智能体节点','状态'],
                                ['Game','Start','First','Plies','Winner','Agent nodes','Status']),rows,'cccccrc')
    hwins=sum(g['winner']==1 for g in humans)
    owins=sum(g['winner']==-1 for g in humans)
    n=len(humans)
    stats=[
        [tr('已完成局数','Completed games'),f'{n} / 10'],
        [tr('真人胜 / 智能体胜 / 平局','Human wins / agent wins / draws'),f'{hwins} / {owins} / {n-hwins-owins}' if n else '---'],
        [tr('真人胜率','Human win rate'),f'{hwins/n:.1%}'.replace('%',r'\%') if n else '---'],
        [tr('智能体胜率','Agent win rate'),f'{owins/n:.1%}'.replace('%',r'\%') if n else '---'],
    ]
    tabular('human-summary.tex',tr(['统计项','结果'],['Measure','Result']),stats,'lr')
    if not humans:
        status=tr('本节为待录入版式。下表与预留棋盘尚无实测数据，破折号不表示平局或零胜率。',
                  'This section is a data-entry layout. The tables and reserved boards contain no measured games; '
                  'dashes do not mean draws or zero win rates.')
    else:
        status=tr(f'已录入{n}局真人对战。',f'{n} human games are recorded.')
        if n<10:
            status+=tr(f'距离最低要求还需{10-n}局。',f'Another {10-n} games are needed to meet the minimum.')
        if n>=10:
            status+=tr('当前样本中真人全部获胜。','The human won every game in the sample.') if hwins==n else tr(
                      '当前样本中真人并非全部获胜。','The human did not win every game in the sample.')
    write('human-results.tex',status)
    # Show both strengths and failures instead of silently omitting human wins.
    selected=[]
    for outcome in (-1,1,0):
        selected.extend(i for i,g in enumerate(humans) if g['winner']==outcome and i not in selected)
        if outcome==-1:
            selected=selected[:2]
        if len(selected)>=4:
            selected=selected[:4]
            break
    selected += [i for i in range(n) if i not in selected][:4-len(selected)]
    panels=[r'\begin{figure}[htbp]',r'\centering']
    for i in range(4):
        filename=f'human-{i+1}.pdf'
        actual=selected[i] if i<len(selected) else None
        board=humans[actual]['boards'][-1] if actual is not None else [['_']*9 for _ in range(9)]
        draw_board(filename,board)
        if i>=n:
            # A separate, unmistakably marked blank frame, not an empty played game.
            c=canvas.Canvas(str(FIGURES/filename),pagesize=(180,180),invariant=1)
            c.setStrokeColor(colors.HexColor('#c6ccd4'))
            for j in range(10):
                c.setLineWidth(1 if j%3==0 else .3)
                c.line(j*20,0,j*20,180)
                c.line(0,j*20,180,j*20)
            c.setFillColor(colors.white)
            c.rect(12,77,156,26,fill=1,stroke=0)
            c.setFillColor(colors.HexColor('#777777'))
            c.setFont('Times-Italic',10)
            c.drawCentredString(90,87,'Pending actual game data')
            c.showPage();c.save()
        caption=tr(f'第{actual+1}局：'+{1:'真人胜',-1:'智能体胜',0:'平局'}[humans[actual]['winner']]
                   if actual is not None else f'预留局面{i+1}（待录入）',
                   f'Game {actual+1}: '+{1:'human wins',-1:'agent wins',0:'draw'}[humans[actual]['winner']]
                   if actual is not None else f'Reserved position {i+1} (pending)')
        panels += [r'\begin{subfigure}[t]{.46\linewidth}',r'\centering',
                   r'\includegraphics[height=48mm]{figures/'+filename+'}',
                   r'\caption{'+caption+'}',r'\end{subfigure}']
        if i%2==0:
            panels.append(r'\hfill')
        elif i<3:
            panels.append(r'\par\medskip')
    figure_caption=tr('真人对战的代表终盘，兼顾双方胜局。','Representative human-game boards, including wins by both sides.') if n>=4 else tr(
        '真人实验的代表终盘位置；未录入的框图不属于实验结果。',
        'Slots for representative human final boards. Pending frames are not experimental results.')
    panels += [r'\caption{'+figure_caption+'}',
               r'\end{figure}']
    write('human-figures.tex','\n'.join(panels))
    notes_path=DATA/'human-notes.json'
    notes=json.loads(notes_path.read_text(encoding='utf-8')).get(LANGUAGE,{}) if notes_path.exists() else {}
    labels=[('outcomes',tr('胜负表现与是否所有真人局均获胜','Outcome distribution and whether humans always won')),
            ('representative_positions',tr('代表局面的关键落子、优势与失误','Critical moves, strengths, and mistakes')),
            ('weaknesses',tr('评估函数的不足及改进方向','Evaluation weaknesses and improvements'))]
    blocks=[]
    for key,label in labels:
        value=notes.get(key,'').strip()
        body=tex_text(value) if value else r'\textit{'+tr('待根据实际对局记录填写。','Pending actual game observations.')+'}'
        blocks.append(r'\noindent\textbf{'+label+r'}\par\noindent '+body+r'\par\medskip')
    write('human-observations.tex','\n\n'.join(blocks))


def extra_layout():
    path=DATA/'extra_results.json'
    if not path.exists():
        raise RuntimeError('Run experients/assignment2/run_extra.py first.')
    data=json.loads(path.read_text(encoding='utf-8'))
    games=data['games']
    assert len(games)>=10
    rows=[]
    for i,g in enumerate(games,1):
        status=g['local_status']
        rows.append([i,g['start_board'],'X' if g['max_first'] else 'O',len(g['moves']),
                     status.count('X'),status.count('O'),f"{g['total_nodes']:,}",
                     {1:'X',-1:'O',0:tr('平局','Draw')}[g['winner']]])
    tabular('extra-table.tex',tr(['局次','起点','先手','步数','X占盘','O占盘','节点数','胜方'],
                                ['Game','Start','First','Plies','X boards','O boards','Nodes','Win']),rows,'ccccrrrc')
    x=sum(g['winner']==1 for g in games)
    o=sum(g['winner']==-1 for g in games)
    d=len(games)-x-o
    text=tr(f'使用随机种子{data["seed"]}，共进行{len(games)}局，X胜{x}局（{x/len(games):.1%}），'
            f'O胜{o}局（{o/len(games):.1%}），平局{d}局（{d/len(games):.1%}）。'
            f'平均每局{statistics.mean(len(g["moves"]) for g in games):.1f}步，'
            f'访问{statistics.mean(g["total_nodes"] for g in games):,.1f}个节点。',
            f'With random seed {data["seed"]}, {len(games)} games gave {x} X wins ({x/len(games):.1%}), '
            f'{o} O wins ({o/len(games):.1%}), and {d} draws ({d/len(games):.1%}). '
            f'The mean game lasted {statistics.mean(len(g["moves"]) for g in games):.1f} plies '
            f'and visited {statistics.mean(g["total_nodes"] for g in games):,.1f} nodes.')
    write('extra-results.tex',text.replace('%',r'\%'))
    selected=[]
    keys=set()
    for outcome in (1,-1,0):
        candidate=next(((i,g) for i,g in enumerate(games,1) if g['winner']==outcome),None)
        if candidate:
            selected.append(candidate)
            keys.add((candidate[1]['start_board'],candidate[1]['max_first']))
    for i,g in enumerate(games,1):
        key=(g['start_board'],g['max_first'])
        if len(selected)<4 and key not in keys:
            selected.append((i,g));keys.add(key)
    figures('extra-figures.tex',[g for _,g in selected],'extra',
            [tr(f'第{i}局：'+{1:'X胜',-1:'O胜',0:'平局'}[g['winner']]+
                f'，占盘{g["local_status"].count("X")}:{g["local_status"].count("O")}',
                f'Game {i}: '+{1:'X wins',-1:'O wins',0:'draw'}[g['winner']]+
                f'; boards {g["local_status"].count("X")}:{g["local_status"].count("O")}')
             for i,g in selected])
    paragraphs=[]
    for j,(i,g) in enumerate(selected):
        status=g['local_status']
        if g['winner']:
            symbol='X' if g['winner']==1 else 'O'
            line=next(line for line in LINES if all(status[k]==symbol for k in line))
            indices=','.join(map(str,line))
            paragraphs.append(tr(f'图中第{i}局由{symbol}在局部棋盘{indices}组成全局三连。'
                f'双方占盘数为{status.count("X")}比{status.count("O")}；胜负由棋盘排列决定，而不由占盘总数单独决定。',
                f'In game {i}, {symbol} won through local boards {indices}. '
                f'The capture count was {status.count("X")}:{status.count("O")}; '
                'the arrangement of captured boards, not their total alone, determines victory.'))
        else:
            paragraphs.append(tr(f'第{i}局以平局结束：全部局部棋盘已封闭，但没有任何一方形成全局三连。'
                f'其中{status.count("D")}个局部棋盘为平局。',
                f'Game {i} ended in a draw: every local board was closed, but neither side formed a global line. '
                f'{status.count("D")} local boards were drawn.'))
    write('extra-analysis.tex','\n\n'.join(paragraphs))


def simulated_layout():
    data = json.loads((DATA/'simulated_results.json').read_text(encoding='utf-8'))
    games = data['games']
    names = dict(random=tr('随机','Random'), tactical=tr('一步攻防','Tactical'), shallow=tr('浅层搜索','Shallow'))
    rows = []
    for policy, name in names.items():
        selected = [g for g in games if g['policy'] == policy]
        x, o, d = (sum(g['winner'] == w for g in selected) for w in (1,-1,0))
        rows.append([name, len(selected), x, o, d, f'{100*o/len(selected):.0f}'+r'\%',
                     f'{statistics.mean(len(g["moves"]) for g in selected):.1f}'])
    tabular('simulated-summary.tex', tr(['模拟X策略','局数','X胜','O胜','平局','O胜率','平均步数'],
            ['Synthetic X','Games','X wins','O wins','Draws','O win rate','Mean plies']), rows, 'lrrrrrr')
    for begin, end, name in ((0,15,'simulated-left.tex'),(15,30,'simulated-right.tex')):
        rows = [[i+1, names[g['policy']],g['start_board'],'X' if g['max_first'] else 'O',
                 len(g['moves']), {1:'X',-1:'O',0:tr('平','D')}[g['winner']]]
                for i,g in enumerate(games) if begin <= i < end]
        tabular(name, tr(['局次','策略','起点','先手','步数','胜方'],
                        ['Game','Policy','Start','First','Plies','Win']),rows,'rlccrc')
    chosen = [(1,games[0]), (11,games[10]), (21,games[20]),
              max(enumerate(games,1), key=lambda pair:len(pair[1]['moves']))]
    figures('simulated-figures.tex', [g for _,g in chosen], 'simulated',
            [tr(f'第{i}局，{names[g["policy"]]}，{len(g["moves"])}步',
                f'Game {i}: {names[g["policy"]]}, {len(g["moves"])} plies') for i,g in chosen])


def depth_layout():
    predefined=json.loads((DATA/'depth_predefined_results.json').read_text())['games']
    assert len(predefined)==8
    rows=[]
    for g in predefined:
        rows.append([g['depth'],'MM' if g['minimax_x'] else 'AB', 'MM' if g['minimax_o'] else 'AB',
                     'X' if g['max_first'] else 'O',len(g['moves']),f'{g["total_nodes"]:,}',
                     {1:'X',-1:'O',0:'D'}[g['winner']]])
    tabular('depth-predefined-table.tex',tr(['层数','X算法','O算法','先手','步数','合计节点','胜方'],
            ['Depth','X','O','First','Plies','Total nodes','Winner']),rows,'rcccrrc')
    chosen=[predefined[i] for i in (0,3,4,7)]
    figures('depth-predefined-figures.tex',chosen,'depthpredefined',
            [tr(f'{g["depth"]}层，'+('X' if g['max_first'] else 'O')+'先手',
                f'Depth {g["depth"]}, '+('X' if g['max_first'] else 'O')+' first') for g in chosen])
    for rule in ('local','global'):
        data=json.loads((DATA/f'depth_{rule}_results.json').read_text(encoding='utf-8'))
        games=data['games']
        assert len(games)==90 and len(data['timing_reference'])==5
        rows=[]
        summaries=[]
        for dx,do in data['configs']:
            subset=[g for g in games if (g['depth_x'],g['depth_o'])==(dx,do)]
            x,o,d=(sum(g['winner']==w for g in subset) for w in (1,-1,0))
            nodes=statistics.mean(g['total_nodes'] for g in subset)
            ref=next(r for r in data['timing_reference'] if (r['depth_x'],r['depth_o'])==(dx,do))
            rows.append([dx,do,x,o,d,f'{100*o/18:.1f}'+r'\%',f'{nodes:,.0f}',f'{ref["seconds"]:.2f}'])
            summaries.append((o/18,nodes))
        tabular(f'depth-{rule}-summary.tex',
                tr([r'$d_X$',r'$d_O$','X胜','O胜','平局','O胜率','平均节点','参考耗时/s'],
                   [r'$d_X$',r'$d_O$','X wins','O wins','Draws','O win rate','Mean nodes','Ref. time/s']),rows,'rrrrrrrr')
        rows=[]
        for start,first in data['openings']:
            winners=[]
            for dx,do in data['configs']:
                g=next(g for g in games if (g['depth_x'],g['depth_o'],g['start_board'],g['max_first'])==(dx,do,start,first))
                winners.append({1:'X',-1:'O',0:'D'}[g['winner']])
            rows.append([start,'X' if first else 'O']+winners)
        tabular(f'depth-{rule}-games.tex',tr(['起点','先手'],['Start','First'])+
                [f'$({dx},{do})$' for dx,do in data['configs']],rows,'ccccccc')
        fixed=tr('、',', ').join(f'{100*summaries[i][0]:.1f}'+r'\%' for i in range(3))
        ratios=tr('、',', ').join(f'{summaries[i][1]/summaries[0][1]:.1f}' for i in range(1,5))
        equal=tr('、',', ').join(f'{100*summaries[i][0]:.1f}'+r'\%' for i in (3,4))
        text=tr(f'固定X为三层时，O在三、四、五层的胜率依次为{fixed}。'
                f'双方同时使用四层、五层时，O胜率分别为{equal}。'
                f'其余四种配置的平均节点数相对三层基线分别为{ratios}倍。',
                f'Against depth-three X, O win rates at depths three, four, and five were {fixed}, respectively. '
                f'With both sides at depth four and at depth five, O won {equal}, respectively. '
                f'The other four configurations used {ratios} times the baseline mean node count, respectively.')
        if rule=='global':
            last=[g for g in games if (g['depth_x'],g['depth_o'])==(5,5)]
            draws=sum(g['winner']==0 for g in last)/18
            nonloss=sum(g['winner']!=1 for g in last)/18
            text+=tr(f'双方五层时，平局率为{100*draws:.1f}'+r'\%'+
                     f'，O的不败率为{100*nonloss:.1f}'+r'\%'+
                     '；其胜率虽低于三层对照，但败局也更少，不能仅凭胜率判定退步。',
                     f' At equal depth five, draws accounted for {100*draws:.1f}'+r'\%'+
                     f' and O avoided defeat in {100*nonloss:.1f}'+r'\%'+
                     ' of games. O won less often than in the depth-three control but also lost less often; '
                     'win rate alone does not establish deterioration.')
        write(f'depth-{rule}-analysis.tex',text)


def generate():
    GENERATED.mkdir(exist_ok=True, parents=True)
    FIGURES.mkdir(exist_ok=True)
    data = json.loads((DATA / 'results.json').read_text(encoding='utf-8'))
    games = data['designed']
    wins = sum(g['winner'] == -1 for g in games)
    losses = sum(g['winner'] == 1 for g in games)
    assert len(games) >= 20
    assert len(data['predefined']) == 4
    a,b,c,d = data['predefined']
    macros = dict(DesignedGames=len(games), DesignedWins=wins, DesignedLosses=losses,
                  DesignedDraws=len(games)-wins-losses,
                  DesignedWinRate=f'{wins/len(games):.1%}'.replace('%',r'\%'),
                  DesignedMeanNodes=f'{statistics.mean(g["total_nodes"] for g in games):,.1f}',
                  PruningReductionA=f'{1-b["total_nodes"]/a["total_nodes"]:.1%}'.replace('%',r'\%'),
                  PruningReductionB=f'{1-d["total_nodes"]/c["total_nodes"]:.1%}'.replace('%',r'\%'))
    write('summary.tex','\n'.join('\\newcommand{\\'+key+'}{'+str(value)+'}' for key,value in macros.items()))
    names = {'board_6x10':r'$6\times10$', 'board_5x12':r'$5\times12$',
             'board_3x20':r'$3\times20$', 'empty_chessboard':tr(r'$8\times8$中心挖空',r'$8\times8$ (central hole)')}
    comparison=json.loads((DATA/'csp_comparison.json').read_text(encoding='utf-8'))
    rows=[]
    solved={method:0 for method in comparison['methods']}
    for case in comparison['cases']:
        cells=[]
        for record in case['methods']:
            solved[record['method']]+=record['status']=='solved'
            cells.append(f'{record["search_nodes"]:,}' if record['status']=='solved' else r'$\geq 10^6$*')
        rows.append([names[case['board']],{'dominos':2,'triominos':3,'pentnominos':5}[case['tiles']],
                     f'{case["methods"][0]["placements"]:,}']+cells)
    tabular('csp-table.tex',tr(['棋盘','格数','候选','BT节点','FC节点','AX节点'],
                              ['Board','Size','Candidates','BT nodes','FC nodes','AX nodes']),rows,'lrrrrr')
    rows=[[label,solved[method],12-solved[method]] for method,label in zip(comparison['methods'],
          tr(['传统回溯（BT）','回溯＋前向检查（FC）','Algorithm X＋MRV（AX）'],
             ['Backtracking (BT)','Forward checking (FC)','Algorithm X + MRV (AX)']))]
    tabular('csp-completion.tex',tr(['方法','找到解','达到节点上限'],['Method','Solved','Node cap reached']),rows,'lrr')
    draw_board('csp-6x10.pdf', data['csp'][2]['tiling'], True)
    draw_board('csp-hole.pdf', data['csp'][11]['tiling'], True)
    rows=[]
    for i,g in enumerate(data['predefined'],1):
        xnodes=sum(n for j,n in enumerate(g['nodes_per_move']) if (j%2==0)==g['max_first'])
        rows.append([i, 'MM' if g['minimax_x'] else 'AB', 'MM' if g['minimax_o'] else 'AB',
                     'X' if g['max_first'] else 'O',len(g['moves']),xnodes,g['total_nodes']-xnodes,
                     g['total_nodes'],{1:'X',-1:'O',0:tr('平局','Draw')}[g['winner']]])
    tabular('predefined-table.tex',tr(['局次','X算法','O算法','先手','步数','X节点','O节点','总节点','胜方'],
                                     ['Game','X','O','First','Plies','X nodes','O nodes','Total','Win']),rows,'ccccrrrrc')
    figures('predefined-figures.tex',data['predefined'],'predefined',
            [tr(f'第{i}局，X获胜；{g["total_nodes"]:,}个节点',f'Game {i}: X wins; {g["total_nodes"]:,} nodes')
             for i,g in enumerate(data['predefined'],1)])
    for begin,end,name in [(0,20,'random-left.tex'),(20,40,'random-right.tex')]:
        rows=[[i+1,g['start_board'],'X' if g['max_first'] else 'O',len(g['moves']),
               f"{g['total_nodes']:,}",{1:'X',-1:'O',0:tr('平局','Draw')}[g['winner']]]
              for i,g in enumerate(games) if begin<=i<end]
        tabular(name,tr(['局次','起点','先手','步数','节点数','胜方'],
                        ['Game','Start','First','Plies','Nodes','Win']),rows,'ccccrc')
    tuning = json.loads((DATA/'mobility_tuning.json').read_text(encoding='utf-8'))
    raw = json.loads((DATA/'tuning.json').read_text(encoding='utf-8'))
    initial = next(t for t in raw if t['weights']==[160,160,600,600,35])
    best_raw = max(raw,key=lambda t:t['wins'])
    rows = [[tr('安全落子数量','Safe-move count'),35,initial['wins']],
            [tr('安全落子数量','Safe-move count'),best_raw['weights'][-1],best_raw['wins']]]
    rows += [[tr('安全落子比例','Safe-move ratio'),t['weights'][-1],t['wins']] for t in tuning
             if t['mode']=='ratio' and t['weights'][-1] in (1000,3000,6000)]
    tabular('tuning-table.tex',tr(['行动指标','指标权重','开发胜局 / 18'],
                                ['Mobility feature','Weight','Development wins / 18']),rows,'lrr')
    chosen,seen=[],set()
    for i,g in enumerate(games,1):
        key=(g['start_board'],g['max_first'])
        if g['winner']==-1 and key not in seen:
            chosen.append((i,g))
            seen.add(key)
        if len(chosen)==4:
            break
    figures('designed-figures.tex',[g for _,g in chosen],'designed',
            [tr(f'第{i}局：起点{g["start_board"]}，'+('X' if g['max_first'] else 'O')+'先手',
                f'Game {i}: start {g["start_board"]}, '+('X' if g['max_first'] else 'O')+' first')
             for i,g in chosen])
    ends=[ending(g) for _,g in chosen]
    if all(safe==0 for _,safe in ends):
        counts=tr('、',', ').join(str(n) for n,_ in ends)
        write('designed-analysis.tex',tr(f'四个终盘的前一手，X分别有{counts}个合法落点，'
              '但没有任何一个能够避免O下一手获胜。取胜机会已由此前的威胁与导向形成，'
              '并非仅依赖X在最后一步漏挡三连。',
              f'Immediately before the final move, X had {counts} legal choices in the four games, '
              'respectively, but none could prevent O from winning on the next turn. '
              'The preceding threats and routing had already forced the outcome; '
              'these wins did not merely depend on X overlooking a final block.'))
    else:
        write('designed-analysis.tex','\n\n'.join(tr(f'第{i}局在终盘前一手有{n}个合法落点，'
              f'其中{safe}个可避免对手下一手立即获胜。',
              f'In game {i}, {safe} of {n} legal choices could avoid an immediate loss at the penultimate turn.')
              for (i,_),(n,safe) in zip(chosen,ends)))
    human_file=DATA/'human_games.json'
    humans=json.loads(human_file.read_text(encoding='utf-8')) if human_file.exists() else []
    human_layout(humans)
    simulated_layout()
    extra_layout()
    depth_layout()
    print('Generated tables and vector figures from measured results.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('zh','en'),default='zh')
    LANGUAGE=parser.parse_args().language
    if LANGUAGE=='en':
        GENERATED=GENERATED/'en'
    generate()
