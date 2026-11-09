"""Compare search states with identical placements and candidate order; no timings."""
from pathlib import Path
import json
import sys
import numpy as np

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'submission'))
from solve import solve, SearchLimitReached
import instances
from Pentomino import check_correctness

METHODS=('backtracking','forward_checking','algorithm_x')
NODE_LIMIT=1_000_000


def run():
    output=Path(__file__).with_name('csp_comparison.json')
    data=dict(node_limit=NODE_LIMIT,methods=METHODS,
              counting='recursive states including root, dead ends, and successful leaf; preprocessing excluded',
              cases=[])
    for board_name in ('board_6x10','board_5x12','board_3x20','empty_chessboard'):
        for tile_name in ('dominos','triominos','pentnominos'):
            board,tiles=getattr(instances,board_name),getattr(instances,tile_name)
            case=dict(board=board_name,tiles=tile_name,methods=[])
            for method in METHODS:
                board_copy=board.copy()
                tile_copies=[p.copy() for p in tiles]
                try:
                    solution=solve(board,tiles,method=method,node_limit=NODE_LIMIT)
                    assert check_correctness(solution,board,tiles),(board_name,tile_name,method)
                    image=np.zeros(board.shape,dtype=int)
                    for p,(r,c) in solution:
                        image[r:r+p.shape[0],c:c+p.shape[1]][p!=0]=p[p!=0]
                    record=dict(solve.last_stats,valid=True,tiling=image.tolist())
                except SearchLimitReached:
                    record=dict(solve.last_stats,valid=None,tiling=None)
                assert np.array_equal(board,board_copy)
                assert all(np.array_equal(a,b) for a,b in zip(tiles,tile_copies))
                case['methods'].append(record)
                print(board_name,tile_name,method,record['status'],record['search_nodes'],flush=True)
            data['cases'].append(case)
            output.write_bytes((json.dumps(data,indent=2)+'\n').encode('utf-8'))


if __name__=='__main__':
    run()
