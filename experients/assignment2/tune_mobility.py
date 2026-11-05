"""Compare raw safety, unsafe-choice count, and normalized safety."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'submission'))
import json
from uttt import ultimateTicTacToe

out = Path(__file__).with_name('mobility_tuning.json')
results=[]
for mode, scale in [('unsafe',300),('unsafe',1000),('ratio',1000),('ratio',3000),
                     ('unsafe',100),('unsafe',600),('ratio',6000),('ratio',300)]:
    games=[]
    for idx in range(9):
        for first in (True,False):
            g=ultimateTicTacToe()
            g.designedWeights=(400,400,800,800,scale)
            g.designedMobilityMode=mode
            g._play(first,idx,(False,False),True)
            games.append(dict(start=idx,first=first,winner=g.last_game['winner']))
    wins=sum(g['winner']==-1 for g in games)
    results.append(dict(mode=mode,weights=(400,400,800,800,scale),wins=wins,games=games))
    print(mode,scale,wins,flush=True)
    out.write_text(json.dumps(results,indent=2))
