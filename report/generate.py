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
from uttt import ultimateTicTacToe, LINES


def write(name, text):
    (GENERATED / name).write_bytes((text + '\n').encode('utf-8'))


def tr(zh, en):
    return en if LANGUAGE == 'en' else zh


def tabular(name, columns, rows, alignment):
    lines = [r'\begin{tabular}{' + alignment + '}', r'\toprule',
             ' & '.join(map(str, columns)) + r' \\', r'\midrule']
    lines.extend(' & '.join(map(str, row)) + r' \\' for row in rows)
    lines.extend([r'\bottomrule', r'\end{tabular}'])
    write(name, '\n'.join(lines))


def draw_board(name, board, tiling=False):
    size = 20
    nr, nc = len(board), len(board[0])
    c = canvas.Canvas(str(FIGURES / name), pagesize=(nc*size, nr*size), invariant=1)
    palette = ['#ffffff','#d8e4ed','#ecdbcf','#dce7d7','#eae3c8','#e1dcee',
               '#e9d8de','#d3e5e3','#e7ded0','#d9dff0','#e5e7cc','#eddbd7','#d5e3ec']
    for r, row in enumerate(board):
        for col, cell in enumerate(row):
            x, y = col*size, (nr-r-1)*size
            shade = palette[int(cell) % len(palette)] if tiling else '#ffffff'
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
    c.showPage()
    c.save()


def figures(name, records, prefix, labels):
    lines = [r'\begin{figure}[htbp]', r'\centering']
    for i, (record, label) in enumerate(zip(records, labels)):
        filename = f'{prefix}-{i+1}.pdf'
        draw_board(filename, record['boards'][-1])
        lines.extend([r'\begin{subfigure}[t]{.46\linewidth}', r'\centering',
                      r'\includegraphics[height=48mm]{figures/' + filename + '}',
                      r'\caption{' + label + '}', r'\end{subfigure}'])
        if i % 2 == 0 and i+1 < len(records):
            lines.append(r'\hfill')
        elif i+1 < len(records):
            lines.append(r'\par\medskip')
    captions = {'predefined':tr('预定义智能体的最终棋盘。','Final boards of the predefined agents.'),
                'designed':tr('自定义智能体对局的代表终盘。','Representative final boards of the designed agent.'),
                'human':tr('真人对战的代表终盘。','Representative final boards of the human games.')}
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
    rows = [[names[g['board']], {'dominos':2,'triominos':3,'pentnominos':5}[g['tiles']],
             g['stats']['placements'], g['stats']['search_nodes'], f"{g['seconds']*1000:.2f}"]
            for g in data['csp']]
    tabular('csp-table.tex',tr(['棋盘','骨牌格数','候选放置','搜索节点','耗时 / ms'],
                              ['Board','Tile size','Placements','Search nodes','Time / ms']),rows,'lrrrr')
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
    if not humans:
        write('human-results.tex',tr('真人对战实验尚未完成，胜率、代表棋盘与实测讨论待补充。',
                                    'The human experiment has not yet been completed. '
                                    'Its win rate, representative boards, and empirical discussion remain to be added.'))
    else:
        hwins=sum(g['winner']==1 for g in humans)
        owins=sum(g['winner']==-1 for g in humans)
        draws=len(humans)-hwins-owins
        text=tr(f'目前完成{len(humans)}局，真人获胜{hwins}局，智能体获胜{owins}局，平局{draws}局，'
                f'真人胜率为{hwins/len(humans):.1%}。',
                f'In {len(humans)} completed games, the human won {hwins}, the agent won {owins}, '
                f'and {draws} were drawn. The human win rate was {hwins/len(humans):.1%}.').replace('%',r'\%')
        if len(humans)<10:
            text+=tr('对局数不足10局，仍需补充。','Fewer than ten games have been completed; more are required.')
        else:
            text+=tr('当前样本中真人全部获胜。','The human won every game in this sample.') if hwins==len(humans) else tr(
                     '当前样本中真人并非总能获胜。','The human did not win every game in this sample.')
        figures('human-figures.tex',humans[:4],'human',[tr(f'真人对战第{i+1}局',f'Human game {i+1}')
                                                     for i in range(min(4,len(humans)))])
        # English and Chinese entry points resolve their own generated data.
        human_input='generated/en/human-figures.tex' if LANGUAGE=='en' else 'generated/human-figures.tex'
        write('human-results.tex',text+'\n'+r'\input{'+human_input+'}')
    print('Generated tables and vector figures from measured results.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('zh','en'),default='zh')
    LANGUAGE=parser.parse_args().language
    if LANGUAGE=='en':
        GENERATED=GENERATED/'en'
    generate()
