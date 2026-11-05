"""First-local-board-wins Ultimate Tic-Tac-Toe. Standard library only.

Run python uttt.py human --games 10 to collect real human experiment records.
Run python uttt.py extra --games 12 for the global-board extension.
Search depth includes the root move. Equal scores retain raster-order moves.
"""
from math import inf
from random import Random
from functools import lru_cache
import argparse
import json
from pathlib import Path

LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
         (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


@lru_cache(maxsize=19683)
def _features(cells):
    """winner, X/O threats, X/O blocks, X/O corners, winning squares."""
    winner = tx = to = bx = bo = 0
    wx, wo = set(), set()
    for line in LINES:
        values = [cells[i] for i in line]
        x, o = values.count('X'), values.count('O')
        if x == 3:
            winner = 1
        if o == 3:
            winner = -1
        if x == 2 and o == 0:
            tx += 1
            wx.update(i for i in line if cells[i] == '_')
        if o == 2 and x == 0:
            to += 1
            wo.update(i for i in line if cells[i] == '_')
        bx += o == 2 and x == 1
        bo += x == 2 and o == 1
    cx = sum(cells[i] == 'X' for i in (0, 2, 6, 8))
    co = sum(cells[i] == 'O' for i in (0, 2, 6, 8))
    return winner, tx, to, bx, bo, cx, co, tuple(sorted(wx)), tuple(sorted(wo))


class ultimateTicTacToe:
    def __init__(self):
        self.board = [['_'] * 9 for _ in range(9)]
        self.maxPlayer, self.minPlayer = 'X', 'O'
        self.maxDepth = 3
        self.globalIdx = [(r, c) for r in (0, 3, 6) for c in (0, 3, 6)]
        self.startBoardIdx = 4
        self.winnerMaxUtility = 10000
        self.twoInARowMaxUtility = 500
        self.preventThreeInARowMaxUtility = 100
        self.cornerMaxUtility = 30
        self.winnerMinUtility = -10000
        self.twoInARowMinUtility = -100
        self.preventThreeInARowMinUtility = -500
        self.cornerMinUtility = -30
        self.expandedNodes = 0
        self.currPlayer = True
        self._root_is_max = None
        self._designed = False
        self._next_board = 4
        self._next_player = True
        self.last_game = {}
        self.designedWeights = (400, 400, 800, 800, 6000)
        self.designedPositionWeights = (15, 40)
        self.designedStructureWeights = (0, 0)
        self.designedMobilityMode = 'ratio'

    def _local(self, idx):
        r, c = self.globalIdx[idx]
        return tuple(self.board[r + dr][c + dc] for dr in range(3) for dc in range(3))

    def printGameBoard(self):
        for r, row in enumerate(self.board):
            print(' | '.join(' '.join(row[c:c + 3]) for c in (0, 3, 6)))
            if r in (2, 5):
                print('------+-------+------')

    def evaluatePredifined(self, isMax):
        """Use the root agent's three-tier heuristic on the global board."""
        winner = self.checkWinner()
        if winner:
            return winner * 10000
        f = [_features(self._local(i)) for i in range(9)]
        if isMax:
            tier2 = sum(x[1] * self.twoInARowMaxUtility +
                        x[3] * self.preventThreeInARowMaxUtility for x in f)
            return tier2 if tier2 else sum(x[5] * self.cornerMaxUtility for x in f)
        tier2 = sum(x[2] * self.twoInARowMinUtility +
                    x[4] * self.preventThreeInARowMinUtility for x in f)
        return tier2 if tier2 else sum(x[6] * self.cornerMinUtility for x in f)

    def evaluateDesigned(self, isMax):
        """Routing-aware zero-sum heuristic, always expressed in X utility.

        isMax is retained for skeleton compatibility. Both sides' threats are
        considered; the designed agent plays O in the experiments.
        """
        winner = self.checkWinner()
        if winner:
            return winner * 10000
        locals_ = [self._local(i) for i in range(9)]
        feats = [_features(c) for c in locals_]
        moves = self.legalMoves(self._next_board)
        if not moves:
            return 0
        side = self._next_player
        symbol = 'X' if side else 'O'
        sign = 1 if side else -1
        # An immediate win on the board actually being played dominates
        # irrelevant threats elsewhere. Count safe destinations as well.
        safe = 0
        for r, c in moves:
            local_idx = (r // 3) * 3 + c // 3
            pos = (r % 3) * 3 + c % 3
            if pos in feats[local_idx][7 if side else 8]:
                return sign * 9500
            target = pos
            target_cells = list(locals_[target])
            if target == local_idx:
                target_cells[pos] = symbol
            target_f = _features(tuple(target_cells))
            if '_' not in target_cells:
                # A full destination grants a free move on the global board.
                dangerous = any(f[8 if side else 7] for f in feats)
            else:
                dangerous = bool(target_f[8 if side else 7])
            safe += not dangerous
        if safe == 0:
            return -sign * 9000
        tx, to, fx, fo, mobility = self.designedWeights
        corner, center = self.designedPositionWeights
        score = sum(tx * f[1] - to * f[2] + 35 * (len(f[7]) - len(f[8])) +
                    corner * (f[5] - f[6]) for f in feats)
        # Distinct immediate winning cells reward forks rather than double
        # counting two lines that share the same blocking square.
        score += sum(fx * (len(f[7]) >= 2) - fo * (len(f[8]) >= 2) for f in feats)
        score += center * sum((c[4] == 'X') - (c[4] == 'O') for c in locals_)
        spread, singles = self.designedStructureWeights
        score += spread * sum(bool(f[7]) - bool(f[8]) for f in feats)
        if singles:
            for cells in locals_:
                for line in LINES:
                    values = [cells[i] for i in line]
                    score += singles * ((values.count('X') == 1 and 'O' not in values) -
                                        (values.count('O') == 1 and 'X' not in values))
        mobility_feature = safe
        if self.designedMobilityMode == 'unsafe':
            mobility_feature = safe - len(moves)
        elif self.designedMobilityMode == 'ratio':
            mobility_feature = safe / len(moves)
        score += sign * mobility * mobility_feature
        return max(-8000, min(8000, score))

    def checkMovesLeft(self):
        return any('_' in row for row in self.board)

    def checkWinner(self):
        for i in range(9):
            winner = _features(self._local(i))[0]
            if winner:
                return winner
        return 0

    def legalMoves(self, currBoardIdx):
        """A full forced board releases the player to any empty global cell."""
        if currBoardIdx is not None and 0 <= currBoardIdx < 9:
            r, c = self.globalIdx[currBoardIdx]
            moves = [(r + dr, c + dc) for dr in range(3) for dc in range(3)
                     if self.board[r + dr][c + dc] == '_']
            if moves:
                return moves
        return [(r, c) for r in range(9) for c in range(9) if self.board[r][c] == '_']

    @staticmethod
    def _destination(move):
        return (move[0] % 3) * 3 + move[1] % 3

    def _search(self, depth, idx, alpha, beta, isMax, pruning):
        # Count all visited search states, including root and evaluated leaves.
        self.expandedNodes += 1
        winner = self.checkWinner()
        if winner:
            return winner * 10000
        if not self.checkMovesLeft():
            return 0
        if depth >= self.maxDepth:
            self._next_board, self._next_player = idx, isMax
            return (self.evaluateDesigned(self._root_is_max) if self._designed else
                    self.evaluatePredifined(self._root_is_max))
        best = -inf if isMax else inf
        for r, c in self.legalMoves(idx):
            self.board[r][c] = 'X' if isMax else 'O'
            try:
                value = self._search(depth + 1, self._destination((r, c)),
                                     alpha, beta, not isMax, pruning)
            finally:
                self.board[r][c] = '_'
            if isMax:
                best = max(best, value)
                alpha = max(alpha, best)
            else:
                best = min(best, value)
                beta = min(beta, best)
            if pruning and alpha >= beta:
                break
        return best

    def _public_search(self, depth, idx, alpha, beta, isMax, pruning):
        old = self._root_is_max
        if old is None:
            self._root_is_max = isMax
        try:
            return self._search(depth, idx, alpha, beta, isMax, pruning)
        finally:
            self._root_is_max = old

    def alphabeta(self, depth, currBoardIdx, alpha, beta, isMax):
        return self._public_search(depth, currBoardIdx, alpha, beta, isMax, True)

    def minimax(self, depth, currBoardIdx, isMax):
        return self._public_search(depth, currBoardIdx, -inf, inf, isMax, False)

    def chooseMove(self, idx, isMax, use_minimax=False, designed=False):
        if self.checkWinner() or not self.checkMovesLeft():
            return None, self.checkWinner() * 10000, 0
        self.expandedNodes = 1  # root
        self._root_is_max, self._designed = isMax, designed
        best, move, alpha, beta = (-inf if isMax else inf), None, -inf, inf
        try:
            for r, c in self.legalMoves(idx):
                self.board[r][c] = 'X' if isMax else 'O'
                try:
                    value = self._search(1, self._destination((r, c)), alpha, beta,
                                         not isMax, not use_minimax)
                finally:
                    self.board[r][c] = '_'
                if move is None or (value > best if isMax else value < best):
                    best, move = value, (r, c)
                if not use_minimax:
                    if isMax:
                        alpha = max(alpha, best)
                    else:
                        beta = min(beta, best)
        finally:
            self._root_is_max, self._designed = None, False
        return move, best, self.expandedNodes

    def _play(self, first, start, algorithms, designed_o=False, human=False):
        boards, moves, counts, values = [], [], [], []
        idx, side = start, first
        initial = [row[:] for row in self.board]
        while not self.checkWinner() and self.checkMovesLeft():
            if human and side:
                self.printGameBoard()
                print('Human X. Forced board:', idx, '; legal moves:', self.legalMoves(idx))
                while True:
                    try:
                        move = tuple(map(int, input('Enter row column (0-8): ').split()))
                        if move in self.legalMoves(idx):
                            break
                    except ValueError:
                        pass
                    print('Invalid move; try again.')
                value, count = None, 0
            else:
                move, value, count = self.chooseMove(idx, side, algorithms[0 if side else 1],
                                                     designed_o and not side)
            r, c = move
            self.board[r][c] = 'X' if side else 'O'
            moves.append(move)
            values.append(value)
            counts.append(count)
            boards.append([row[:] for row in self.board])
            idx, side = self._destination(move), not side
        winner = self.checkWinner()
        self.last_game = dict(start_board=start, max_first=first, moves=moves,
                              nodes_per_move=counts, values=values, boards=boards,
                              initial_board=initial, winner=winner, depth=self.maxDepth,
                              total_nodes=sum(counts), human=human)
        return boards, moves, counts, values, winner

    def playGamePredifinedAgent(self, maxFirst, isMinimaxOffensive, isMinimaxDefensive):
        return self._play(maxFirst, self.startBoardIdx,
                          (isMinimaxOffensive, isMinimaxDefensive))

    def playGameYourAgent(self):
        rng = Random()
        result = self._play(bool(rng.getrandbits(1)), rng.randrange(9), (False, False), True)
        return result[0], result[1], result[4]

    def playGameHuman(self):
        result = self._play(self.currPlayer, self.startBoardIdx, (False, False), True, True)
        return result[0], result[1], result[4]


@lru_cache(maxsize=65536)
def _line_potential(cells):
    """Open one/two-in-a-row lines, with D representing a closed draw."""
    one_x = one_o = two_x = two_o = 0
    win_x, win_o = set(), set()
    winner = 0
    for line in LINES:
        values = [cells[i] for i in line]
        if 'D' in values:
            continue
        x, o = values.count('X'), values.count('O')
        if x == 3:
            winner = 1
        if o == 3:
            winner = -1
        if not o:
            one_x += x == 1
            two_x += x == 2
            if x == 2:
                win_x.update(i for i in line if cells[i] == '_')
        if not x:
            one_o += o == 1
            two_o += o == 2
            if o == 2:
                win_o.update(i for i in line if cells[i] == '_')
    return winner, one_x, one_o, two_x, two_o, tuple(win_x), tuple(win_o)


class globalTicTacToe(ultimateTicTacToe):
    """Extra-credit rules: win three local boards in a global line.

    A won or drawn local board is closed. Routing to a closed board grants
    free choice among all open local boards. Both custom agents use the
    inherited depth-three alpha-beta search, with root-specific heuristics.
    """
    def localStatus(self):
        status = []
        for idx in range(9):
            cells = self._local(idx)
            winner = _features(cells)[0]
            status.append('X' if winner == 1 else 'O' if winner == -1 else
                          '_' if '_' in cells else 'D')
        return tuple(status)

    def checkWinner(self):
        return _line_potential(self.localStatus())[0]

    def checkMovesLeft(self):
        return '_' in self.localStatus()

    def legalMoves(self, currBoardIdx):
        status = self.localStatus()
        if _line_potential(status)[0]:
            return []
        if currBoardIdx is not None and 0 <= currBoardIdx < 9 and status[currBoardIdx] == '_':
            r, c = self.globalIdx[currBoardIdx]
            return [(r+dr, c+dc) for dr in range(3) for dc in range(3)
                    if self.board[r+dr][c+dc] == '_']
        return [(r, c) for r in range(9) for c in range(9)
                if status[(r//3)*3+c//3] == '_' and self.board[r][c] == '_']

    def evaluatePredifined(self, isMax):
        """Own offensive (X root) / defensive (O root) global heuristics."""
        status = self.localStatus()
        macro = _line_potential(status)
        if macro[0]:
            return macro[0] * 10000
        if '_' not in status:
            return 0
        local = [_features(self._local(i)) for i in range(9)]
        if self._next_board is not None and status[self._next_board] == '_':
            active = [self._next_board]
        else:
            active = [i for i in range(9) if status[i] == '_']
        side = self._next_player
        sign = 1 if side else -1
        # A local capture is a global immediate win only on a required board.
        needed = macro[5 if side else 6]
        if any(i in needed and local[i][7 if side else 8] for i in active):
            return sign * 9500
        cap_x, threat_x, local_x = (500, 1600, 45) if isMax else (550, 1800, 55)
        score = cap_x * status.count('X') - 450 * status.count('O')
        score += threat_x * macro[3] - 1400 * macro[4]
        score += 150 * macro[1] - 120 * macro[2]
        positions = (2, 1, 2, 1, 3, 1, 2, 1, 2)
        score += 25 * sum(w * ((s == 'X') - (s == 'O')) for w, s in zip(positions, status))
        for i, state in enumerate(status):
            if state == '_':
                score += local_x * local[i][1] - 35 * local[i][2]
                single = _line_potential(self._local(i))
                score += 4 * (single[1] - single[2])
        score += 80 * sum(local[i][1] - local[i][2] for i in active)
        if any(local[i][7 if side else 8] for i in active):
            score += 200 * sign
        return max(-8000, min(8000, score))

    def evaluateDesigned(self, isMax):
        return self.evaluatePredifined(isMax)

    def playGameGlobal(self, maxFirst=True, startBoardIdx=4):
        result = self._play(maxFirst, startBoardIdx, (False, False))
        self.last_game.update(rule='global', local_status=self.localStatus(),
                              agent_x='custom_offensive', agent_o='custom_defensive')
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('demo', 'human', 'extra'), nargs='?', default='demo')
    parser.add_argument('--games', type=int, default=10)
    parser.add_argument('--output', default=None)
    parser.add_argument('--seed', type=int, default=448)
    args = parser.parse_args()
    if args.output is None:
        args.output = 'extra_games.json' if args.mode == 'extra' else 'human_games.json'
    if args.mode == 'extra':
        rng = Random(args.seed)
        records = []
        for i in range(args.games):
            game = globalTicTacToe()
            idx, first = rng.randrange(9), bool(rng.getrandbits(1))
            game.playGameGlobal(first, idx)
            records.append(game.last_game)
            print('Global game', i+1, 'winner', game.last_game['winner'],
                  'nodes', game.last_game['total_nodes'], flush=True)
            Path(args.output).write_text(json.dumps(records, indent=2), encoding='utf-8')
        return
    if args.mode == 'demo':
        game = ultimateTicTacToe()
        game.playGamePredifinedAgent(True, False, False)
        game.printGameBoard()
        print('Winner:', game.last_game['winner'], 'Nodes:', game.last_game['total_nodes'])
        return
    output = Path(args.output)
    records = json.loads(output.read_text(encoding='utf-8')) if output.exists() else []
    rng = Random(args.seed)
    for _ in range(len(records)):
        rng.randrange(9)
        rng.getrandbits(1)
    while len(records) < args.games:
        game = ultimateTicTacToe()
        game.startBoardIdx, game.currPlayer = rng.randrange(9), bool(rng.getrandbits(1))
        print('Game', len(records) + 1, '/', args.games)
        try:
            game.playGameHuman()
        except (EOFError, KeyboardInterrupt):
            print('\nStopped; completed games remain saved in', output)
            break
        game.printGameBoard()
        print('Winner:', {1: 'Human X', -1: 'Agent O', 0: 'Draw'}[game.last_game['winner']])
        records.append(game.last_game)
        output.write_text(json.dumps(records, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
