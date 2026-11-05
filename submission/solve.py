"""Polyomino tiling as exact cover, using bitsets and minimum-domain search."""
import numpy as np


def solve(board, pents):
    """Return [(oriented_tile, (row, column)), ...] without changing inputs.

    Nonzero board cells must be covered exactly once; every tile is used once.
    Rotations/reflections are allowed. An impossible instance returns [].
    """
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
        nodes += 1
        if not uncovered:
            return []
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

    answer = search((1 << ncols) - 1, (1 << len(rows)) - 1)
    solve.last_stats = {"placements": len(rows), "search_nodes": nodes}
    return [] if answer is None else [(rows[i][0].copy(), rows[i][1]) for i in answer]
