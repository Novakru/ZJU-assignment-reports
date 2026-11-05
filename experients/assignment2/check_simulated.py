"""Check synthetic provenance, legal traces, and tactical priorities."""
import json
import random
import unittest
from pathlib import Path
from run_simulated import POLICIES, play, tactical, ultimateTicTacToe


class SimulatedChecks(unittest.TestCase):
    def test_provenance_and_paired_openings(self):
        data = json.loads(Path(__file__).with_name('simulated_results.json').read_text())
        self.assertFalse(data['human'])
        self.assertEqual(data['source'], 'simulated')
        openings = []
        for policy in POLICIES:
            games = [g for g in data['games'] if g['policy'] == policy]
            self.assertEqual(len(games), 10)
            openings.append([(g['start_board'], g['max_first']) for g in games])
            for g in games:
                self.assertFalse(g['human'])
                self.assertEqual(g['source'], 'simulated')
        self.assertTrue(all(o == openings[0] for o in openings))

    def test_replay_and_reproducibility(self):
        data = json.loads(Path(__file__).with_name('simulated_results.json').read_text())
        for record in data['games']:
            game = ultimateTicTacToe()
            idx, side = record['start_board'], record['max_first']
            for move, board in zip(record['moves'], record['boards']):
                self.assertEqual(game.checkWinner(), 0)
                self.assertIn(tuple(move), game.legalMoves(idx))
                game.board[move[0]][move[1]] = 'X' if side else 'O'
                self.assertEqual(game.board, board)
                idx, side = game._destination(move), not side
            self.assertEqual(game.checkWinner(), record['winner'])
            replay = play(record['policy'], record['start_board'], record['max_first'], record['seed'])
            self.assertEqual(json.loads(json.dumps(replay)), record)

    def test_tactical_win_block_and_restore(self):
        for row, expected in ((['X', 'X', '_'], (0, 2)), (['O', 'O', '_'], (0, 2))):
            game = ultimateTicTacToe()
            game.board[0][:3] = row
            before = [r[:] for r in game.board]
            self.assertEqual(tactical(game, 0, random.Random(1)), expected)
            self.assertEqual(game.board, before)


if __name__ == '__main__':
    unittest.main()
