"""Develop board-spread and open-line features; keep all outcomes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'submission'))
import json
from uttt import ultimateTicTacToe

out = Path(__file__).with_name('structure_tuning.json')
results = []
candidates = [(100,0),(300,0),(600,0),(1000,0),(-300,0),
              (0,30),(0,100),(0,300),(300,30),(600,100),(-300,100),(1000,100)]
for structure in candidates:
    games = []
    for idx in range(9):
        for first in (True, False):
            game = ultimateTicTacToe()
            game.designedMobilityMode = 'safe'
            game.designedWeights = (400,400,800,800,1000)
            game.designedStructureWeights = structure
            game._play(first, idx, (False, False), True)
            games.append(dict(start=idx, first=first, winner=game.last_game['winner']))
    wins = sum(g['winner']==-1 for g in games)
    results.append(dict(weights=(400,400,800,800,1000), structure=structure, wins=wins, games=games))
    print(structure,wins,flush=True)
    out.write_text(json.dumps(results,indent=2))
