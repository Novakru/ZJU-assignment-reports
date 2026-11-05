"""Development sweep, separate from the final reproducibility run."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'submission'))
import json
from uttt import ultimateTicTacToe

candidates = [(160,160,600,600,35), (160,160,600,600,300),
              (160,160,600,600,800), (400,600,800,1200,300),
              (100,600,300,1200,300), (600,100,1200,300,300),
              (100,400,300,800,800), (400,400,800,800,1000),
              (500,500,1000,1000,0), (100,800,300,1600,100),
              (400,400,800,800,600), (400,400,800,800,1500),
              (400,400,800,800,2000), (200,200,800,800,1000),
              (600,600,800,800,1000), (400,400,0,0,1000),
              (400,400,1600,1600,1000), (300,500,800,800,1000),
              (500,300,800,800,1000), (160,160,600,600,150),
              (160,160,600,600,450), (160,160,600,600,600)]
out = Path(__file__).with_name('tuning.json')
results = []
for weights in candidates:
    games = []
    for idx in range(9):
        for first in (True, False):
            game = ultimateTicTacToe()
            game.designedMobilityMode = 'safe'
            game.designedWeights = weights
            game._play(first, idx, (False, False), True)
            games.append(dict(start=idx, first=first, winner=game.last_game['winner']))
    wins = sum(g['winner'] == -1 for g in games)
    results.append(dict(weights=weights, wins=wins, games=games))
    print(weights, wins, flush=True)
    Path(__file__).with_name('tuning.json').write_text(json.dumps(results, indent=2))
