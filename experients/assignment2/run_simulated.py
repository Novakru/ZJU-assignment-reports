"""Synthetic opponents; these records are never human-play observations."""
from pathlib import Path
import json
import random
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'submission'))
from uttt import ultimateTicTacToe

POLICIES = ('random', 'tactical', 'shallow')
SEED = 20261106


def tactical(game, idx, rng):
    moves = game.legalMoves(idx)
    # Immediate wins take priority over blocks; both precede positional choice.
    for mark, winner in (('X', 1), ('O', -1)):
        candidates = []
        for r, c in moves:
            game.board[r][c] = mark
            wins = game.checkWinner() == winner
            game.board[r][c] = '_'
            if wins:
                candidates.append((r, c))
        if candidates:
            return rng.choice(candidates)
    scores = {m: (2 if (m[0] % 3, m[1] % 3) == (1, 1) else
                  1 if m[0] % 3 != 1 and m[1] % 3 != 1 else 0) for m in moves}
    return rng.choice([m for m in moves if scores[m] == max(scores.values())])


def play(policy, start, first, seed):
    game, rng = ultimateTicTacToe(), random.Random(seed)
    record = dict(source='simulated', human=False, policy=policy, seed=seed,
                  start_board=start, max_first=first, depth=3,
                  initial_board=[row[:] for row in game.board],
                  moves=[], boards=[], nodes_per_move=[], values=[])
    idx, side = start, first
    while not game.checkWinner() and game.checkMovesLeft():
        value, count = None, 0
        if not side:
            move, value, count = game.chooseMove(idx, False, False, True)
        elif policy == 'random' or rng.random() < {'tactical': .15, 'shallow': .10}[policy]:
            move = rng.choice(game.legalMoves(idx))
        elif policy == 'tactical':
            move = tactical(game, idx, rng)
        else:
            game.maxDepth = 2
            move, value, count = game.chooseMove(idx, True, False, False)
            game.maxDepth = 3
        r, c = move
        game.board[r][c] = 'X' if side else 'O'
        record['moves'].append(move)
        record['boards'].append([row[:] for row in game.board])
        record['nodes_per_move'].append(count)
        record['values'].append(value)
        idx, side = game._destination(move), not side
    record.update(winner=game.checkWinner(), total_nodes=sum(record['nodes_per_move']))
    return record


def run():
    rng = random.Random(SEED)
    openings = [(rng.randrange(9), bool(rng.getrandbits(1))) for _ in range(10)]
    data = dict(source='simulated', human=False, seed=SEED, games_per_policy=10,
                error_probability=dict(random=1, tactical=.15, shallow=.10), games=[])
    output = Path(__file__).with_name('simulated_results.json')
    for p, policy in enumerate(POLICIES):
        for i, (start, first) in enumerate(openings):
            record = play(policy, start, first, SEED + 1000 * (p+1) + i)
            data['games'].append(record)
            output.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
            print(policy, i+1, 'winner', record['winner'], 'plies', len(record['moves']), flush=True)


if __name__ == '__main__':
    run()
