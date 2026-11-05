"""Click-to-play human experiment. Uses only Python's standard library."""
from pathlib import Path
from random import Random
from queue import Queue, Empty
from threading import Thread
import argparse
import json
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'submission'))
from uttt import ultimateTicTacToe, LINES

OUTPUT = ROOT / 'experients/assignment2/human_games.json'
BLUE, RED, INK = '#003f88', '#a43c38', '#243447'
BG, MUTED = '#f5f6f8', '#526175'


class HumanSession:
    def __init__(self, output=OUTPUT):
        self.output = Path(output)
        self.records = json.loads(self.output.read_text(encoding='utf-8')) if self.output.exists() else []
        if not isinstance(self.records, list) or any(g.get('human') is not True for g in self.records):
            raise ValueError('真人记录格式不正确，请先检查记录文件；现有数据没有被修改。')
        self.game = None
        self.saved = False

    def start(self):
        if self.game and not self.finished:
            raise ValueError('请先完成当前对局。')
        rng = Random(448)
        for _ in self.records:
            rng.randrange(9)
            rng.getrandbits(1)
        self.idx, self.side = rng.randrange(9), bool(rng.getrandbits(1))
        self.game, self.saved = ultimateTicTacToe(), False
        self.record = dict(start_board=self.idx, max_first=self.side, human=True,
                           source='human_gui', depth=3, initial_board=[r[:] for r in self.game.board],
                           moves=[], boards=[], nodes_per_move=[], values=[])

    @property
    def finished(self):
        return self.game is not None and (bool(self.game.checkWinner()) or not self.game.checkMovesLeft())

    def move(self, move, value=None, nodes=0):
        if self.finished or move not in self.game.legalMoves(self.idx):
            raise ValueError('请在高亮区域的空格落子。')
        r, c = move
        self.game.board[r][c] = 'X' if self.side else 'O'
        self.record['moves'].append(move)
        self.record['boards'].append([row[:] for row in self.game.board])
        self.record['nodes_per_move'].append(nodes)
        self.record['values'].append(value)
        self.idx, self.side = self.game._destination(move), not self.side

    def save(self):
        if not self.finished or self.saved:
            return
        # Refuse to overwrite a log changed by another open game window.
        current = json.loads(self.output.read_text(encoding='utf-8')) if self.output.exists() else []
        if current != json.loads(json.dumps(self.records)):
            raise ValueError('记录已被其他窗口更新。请保留本窗口，关闭其他对局窗口后处理记录冲突。')
        record = dict(self.record, winner=self.game.checkWinner(),
                      total_nodes=sum(self.record['nodes_per_move']))
        self.output.parent.mkdir(parents=True, exist_ok=True)
        temp = self.output.with_suffix('.json.tmp')
        temp.write_text(json.dumps(self.records + [record], indent=2)+'\n', encoding='utf-8')
        temp.replace(self.output)
        self.records.append(record)
        self.saved = True


