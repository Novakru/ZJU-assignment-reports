"""Behavioral checks for required rules, search equivalence, and saved traces."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'submission'))
import json
import random
import unittest
import numpy as np
from solve import solve
from uttt import ultimateTicTacToe


class RulesAndSearch(unittest.TestCase):
    def test_tiers_and_terminal(self):
        g = ultimateTicTacToe()
        g.board[0][0] = 'X'
        self.assertEqual(g.evaluatePredifined(True), 30)
        g.board[0][1] = 'X'
        self.assertEqual(g.evaluatePredifined(True), 500)
        g.board[0][2] = 'O'
        self.assertEqual(g.evaluatePredifined(False), -500)
        g.board[1][0] = g.board[1][1] = g.board[1][2] = 'O'
        self.assertEqual(g.checkWinner(), -1)
        self.assertEqual(g.evaluatePredifined(True), -10000)

    def test_full_target(self):
        g = ultimateTicTacToe()
        pattern = ('XOX', 'XOO', 'OXX')
        for r in range(3):
            g.board[r][:3] = pattern[r]
        self.assertEqual(g.checkWinner(), 0)
        self.assertEqual(len(g.legalMoves(0)), 72)

    def test_search_equivalence(self):
        rng = random.Random(123)
        for _ in range(15):
            g = ultimateTicTacToe()
            idx, side = rng.randrange(9), bool(rng.getrandbits(1))
            for step in range(rng.randrange(0, 18)):
                move = rng.choice(g.legalMoves(idx))
                g.board[move[0]][move[1]] = 'X' if side else 'O'
                idx, side = g._destination(move), not side
                if g.checkWinner():
                    break
            if g.checkWinner():
                continue
            before = [row[:] for row in g.board]
            for designed in (False, True):
                mm = g.chooseMove(idx, side, True, designed)
                ab = g.chooseMove(idx, side, False, designed)
                self.assertEqual(mm[:2], ab[:2])
                self.assertLessEqual(ab[2], mm[2])
                self.assertEqual(g.board, before)

    def test_forced_local_wins_and_ties(self):
        for side, symbol in ((True, 'X'), (False, 'O')):
            g = ultimateTicTacToe()
            g.board[3][3] = g.board[3][4] = symbol
            for designed in (False, True):
                move, value, _ = g.chooseMove(4, side, False, designed)
                self.assertEqual(move, (3, 5))
                self.assertEqual(value, 10000 if side else -10000)
        # All horizon values tie at zero: raster order must choose the first.
        g = ultimateTicTacToe()
        g.maxDepth = 1
        g.evaluatePredifined = lambda _: 0
        self.assertEqual(g.chooseMove(4, True, True)[0], (3, 3))
        self.assertEqual(g.chooseMove(4, True, False)[0], (3, 3))

    def test_csp_edges(self):
        board = np.array([[1, 0, 1], [1, 0, 1]])
        tiles = [np.array([[1], [1]]), np.array([[2], [2]])]
        self.assertEqual(len(solve(board, tiles)), 2)
        self.assertEqual(solve(np.ones((1, 3)), tiles), [])
        self.assertEqual(solve(np.zeros((2, 2)), []), [])
        # This needs a reflection/rotation, and uses irregular non-rectangular support.
        solution = solve(np.array([[1, 1], [0, 1]]), [np.array([[1, 0], [1, 1]])])
        self.assertEqual(len(solution), 1)

    def test_replay_saved_games(self):
        path = Path(__file__).with_name('results.json')
        if not path.exists():
            self.skipTest('Run experiments first')
        results = json.loads(path.read_text(encoding='utf-8'))
        for first, second in ((0, 1), (2, 3)):
            a, b = results['predefined'][first], results['predefined'][second]
            self.assertEqual(a['moves'], b['moves'])
            self.assertLess(b['total_nodes'], a['total_nodes'])
        for record in results['predefined'] + results['designed']:
            g = ultimateTicTacToe()
            idx, side = record['start_board'], record['max_first']
            for i, move in enumerate(record['moves']):
                move = tuple(move)
                self.assertEqual(g.checkWinner(), 0)
                self.assertIn(move, g.legalMoves(idx))
                g.board[move[0]][move[1]] = 'X' if side else 'O'
                self.assertEqual(g.board, record['boards'][i])
                idx, side = g._destination(move), not side
            self.assertEqual(g.checkWinner(), record['winner'])
            self.assertEqual(sum(record['nodes_per_move']), record['total_nodes'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
