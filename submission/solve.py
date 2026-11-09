"""Polyomino tiling as exact cover, using bitsets and minimum-domain search."""
import numpy as np


def solve(board, pents, *, method='algorithm_x', node_limit=None):
    """Return [(oriented_tile, (row, column)), ...] without changing inputs.

    Nonzero board cells must be covered exactly once; every tile is used once.
    Rotations/reflections are allowed. An impossible instance returns [].
    method: algorithm_x (MRV), backtracking (first empty cell), or
    forward_checking (first empty cell plus zero-domain checks).
    Optional node_limit raises SearchLimitReached; it never reports no solution.
    last_stats counts recursive states, including root and successful leaf.
    """
    if method not in ('algorithm_x', 'backtracking', 'forward_checking'):
        raise ValueError('unknown search method: ' + str(method))
    if node_limit is not None and (not isinstance(node_limit, int) or node_limit < 1):
        raise ValueError('node_limit must be a positive integer or None')
    solve.last_stats = dict(method=method, placements=0, search_nodes=0, status='invalid')
    board = np.asarray(board)
    if board.ndim != 2:
        raise ValueError("board must be two dimensional")
    cells = {tuple(rc): i for i, rc in enumerate(np.argwhere(board != 0))}
    if sum(np.count_nonzero(p) for p in pents) != len(cells):
        return []
    ncols = len(cells) + len(pents)
    columns = [0] * ncols
    rows, masks = [], []
    for tile_idx, tile in enumerate(pents):
        tile = np.asarray(tile)
        if tile.ndim != 2 or not np.any(tile):
            return []
        seen = set()
        for reflected in (tile, np.flip(tile, 0)):
            for rotation in range(4):
                p = np.rot90(reflected, rotation).copy()
                key = (p.shape, p.tobytes())
                if key in seen:
                    continue
                seen.add(key)
                offsets = [tuple(rc) for rc in np.argwhere(p != 0)]
                for r in range(board.shape[0] - p.shape[0] + 1):
                    for c in range(board.shape[1] - p.shape[1] + 1):
                        covered = [cells.get((r + dr, c + dc)) for dr, dc in offsets]
                        if None in covered:
                            continue
                        covered.append(len(cells) + tile_idx)
                        mask = sum(1 << i for i in covered)
                        row_id = len(rows)
                        rows.append((p, (r, c)))
                        masks.append(mask)
                        for i in covered:
                            columns[i] |= 1 << row_id
    # A row conflicts with every row sharing any cell or tile identity.
    conflicts = []
    for mask in masks:
        conflict = 0
        while mask:
            bit = mask & -mask
            conflict |= columns[bit.bit_length() - 1]
            mask ^= bit
        conflicts.append(conflict)
    nodes = 0

    def search(uncovered, available):
        nonlocal nodes
        if node_limit is not None and nodes >= node_limit:
            raise SearchLimitReached(node_limit)
        nodes += 1
        if not uncovered:
            return []
        if method == 'algorithm_x':
            remaining, best, size = uncovered, 0, len(rows) + 1
            while remaining:
                bit = remaining & -remaining
                options = columns[bit.bit_length() - 1] & available
                count = options.bit_count()
                if count < size:
                    best, size = options, count
                    if count <= 1:
                        break
                remaining ^= bit
        else:
            # Cell bits precede tile bits, so the first bit is the first empty
            # board cell whenever cells remain. No dynamic variable ordering.
            bit = uncovered & -uncovered
            best = columns[bit.bit_length() - 1] & available
            size = best.bit_count()
            if method == 'forward_checking':
                remaining = uncovered
                while remaining:
                    bit = remaining & -remaining
                    if not columns[bit.bit_length() - 1] & available:
                        return None
                    remaining ^= bit
        if size == 0:
            return None
        while best:
            bit = best & -best
            row_id = bit.bit_length() - 1
            answer = search(uncovered & ~masks[row_id], available & ~conflicts[row_id])
            if answer is not None:
                return [row_id] + answer
            best ^= bit
        return None

    try:
        answer = search((1 << ncols) - 1, (1 << len(rows)) - 1)
    except SearchLimitReached:
        solve.last_stats = dict(method=method, placements=len(rows), search_nodes=nodes, status='node_limit')
        raise
    solve.last_stats = dict(method=method, placements=len(rows), search_nodes=nodes,
                           status='solved' if answer is not None else 'unsatisfiable')
    return [] if answer is None else [(rows[i][0].copy(), rows[i][1]) for i in answer]


class SearchLimitReached(RuntimeError):
    """A resource cap was reached; this is not an unsatisfiability result."""


def solve_backtracking(board, pents, *, node_limit=None):
    """Traditional first-empty-cell DFS with overlap and tile-use checks."""
    return solve(board, pents, method='backtracking', node_limit=node_limit)


def solve_forward_checking(board, pents, *, node_limit=None):
    """First-empty-cell DFS with an additional zero-domain feasibility check."""
    return solve(board, pents, method='forward_checking', node_limit=node_limit)


def solve_algorithm_x(board, pents, *, node_limit=None):
    """Algorithm X with minimum remaining values; also the default solve()."""
    return solve(board, pents, method='algorithm_x', node_limit=node_limit)
