"""Rule and search checks for the global-board game, plus full replay."""
from pathlib import Path
import json
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'submission'))
from uttt import globalTicTacToe


class GlobalRules(unittest.TestCase):
    def win_local(self, game, idx, symbol):
        r, c = game.globalIdx[idx]
        game.board[r][c:c+3] = [symbol]*3

    def test_local_win_not_global_and_closed(self):
        g = globalTicTacToe()
        self.win_local(g, 0, 'X')
        self.assertEqual(g.checkWinner(), 0)
        self.assertEqual(g.localStatus()[0], 'X')
        self.assertTrue(all(r >= 3 or c >= 3 for r, c in g.legalMoves(0)))
        self.assertEqual(len(g.legalMoves(0)), 72)

    def test_global_lines_and_draws(self):
        for side, symbol in ((1,'X'),(-1,'O')):
            g = globalTicTacToe()
            for idx in (0,4,8):
                self.win_local(g, idx, symbol)
            self.assertEqual(g.checkWinner(), side)
            self.assertEqual(g.legalMoves(3), [])
        g = globalTicTacToe()
        pattern = ('XOX','XOO','OXX')
        for br, bc in g.globalIdx:
            for r in range(3):
                g.board[br+r][bc:bc+3] = pattern[r]
        self.assertEqual(g.localStatus(), ('D',)*9)
        self.assertEqual(g.checkWinner(), 0)
        self.assertFalse(g.checkMovesLeft())
        self.assertEqual(g.legalMoves(4), [])

    def test_macro_draw_blocks_threat(self):
        g = globalTicTacToe()
        self.win_local(g, 0, 'X')
        self.win_local(g, 1, 'X')
        for r, values in enumerate(('XOX','XOO','OXX')):
            g.board[r][6:9] = values
        self.assertEqual(g.checkWinner(), 0)
        self.assertEqual(g.localStatus()[2], 'D')

    def test_global_immediate_win_and_search(self):
        for side,symbol in ((True,'X'),(False,'O')):
            g = globalTicTacToe()
            for idx in (0,1):
                self.win_local(g, idx, symbol)
            g.board[0][6:8] = [symbol,symbol]
            before = [row[:] for row in g.board]
            ab = g.chooseMove(2, side, False)
            mm = g.chooseMove(2, side, True)
            self.assertEqual(ab[:2], ((0,8),10000 if side else -10000))
            self.assertEqual(ab[:2], mm[:2])
            self.assertLessEqual(ab[2], mm[2])
            self.assertEqual(g.board, before)

    def test_replay(self):
        path = Path(__file__).with_name('extra_results.json')
        if not path.exists():
            self.skipTest('Run extra experiment first')
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data['games']), 10)
        for record in data['games']:
            g = globalTicTacToe()
            idx, side = record['start_board'], record['max_first']
            closed = {}
            for i, move in enumerate(record['moves']):
                self.assertEqual(g.checkWinner(), 0)
                self.assertIn(tuple(move), g.legalMoves(idx))
                g.board[move[0]][move[1]] = 'X' if side else 'O'
                self.assertEqual(g.board, record['boards'][i])
                for j, state in enumerate(g.localStatus()):
                    cells = g._local(j)
                    if j in closed:
                        self.assertEqual(cells, closed[j])
                    elif state != '_':
                        closed[j] = cells
                idx, side = g._destination(move), not side
            self.assertEqual(g.checkWinner(), record['winner'])
            self.assertEqual(list(g.localStatus()), record['local_status'])
            # Recompute final local/global ownership directly, independently
            # of the solver's cached feature and terminal implementations.
            lines=((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
            ownership=[]
            for br,bc in g.globalIdx:
                cells=[g.board[br+r][bc+c] for r in range(3) for c in range(3)]
                found=next((symbol for symbol in ('X','O')
                            if any(all(cells[k]==symbol for k in line) for line in lines)),None)
                ownership.append(found or ('_' if '_' in cells else 'D'))
            expected=next((1 if symbol=='X' else -1 for symbol in ('X','O')
                           if any(all(ownership[k]==symbol for k in line) for line in lines)),0)
            self.assertEqual(ownership,record['local_status'])
            self.assertEqual(expected,record['winner'])
            self.assertEqual(sum(record['nodes_per_move']), record['total_nodes'])
            self.assertTrue(g.checkWinner() or not g.checkMovesLeft())


if __name__ == '__main__':
    unittest.main(verbosity=2)
