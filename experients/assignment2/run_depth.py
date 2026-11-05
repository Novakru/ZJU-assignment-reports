"""Depth controls with unchanged heuristics; never modifies human records."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'submission'))
from uttt import ultimateTicTacToe, globalTicTacToe

CONFIGS = ((3, 3), (3, 4), (3, 5), (4, 4), (5, 5))
OPENINGS = [(board, first) for board in range(9) for first in (False, True)]


def human_digest(path):
    records=json.loads(Path(path).read_text(encoding='utf-8'))
    canonical=json.dumps(records,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def play(rule, depth_x, depth_o, start, first):
    game = (globalTicTacToe if rule == 'global' else ultimateTicTacToe)()
    record = dict(rule=rule, source='automatic_depth_control', human=False,
                  depth_x=depth_x, depth_o=depth_o, start_board=start, max_first=first,
                  initial_board=[r[:] for r in game.board], moves=[], boards=[],
                  nodes_per_move=[], values=[], seconds_per_move=[])
    idx, side = start, first
    started = time.perf_counter()
    while not game.checkWinner() and game.checkMovesLeft():
        game.maxDepth = depth_x if side else depth_o
        before = time.perf_counter()
        move, value, nodes = game.chooseMove(idx, side, False, rule == 'local' and not side)
        record['seconds_per_move'].append(time.perf_counter()-before)
        game.board[move[0]][move[1]] = 'X' if side else 'O'
        record['moves'].append(move)
        record['boards'].append([r[:] for r in game.board])
        record['nodes_per_move'].append(nodes)
        record['values'].append(value)
        idx, side = game._destination(move), not side
    record.update(winner=game.checkWinner(), seconds=time.perf_counter()-started,
                  total_nodes=sum(record['nodes_per_move']))
    if rule == 'global':
        record['local_status'] = game.localStatus()
    return record


def play_job(job):
    return play(*job)


def run(rule, workers=1):
    output = Path(__file__).with_name(f'depth_{rule}_results.json')
    human = Path(__file__).with_name('human_games.json')
    data = dict(rule=rule, configs=CONFIGS, openings=OPENINGS, source='automatic_depth_control',
                human=False, human_reference_sha256=human_digest(human),
                human_reference_hash_basis='canonical-json-v1',
                human_reference_raw_sha256=hashlib.sha256(human.read_bytes()).hexdigest(),
                environment=dict(python=sys.version, platform=platform.platform(),
                                 processor=platform.processor()), games=[])
    if output.exists():
        saved = json.loads(output.read_text(encoding='utf-8'))
        if saved['configs'] != [list(c) for c in CONFIGS] or saved['openings'] != [list(o) for o in OPENINGS]:
            raise ValueError('Existing protocol differs; preserve it before starting a new experiment.')
        if saved['human_reference_sha256'] != data['human_reference_sha256']:
            raise ValueError('Human records changed; investigate instead of relabeling their depth.')
        data = saved
    completed = {(g['depth_x'],g['depth_o'],g['start_board'],g['max_first']) for g in data['games']}
    jobs=[(rule,dx,do,start,first) for dx,do in CONFIGS for start,first in OPENINGS
          if (dx,do,start,first) not in completed]

    def save(records):
        for record in records:
            data['games'].append(record)
            temp = output.with_suffix('.json.tmp')
            temp.write_bytes((json.dumps(data,separators=(',',':'))+'\n').encode('utf-8'))
            temp.replace(output)
            print(rule, f'{record["depth_x"]}:{record["depth_o"]}', 'start',record['start_board'],
                  'X first',record['max_first'],'winner',record['winner'],
                  'nodes',record['total_nodes'],'seconds',round(record['seconds'],3),flush=True)
    if workers==1:
        save(map(play_job,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            save(pool.map(play_job,jobs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rule',choices=('local','global'))
    parser.add_argument('--workers',type=int,choices=range(1,5),default=1)
    args=parser.parse_args()
    run(args.rule,args.workers)
