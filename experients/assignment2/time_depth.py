"""Sequential wall-time reference, run after both full depth experiments finish."""
from pathlib import Path
import hashlib
import json
from run_depth import CONFIGS, play


def run():
    for rule in ('local','global'):
        path=Path(__file__).with_name(f'depth_{rule}_results.json')
        data=json.loads(path.read_text(encoding='utf-8'))
        if len(data['games']) != 90:
            raise ValueError('Complete all 90 games before taking sequential timings.')
        refs=[]
        for dx,do in CONFIGS:
            record=play(rule,dx,do,0,True)
            original=next(g for g in data['games'] if
                          (g['depth_x'],g['depth_o'],g['start_board'],g['max_first'])==(dx,do,0,True))
            trace=json.loads(json.dumps(record['moves']))
            assert trace==original['moves'] and record['total_nodes']==original['total_nodes']
            refs.append(dict(depth_x=dx,depth_o=do,start_board=0,max_first=True,
                             seconds=record['seconds'],total_nodes=record['total_nodes'],
                             winner=record['winner'],plies=len(trace),
                             trace_sha256=hashlib.sha256(json.dumps(trace).encode()).hexdigest()))
            print('Sequential timing',rule,dx,do,round(record['seconds'],3),flush=True)
        data['timing_reference']=refs
        temp=path.with_suffix('.json.tmp')
        temp.write_bytes((json.dumps(data,separators=(',',':'))+'\n').encode('utf-8'))
        temp.replace(path)


if __name__=='__main__':
    run()
