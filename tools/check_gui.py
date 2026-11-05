"""GUI integration checks. All generated moves go to temporary test logs only."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import time
import tkinter as tk
import unittest
from play_gui import HumanSession, GameWindow, ultimateTicTacToe


class GuiChecks(unittest.TestCase):
    def test_complete_save_resume_and_conflict(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'test-only.json'
            session=HumanSession(path)
            session.start()
            while not session.finished:
                if session.side:
                    session.move(session.game.legalMoves(session.idx)[0])
                else:
                    session.move(*session.game.chooseMove(session.idx,False,False,True))
            session.save()
            session.save()
            records=json.loads(path.read_text())
            self.assertEqual(len(records),1)
            self.assertTrue(records[0]['human'])
            resumed=HumanSession(path)
            resumed.start()
            rng_session=HumanSession(Path(directory)/'unused-test-only.json')
            rng_session.records=records
            rng_session.start()
            self.assertEqual((resumed.idx,resumed.side),(rng_session.idx,rng_session.side))
            session.saved=False
            path.write_text('[]')
            with self.assertRaises(ValueError):
                session.save()
            self.assertEqual(json.loads(path.read_text()),[])

    def test_invalid_input_and_nonhuman_log(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'test-only.json'
            s=HumanSession(path)
            s.start()
            before=[r[:] for r in s.game.board]
            with self.assertRaises(ValueError):
                s.move((-1,0))
            self.assertEqual(before,s.game.board)
            path.write_text('[{"human":false}]')
            with self.assertRaises(ValueError):
                HumanSession(path)

    def test_window_click_agent_and_finish(self):
        with TemporaryDirectory() as directory:
            root=tk.Tk()
            root.withdraw()
            try:
                app=GameWindow(root,Path(directory)/'synthetic-ui-test-only.json')
                root.update()
                app.start()
                deadline=time.monotonic()+20
                while not app.session.saved and time.monotonic()<deadline:
                    root.update()
                    s=app.session
                    if s.side and not app.busy and not s.finished:
                        r,c=s.game.legalMoves(s.idx)[0]
                        app.click(SimpleNamespace(x=app.left+(c+.5)*app.size/9,
                                                  y=app.top+(r+.5)*app.size/9))
                    time.sleep(.01)
                self.assertTrue(app.session.saved)
                record=app.session.records[0]
                replay=ultimateTicTacToe()
                idx,side=record['start_board'],record['max_first']
                for move,board in zip(record['moves'],record['boards']):
                    self.assertIn(tuple(move),replay.legalMoves(idx))
                    replay.board[move[0]][move[1]]='X' if side else 'O'
                    self.assertEqual(replay.board,board)
                    idx,side=replay._destination(move),not side
                self.assertEqual(record['winner'],replay.checkWinner())
                self.assertEqual(str(app.next_button['state']),'normal')
            finally:
                root.destroy()


if __name__=='__main__':
    unittest.main()
