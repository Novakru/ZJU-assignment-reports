"""Validate all depth-control traces, fixed openings, and unchanged human data."""
from pathlib import Path
import hashlib
import json
import unittest
from tempfile import TemporaryDirectory
from run_depth import CONFIGS, OPENINGS, ultimateTicTacToe, globalTicTacToe, human_digest
from check_human import direct_winner

DATA=Path(__file__).resolve().parent


def macro_winner(status):
    # Use a separate 3x3 board and the direct row/column/diagonal oracle.
    board=[['_']*9 for _ in range(9)]
    for i,s in enumerate(status):
        board[i//3][i%3]=s
    return direct_winner(board)


class DepthChecks(unittest.TestCase):
    def test_human_freeze_survives_checkout_line_endings(self):
        source=DATA/'human_games.json'
        with TemporaryDirectory() as directory:
            copy=Path(directory)/'human-test-only.json'
            raw=source.read_bytes().replace(b'\r\n',b'\n')
            copy.write_bytes(raw)
            self.assertEqual(human_digest(source),human_digest(copy))
            copy.write_bytes(raw.replace(b'\n',b'\r\n'))
            self.assertEqual(human_digest(source),human_digest(copy))
            changed=json.loads(raw)
            changed[0]['depth']=5
            copy.write_text(json.dumps(changed),encoding='utf-8')
            self.assertNotEqual(human_digest(source),human_digest(copy))

    def test_deeper_predefined_traces_and_pruning(self):
        games=json.loads((DATA/'depth_predefined_results.json').read_text())['games']
        self.assertEqual(len(games),8)
        for depth in (4,5):
            subset=[g for g in games if g['depth']==depth]
            self.assertEqual(len(subset),4)
            for a,b in ((subset[0],subset[1]),(subset[2],subset[3])):
                self.assertEqual(a['moves'],b['moves'])
                self.assertLess(b['total_nodes'],a['total_nodes'])
            for record in subset:
                game=ultimateTicTacToe()
                self.assertFalse(record['human'])
                self.assertEqual(record['start_board'],4)
                idx,side=4,record['max_first']
                for move,board in zip(record['moves'],record['boards']):
                    self.assertEqual(direct_winner(game.board),0)
                    self.assertIn(tuple(move),game.legalMoves(idx))
                    game.board[move[0]][move[1]]='X' if side else 'O'
                    self.assertEqual(game.board,board)
                    idx,side=game._destination(move),not side
                self.assertEqual(direct_winner(game.board),record['winner'])
                self.assertEqual(sum(record['nodes_per_move']),record['total_nodes'])

    def test_deeper_alpha_beta_matches_minimax(self):
        for rule in ('local','global'):
            data=json.loads((DATA/f'depth_{rule}_results.json').read_text())
            # Small late-game trees check depth semantics without rerunning the whole experiment.
            record=next(g for g in data['games'] if g['winner'])
            game=(globalTicTacToe if rule=='global' else ultimateTicTacToe)()
            game.board=[r[:] for r in record['boards'][-4]]
            idx=game._destination(record['moves'][-4])
            side=record['max_first'] == ((len(record['moves'])-3)%2==0)
            before=[r[:] for r in game.board]
            for depth in (4,5):
                game.maxDepth=depth
                mm=game.chooseMove(idx,side,True,rule=='local' and not side)
                ab=game.chooseMove(idx,side,False,rule=='local' and not side)
                self.assertEqual(mm[:2],ab[:2])
                self.assertLessEqual(ab[2],mm[2])
                self.assertEqual(game.board,before)

    def test_complete_protocol_and_human_freeze(self):
        human_hash=human_digest(DATA/'human_games.json')
        for rule in ('local','global'):
            data=json.loads((DATA/f'depth_{rule}_results.json').read_text(encoding='utf-8'))
            self.assertEqual(data['human_reference_sha256'],human_hash)
            self.assertEqual(data['human_reference_hash_basis'],'canonical-json-v1')
            self.assertFalse(data['human'])
            self.assertEqual(len(data['games']),90)
            keys=[(g['depth_x'],g['depth_o'],g['start_board'],g['max_first']) for g in data['games']]
            self.assertEqual(set(keys),{(dx,do,b,f) for dx,do in CONFIGS for b,f in OPENINGS})
            self.assertEqual(len(set(keys)),90)
            self.assertEqual(len(data['timing_reference']),5)
            for ref in data['timing_reference']:
                g=next(g for g in data['games'] if (g['depth_x'],g['depth_o'],g['start_board'],g['max_first'])==
                       (ref['depth_x'],ref['depth_o'],0,True))
                self.assertEqual(ref['trace_sha256'],hashlib.sha256(json.dumps(g['moves']).encode()).hexdigest())
                self.assertEqual(ref['total_nodes'],g['total_nodes'])
                self.assertGreater(ref['seconds'],0)

    def test_legal_replay_and_original_baselines(self):
        baseline_local=json.loads((DATA/'results.json').read_text())['designed']
        baseline_global=json.loads((DATA/'extra_results.json').read_text())['games']
        for rule,baseline in (('local',baseline_local),('global',baseline_global)):
            data=json.loads((DATA/f'depth_{rule}_results.json').read_text())
            for g in data['games']:
                self.assertFalse(g['human'])
                self.assertEqual(g['source'],'automatic_depth_control')
                game=(globalTicTacToe if rule=='global' else ultimateTicTacToe)()
                self.assertEqual(game.board,g['initial_board'])
                idx,side=g['start_board'],g['max_first']
                for field in ('boards','values','nodes_per_move','seconds_per_move'):
                    self.assertEqual(len(g[field]),len(g['moves']))
                for move,board in zip(g['moves'],g['boards']):
                    self.assertEqual(game.checkWinner(),0)
                    self.assertIn(tuple(move),game.legalMoves(idx))
                    old=[r[:] for r in game.board]
                    closed=game.localStatus() if rule=='global' else None
                    game.board[move[0]][move[1]]='X' if side else 'O'
                    self.assertEqual(game.board,board)
                    if closed:
                        for i,status in enumerate(closed):
                            if status!='_':
                                br,bc=game.globalIdx[i]
                                self.assertEqual([r[bc:bc+3] for r in old[br:br+3]],
                                                 [r[bc:bc+3] for r in board[br:br+3]])
                    idx,side=game._destination(move),not side
                actual=macro_winner(game.localStatus()) if rule=='global' else direct_winner(game.board)
                self.assertEqual(actual,g['winner'])
                self.assertTrue(actual or not game.checkMovesLeft())
                self.assertEqual(g['total_nodes'],sum(g['nodes_per_move']))
                if (g['depth_x'],g['depth_o'])==(3,3):
                    for original in baseline:
                        if (original['start_board'],original['max_first'])==(g['start_board'],g['max_first']):
                            self.assertEqual(original['moves'],g['moves'])
                            self.assertEqual(original['total_nodes'],g['total_nodes'])


if __name__=='__main__':
    unittest.main(verbosity=2)
