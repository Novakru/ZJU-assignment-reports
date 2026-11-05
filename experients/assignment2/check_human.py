"""Replay genuine GUI/CLI records and independently verify local winners."""
from pathlib import Path
import json
import sys
import unittest

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'submission'))
from uttt import ultimateTicTacToe


def direct_winner(board):
    for br in (0,3,6):
        for bc in (0,3,6):
            lines=[[board[br+r][bc+c] for c in range(3)] for r in range(3)]
            lines += [[board[br+r][bc+c] for r in range(3)] for c in range(3)]
            lines += [[board[br+i][bc+i] for i in range(3)],
                      [board[br+i][bc+2-i] for i in range(3)]]
            for line in lines:
                if line==['X']*3:
                    return 1
                if line==['O']*3:
                    return -1
    return 0


class HumanChecks(unittest.TestCase):
    def test_replay_provenance_and_agent(self):
        path=Path(__file__).with_name('human_games.json')
        if not path.exists():
            self.skipTest('No human games recorded yet')
        records=json.loads(path.read_text(encoding='utf-8'))
        for number,record in enumerate(records,1):
            with self.subTest(game=number):
                self.assertIs(record['human'],True)
                self.assertNotEqual(record.get('source'),'simulated')
                self.assertEqual(record['depth'],3)
                game=ultimateTicTacToe()
                self.assertEqual(record['initial_board'],game.board)
                idx,side=record['start_board'],record['max_first']
                for field in ('boards','values','nodes_per_move'):
                    self.assertEqual(len(record[field]),len(record['moves']))
                for i,move in enumerate(record['moves']):
                    move=tuple(move)
                    self.assertEqual(direct_winner(game.board),0)
                    self.assertIn(move,game.legalMoves(idx))
                    if side:
                        self.assertIsNone(record['values'][i])
                        self.assertEqual(record['nodes_per_move'][i],0)
                    else:
                        chosen,value,nodes=game.chooseMove(idx,False,False,True)
                        self.assertEqual(move,chosen)
                        self.assertEqual(record['values'][i],value)
                        self.assertEqual(record['nodes_per_move'][i],nodes)
                    game.board[move[0]][move[1]]='X' if side else 'O'
                    self.assertEqual(game.board,record['boards'][i])
                    idx,side=game._destination(move),not side
                self.assertEqual(record['winner'],direct_winner(game.board))
                self.assertTrue(record['winner'] or not game.checkMovesLeft())
                self.assertEqual(record['total_nodes'],sum(record['nodes_per_move']))


if __name__=='__main__':
    unittest.main(verbosity=2)
