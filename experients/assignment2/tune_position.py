"""Tune structural features on all 18 opening conditions, keeping a full log."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'submission'))
import json
from uttt import ultimateTicTacToe

out = Path(__file__).with_name('position_tuning.json')
results = []
hard = [(0, True), (1, False), (3, True), (7, True)]
others = [(idx, first) for idx in range(9) for first in (True, False) if (idx, first) not in hard]
candidates = [(15, 0), (0, 0), (0, 100), (0, 300), (0, 600),
              (100, 40), (300, 40), (600, 40), (100, 300),
              (-40, 40), (15, -100), (300, 300), (600, 600), (40, 1000)]
for positions in candidates:
    games = []
    for idx, first in hard + others:
        game = ultimateTicTacToe()
        game.designedMobilityMode = 'safe'
        game.designedWeights = (400, 400, 800, 800, 1000)
        game.designedPositionWeights = positions
        game._play(first, idx, (False, False), True)
        games.append(dict(start=idx, first=first, winner=game.last_game['winner']))
    wins = sum(g['winner'] == -1 for g in games)
    results.append(dict(weights=(400,400,800,800,1000), positions=positions, wins=wins, games=games))
    print(positions, wins, flush=True)
    out.write_text(json.dumps(results, indent=2))
