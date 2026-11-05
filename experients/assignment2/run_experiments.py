"""Reproduce measured results; original starter validators are unchanged."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'submission'))
import json
import platform
import random
import time
import numpy as np
import instances
from Pentomino import check_correctness
from solve import solve
from uttt import ultimateTicTacToe

OUT = Path(__file__).resolve().parent


def run():
    results = dict(environment=dict(python=sys.version, platform=platform.platform(),
                                   numpy=np.__version__), csp=[], predefined=[], designed=[])
    for board_name in ('board_6x10', 'board_5x12', 'board_3x20', 'empty_chessboard'):
        for tile_name in ('dominos', 'triominos', 'pentnominos'):
            board, tiles = getattr(instances, board_name), getattr(instances, tile_name)
            before, tile_copies = board.copy(), [p.copy() for p in tiles]
            start = time.perf_counter()
            solution = solve(board, tiles)
            elapsed = time.perf_counter() - start
            assert check_correctness(solution, board, tiles), (board_name, tile_name)
            assert np.array_equal(before, board)
            assert all(np.array_equal(a, b) for a, b in zip(tiles, tile_copies))
            image = np.zeros(board.shape, dtype=int)
            for p, (r, c) in solution:
                region = image[r:r + p.shape[0], c:c + p.shape[1]]
                region[p != 0] = p[p != 0]
            record = dict(board=board_name, tiles=tile_name, seconds=elapsed,
                          valid=True, stats=solve.last_stats, tiling=image.tolist())
            results['csp'].append(record)
            print('CSP', board_name, tile_name, round(elapsed, 4), flush=True)
    for first, mm_x, mm_o in ((True, True, True), (True, True, False),
                               (False, False, True), (False, False, False)):
        game = ultimateTicTacToe()
        start = time.perf_counter()
        game.playGamePredifinedAgent(first, mm_x, mm_o)
        record = dict(game.last_game, minimax_x=mm_x, minimax_o=mm_o,
                      seconds=time.perf_counter() - start)
        results['predefined'].append(record)
        print('PREDEFINED', first, mm_x, mm_o, record['winner'], record['total_nodes'], flush=True)
    # Randomization protocol fixed before collecting results; no seed filtering.
    rng = random.Random(448)
    for i in range(40):
        game = ultimateTicTacToe()
        board_idx, first = rng.randrange(9), bool(rng.getrandbits(1))
        start = time.perf_counter()
        game._play(first, board_idx, (False, False), True)
        record = dict(game.last_game, seconds=time.perf_counter() - start)
        results['designed'].append(record)
        print('DESIGNED', i + 1, board_idx, first, record['winner'], record['total_nodes'], flush=True)
        (OUT / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('WIN RATE', sum(g['winner'] == -1 for g in results['designed']) / 40, flush=True)


if __name__ == '__main__':
    run()
