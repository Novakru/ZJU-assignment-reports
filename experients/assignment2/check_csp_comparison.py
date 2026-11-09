"""Independent tiny-instance oracle, shared-interface checks, and experiment replay."""
from pathlib import Path
import json
import unittest
from run_csp_comparison import METHODS, NODE_LIMIT, solve, SearchLimitReached, instances, np
from Pentomino import check_correctness
from solve import solve_algorithm_x, solve_backtracking, solve_forward_checking

DATA=Path(__file__).resolve().parent


class CspComparisonChecks(unittest.TestCase):
    def test_domino_existence_against_direct_cell_oracle(self):
        def possible(cells):
            if not cells:
                return True
            r,c=min(cells)
            for other in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if other in cells and possible(cells-{(r,c),other}):
                    return True
            return False
        for mask in range(1,64):
            cells={(i//3,i%3) for i in range(6) if mask & (1<<i)}
            if len(cells)%2:
                continue
            board=np.zeros((2,3),dtype=int)
            for r,c in cells:
                board[r,c]=1
            tiles=[np.array([[i,i]]) for i in range(1,len(cells)//2+1)]
            for method in METHODS:
                answer=solve(board,tiles,method=method)
                self.assertEqual(bool(answer),possible(cells),(mask,method))
                if answer:
                    self.assertTrue(check_correctness(answer,board,tiles))

    def test_public_interfaces_limits_and_stats(self):
        board=np.ones((2,2),dtype=int)
        tiles=[np.array([[1,1]]),np.array([[2,2]])]
        for entry in (solve,solve_algorithm_x,solve_backtracking,solve_forward_checking):
            self.assertTrue(check_correctness(entry(board,tiles),board,tiles))
            self.assertEqual(solve.last_stats['search_nodes'],3)
            with self.assertRaises(SearchLimitReached):
                entry(board,tiles,node_limit=1)
            self.assertEqual(solve.last_stats['search_nodes'],1)
            self.assertEqual(solve.last_stats['status'],'node_limit')
        with self.assertRaises(ValueError):
            solve(board,tiles,method='typo')
        with self.assertRaises(ValueError):
            solve(board,tiles,node_limit=0)

    def test_all_measured_counts_and_original_mrv_baseline(self):
        data=json.loads((DATA/'csp_comparison.json').read_text())
        original=json.loads((DATA/'results.json').read_text())['csp']
        self.assertEqual(len(data['cases']),12)
        self.assertEqual(data['node_limit'],NODE_LIMIT)
        for case in data['cases']:
            board,tiles=getattr(instances,case['board']),getattr(instances,case['tiles'])
            before=board.copy()
            copies=[p.copy() for p in tiles]
            counts=[]
            self.assertEqual([m['method'] for m in case['methods']],list(METHODS))
            for saved in case['methods']:
                method=saved['method']
                try:
                    answer=solve(board,tiles,method=method,node_limit=NODE_LIMIT)
                    self.assertTrue(check_correctness(answer,board,tiles))
                    image=np.zeros(board.shape,dtype=int)
                    for p,(r,c) in answer:
                        image[r:r+p.shape[0],c:c+p.shape[1]][p!=0]=p[p!=0]
                    self.assertEqual(image.tolist(),saved['tiling'])
                    self.assertTrue(saved['valid'])
                except SearchLimitReached:
                    self.assertEqual(saved['status'],'node_limit')
                    self.assertIsNone(saved['valid'])
                    self.assertIsNone(saved['tiling'])
                for key,value in solve.last_stats.items():
                    self.assertEqual(value,saved[key])
                counts.append(saved['placements'])
                self.assertTrue(np.array_equal(before,board))
                self.assertTrue(all(np.array_equal(a,b) for a,b in zip(copies,tiles)))
            self.assertEqual(len(set(counts)),1)
            baseline=next(g for g in original if (g['board'],g['tiles'])==(case['board'],case['tiles']))
            mrv=case['methods'][-1]
            self.assertEqual(mrv['search_nodes'],baseline['stats']['search_nodes'])
            self.assertEqual(mrv['tiling'],baseline['tiling'])


if __name__=='__main__':
    unittest.main(verbosity=2)
