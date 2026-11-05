"""Deeper supplementary versions of the four prescribed predefined matchups."""
from pathlib import Path
import json
from run_depth import ultimateTicTacToe


def run():
    output=Path(__file__).with_name('depth_predefined_results.json')
    games=json.loads(output.read_text())['games'] if output.exists() else []
    settings=((True,True,True),(True,True,False),(False,False,True),(False,False,False))
    for depth in (4,5):
        for first,mm_x,mm_o in settings:
            if any((g['depth'],g['max_first'],g['minimax_x'],g['minimax_o'])==
                   (depth,first,mm_x,mm_o) for g in games):
                continue
            game=ultimateTicTacToe()
            game.maxDepth=depth
            game.playGamePredifinedAgent(first,mm_x,mm_o)
            record=dict(game.last_game,source='automatic_depth_control',minimax_x=mm_x,minimax_o=mm_o)
            games.append(record)
            output.write_bytes((json.dumps(dict(games=games),separators=(',',':'))+'\n').encode('utf-8'))
            print('predefined',depth,'MM X/O',mm_x,mm_o,'X first',first,
                  'winner',record['winner'],'nodes',record['total_nodes'],flush=True)


if __name__=='__main__':
    run()
