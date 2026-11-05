"""Reproduce the global-board extra-credit experiment without human data."""
from pathlib import Path
import json
import random
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'submission'))
from uttt import globalTicTacToe


def run():
    output = Path(__file__).with_name('extra_results.json')
    rng = random.Random(2013)
    data = dict(rule='global', seed=2013, depth=3, games=[])
    for i in range(12):
        idx, first = rng.randrange(9), bool(rng.getrandbits(1))
        game = globalTicTacToe()
        start = time.perf_counter()
        game.playGameGlobal(first, idx)
        record = dict(game.last_game, seconds=time.perf_counter()-start)
        data['games'].append(record)
        output.write_bytes((json.dumps(data, indent=2)+'\n').encode('utf-8'))
        print('Extra', i+1, 'start', idx, 'X first', first, 'winner', record['winner'],
              'plies', len(record['moves']), 'nodes', record['total_nodes'], flush=True)


if __name__ == '__main__':
    run()