class GameWindow:
    def __init__(self, root, output=OUTPUT):
        self.root, self.session = root, HumanSession(output)
        self.queue, self.busy, self.building = Queue(), False, False
        self.focus_cell = (4, 4)
        root.title('UTTT · 真人对战 | ECE2013')
        root.geometry('1020x760')
        root.minsize(900, 700)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TButton', font=('Microsoft YaHei UI', 11), padding=(14, 10))
        style.configure('Primary.TButton', background=BLUE, foreground='white')
        style.map('Primary.TButton', background=[('active', '#185a9f'), ('disabled', '#dce2e9')],
                  foreground=[('disabled', MUTED)])
        top = tk.Frame(root, bg=BG)
        top.pack(fill='x', padx=30, pady=(24, 16))
        tk.Label(top, text='Ultimate Tic-Tac-Toe', font=('Georgia', 24), fg=INK, bg=BG).pack(anchor='w')
        tk.Label(top, text='真人执 X  /  智能体执 O    ·    任一小棋盘先连成三子即获胜',
                 font=('Microsoft YaHei UI', 11), fg=MUTED, bg=BG).pack(anchor='w', pady=(8, 0))
        body = tk.Frame(root, bg=BG)
        body.pack(fill='both', expand=True, padx=30)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(body, bg=BG, highlightthickness=0, takefocus=True)
        self.canvas.grid(row=0, column=0, sticky='nsew', padx=(0, 28))
        self.canvas.bind('<Configure>', lambda e: self.draw())
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Key>', self.key)
        panel = tk.Frame(body, bg=BG, width=270)
        panel.grid(row=0, column=1, sticky='ns')
        panel.grid_propagate(False)
        self.status = tk.Label(panel, text='', font=('Microsoft YaHei UI', 18, 'bold'),
                               bg=BG, fg=BLUE, wraplength=268, justify='left')
        self.status.pack(anchor='w', pady=(14, 8))
        self.detail = tk.Label(panel, text='', font=('Microsoft YaHei UI', 11), bg=BG,
                               fg=INK, wraplength=260, justify='left')
        self.detail.pack(anchor='w', pady=(0, 22))
        self.next_button = ttk.Button(panel, text='开始对局', style='Primary.TButton', command=self.start)
        self.next_button.pack(fill='x')
        tk.Label(panel, text='怎样落子', font=('Microsoft YaHei UI', 12, 'bold'), bg=BG, fg=INK).pack(anchor='w', pady=(30, 8))
        tk.Label(panel, text='点击蓝色区域里的空格。\n你的落子位置会决定对手下一步\n必须进入哪个小棋盘。\n\n目标小棋盘填满时，可任选空格。\n任一方在一个小棋盘内三连即获胜。\n\n键盘：方向键移动，空格或回车落子。',
                 font=('Microsoft YaHei UI', 10), bg=BG, fg=MUTED, justify='left').pack(anchor='w')
        self.tally = tk.Label(panel, font=('Microsoft YaHei UI', 10), bg=BG, fg=INK, justify='left')
        self.tally.pack(anchor='w', pady=(24, 12))
        self.build_button = ttk.Button(panel, text='更新中英文报告', command=self.build_report)
        self.build_button.pack(fill='x')
        self.build_note = tk.Label(panel, text='完成的对局自动保存，可关闭后续玩。', font=('Microsoft YaHei UI', 9),
                                    bg=BG, fg=MUTED, wraplength=265, justify='left')
        self.build_note.pack(anchor='w', pady=(10, 0))
        tk.Label(root, text='蓝底：可落子区域    ·    小圆点：合法空格    ·    方框：上一手',
                 font=('Microsoft YaHei UI', 10), bg=BG, fg=MUTED).pack(anchor='w', padx=30, pady=(14, 20))
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.refresh()
        root.after(60, self.poll)

    def start(self):
        try:
            self.session.save()  # Retry any previously failed save before starting another game.
            self.session.start()
        except (OSError, ValueError) as exc:
            messagebox.showerror('无法开始下一局', str(exc), parent=self.root)
            return
        self.focus_cell = self.session.game.legalMoves(self.session.idx)[0]
        self.refresh()
        self.agent_turn()

    def refresh(self):
        s = self.session
        n = len(s.records)
        wins = sum(g['winner'] == 1 for g in s.records)
        losses = sum(g['winner'] == -1 for g in s.records)
        self.tally.config(text=f'真人实验：已保存 {n} 局 / 至少 10 局\n真人 {wins} 胜 · {losses} 负 · {n-wins-losses} 平')
        if s.game is None:
            self.status.config(text='准备好就开始')
            self.detail.config(text='开局与先手随机分配。\n不需要输入行列坐标。')
        elif s.finished:
            self.status.config(text={1:'你赢了！', -1:'智能体获胜', 0:'本局平局'}[s.game.checkWinner()])
            self.detail.config(text=f'共 {len(s.record["moves"])} 步 · '+('结果已自动保存' if s.saved else '结果尚未保存，请重试'))
        else:
            self.status.config(text='轮到你了 · X' if s.side else '智能体思考中 · O')
            area = sorted({3*(r//3)+c//3+1 for r,c in s.game.legalMoves(s.idx)})
            self.detail.config(text=f'第 {n+1} 局 · 已走 {len(s.record["moves"])} 步\n'+
                               (f'请在第 {area[0]} 个小棋盘落子。' if len(area)==1 else '可以任选高亮空格落子。'))
        self.next_button.config(text='下一局' if s.game else '开始对局',
                                state='normal' if (not s.game or s.finished) and not self.building else 'disabled')
        self.build_button.config(state='normal' if (not s.game or s.finished) and not self.building else 'disabled')
        self.draw()

    def draw(self):
        c, s = self.canvas, self.session
        c.delete('all')
        self.size = max(90, min(c.winfo_width()-8, c.winfo_height()-8))
        self.left = (c.winfo_width()-self.size)/2
        self.top = (c.winfo_height()-self.size)/2
        step = self.size/9
        board = s.game.board if s.game else [['_']*9 for _ in range(9)]
        legal = set(s.game.legalMoves(s.idx)) if s.game and not s.finished else set()
        for r in range(9):
            for col in range(9):
                x, y = self.left+col*step, self.top+r*step
                active = (r,col) in legal
                c.create_rectangle(x,y,x+step,y+step,fill='#e8f0fa' if active else 'white',outline='')
                mark = board[r][col]
                pad = step*.28
                if mark == 'X':
                    c.create_line(x+pad,y+pad,x+step-pad,y+step-pad,fill=RED,width=2.5)
                    c.create_line(x+step-pad,y+pad,x+pad,y+step-pad,fill=RED,width=2.5)
                elif mark == 'O':
                    c.create_oval(x+pad,y+pad,x+step-pad,y+step-pad,outline=BLUE,width=2.5)
                elif active:
                    c.create_oval(x+step/2-2,y+step/2-2,x+step/2+2,y+step/2+2,fill='#466c97',outline='')
        for i in range(10):
            width, color = (2, INK) if i%3==0 else (1, '#cbd3dc')
            x,y = self.left+i*step,self.top+i*step
            c.create_line(x,self.top,x,self.top+self.size,fill=color,width=width)
            c.create_line(self.left,y,self.left+self.size,y,fill=color,width=width)
        for i in range(9):
            c.create_text(self.left+(i%3)*3*step+7,self.top+(i//3)*3*step+7,
                          text=str(i+1),anchor='nw',fill=MUTED,font=('Segoe UI',8))
        if s.game and s.record['moves']:
            r,col = s.record['moves'][-1]
            x,y = self.left+col*step,self.top+r*step
            c.create_rectangle(x+4,y+4,x+step-4,y+step-4,outline=BLUE,width=1)
        if s.finished and s.game.checkWinner():
            mark = 'X' if s.game.checkWinner()==1 else 'O'
            for br,bc in s.game.globalIdx:
                for line in LINES:
                    coords = [(br+i//3,bc+i%3) for i in line]
                    if all(board[r][col]==mark for r,col in coords):
                        (r0,c0),_,(r1,c1)=coords
                        c.create_line(self.left+(c0+.5)*step,self.top+(r0+.5)*step,
                                      self.left+(c1+.5)*step,self.top+(r1+.5)*step,
                                      fill=RED if mark=='X' else BLUE,width=4)
        if c.focus_get()==c and s.game and s.side and not s.finished:
            r,col=self.focus_cell
            x,y=self.left+col*step,self.top+r*step
            c.create_rectangle(x+2,y+2,x+step-2,y+step-2,outline=INK,width=2,dash=(3,2))

    def click(self, event):
        self.canvas.focus_set()
        col=int((event.x-self.left)//(self.size/9))
        r=int((event.y-self.top)//(self.size/9))
        self.human_move((r,col))

    def key(self, event):
        r,c=self.focus_cell
        dr,dc={'Up':(-1,0),'Down':(1,0),'Left':(0,-1),'Right':(0,1)}.get(event.keysym,(0,0))
        self.focus_cell=(max(0,min(8,r+dr)),max(0,min(8,c+dc)))
        if event.keysym in ('space','Return'):
            self.human_move(self.focus_cell)
        self.draw()

    def human_move(self, move):
        s=self.session
        if self.busy or not s.game or s.finished or not s.side:
            return
        if move not in s.game.legalMoves(s.idx):
            self.root.bell()
            self.detail.config(text='这里不能落子，请点击蓝色区域中的空格。')
            return
        self.focus_cell=move
        s.move(move)
        self.after_move()

    def after_move(self):
        if self.session.finished:
            try:
                self.session.save()
            except (OSError,ValueError) as exc:
                messagebox.showerror('对局尚未保存', f'{exc}\n点击“下一局”可重试保存。', parent=self.root)
        self.refresh()
        self.agent_turn()

    def agent_turn(self):
        s=self.session
        if self.busy or s.finished or s.side:
            return
        self.busy=True
        # Search a separate board: Tk stays responsive and the displayed board never mutates mid-search.
        game=ultimateTicTacToe()
        game.board=[r[:] for r in s.game.board]
        idx=s.idx
        def work():
            try:
                self.queue.put(('move',game.chooseMove(idx,False,False,True)))
            except Exception as exc:
                self.queue.put(('error',str(exc)))
        Thread(target=work,daemon=True).start()

    def poll(self):
        try:
            kind,payload=self.queue.get_nowait()
            if kind=='move':
                self.busy=False
                move,value,nodes=payload
                self.session.move(move,value,nodes)
                self.after_move()
            elif kind=='error':
                self.busy=False
                self.status.config(text='智能体计算失败')
                self.detail.config(text='请关闭窗口后重试；已完成的对局仍保留。')
                messagebox.showerror('计算失败',payload,parent=self.root)
            elif kind=='build':
                self.building=False
                self.refresh()
                self.build_note.config(text='中英文报告已更新。' if payload else '报告生成失败，详情见 report/previews/gui-build.log。')
        except Empty:
            pass
        self.root.after(60,self.poll)

    def build_report(self):
        if self.building:
            return
        self.building=True
        self.refresh()
        self.build_note.config(text='正在生成中英文报告，请稍候…')
        def work():
            log=ROOT/'report/previews/gui-build.log'
            log.parent.mkdir(exist_ok=True,parents=True)
            wrapper=ROOT.parent/'experiments/build_report.py'
            command=([sys.executable,'-B',str(wrapper)] if wrapper.exists() else
                     ['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'report/build.ps1')])
            try:
                with log.open('w',encoding='utf-8') as stream:
                    result=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,
                                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                self.queue.put(('build',result.returncode==0))
            except OSError as exc:
                log.write_text(str(exc),encoding='utf-8')
                self.queue.put(('build',False))
        Thread(target=work,daemon=True).start()

    def close(self):
        if self.building:
            messagebox.showinfo('报告正在更新','请等待报告生成完成后关闭窗口。',parent=self.root)
            return
        s=self.session
        if s.game and not s.saved:
            if not messagebox.askyesno('退出当前对局？','当前这一局尚未保存，退出后需重玩。此前完成的对局已保留。',parent=self.root):
                return
        self.root.destroy()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    args=parser.parse_args()
    root=tk.Tk()
    try:
        GameWindow(root,args.output)
    except (OSError,ValueError) as exc:
        root.withdraw()
        messagebox.showerror('无法读取对局记录',str(exc),parent=root)
        root.destroy()
        return 1
    root.mainloop()
    return 0


if __name__=='__main__':
    raise SystemExit(main())
