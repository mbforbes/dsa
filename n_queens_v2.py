"""this time with numpy, and finding all the solutions

finding all solutions inspired by https://leetcode.com/problems/n-queens/
"""

import numpy as np


def make_board(n: int):
    return np.zeros((n, n), dtype=bool)


# checking all queens' attack patterns is slower than checking just one.
# we can mantain the invariant that the board is valid: no queens are
# attacking each other. then, we can check whether we *could* add an
# additional queen while keeping the board valid. this lets us only check
# one (hypothetical) queen.


def can_place(board: np.ndarray, i: int, j: int):
    """board is shape n x n, zero-index i and j (0 <= i, j <= n - 1)"""
    # disable these once working if desired
    n, _n = board.shape
    assert n == _n and i >= 0 and i < n and j >= 0 and j < n
    # check col
    if sum(board[:, j]) > 0:
        return False
    # check row (could maybe disable if we never try duplicate rows)
    if sum(board[i, :]) > 0:
        return False
    # check diagonals
    # np.diag gives UL to BR diagonal
    # must convert cell i, j to diagonal k containing i, j
    k = j - i
    if sum(np.diag(board, k=k)) > 0:
        return False
    # flipping left to right reverses diagonal
    # row (i) stays the same, column gets inverted (by n-1)
    flipped_k = (n - 1 - j) - i
    if sum(np.diag(np.fliplr(board), k=flipped_k)) > 0:
        return False
    return True


def place_queens(board, q: int):
    """recursive backtracking, q is 0-based index of queen to be placed"""
    # print(f"attempting to place queen {q}")
    n = board.shape[0]
    # solution! (we've added n 0-indexed qs, so when q == n we're trying to add the
    # n+1th, so we're done)
    if q == n:
        return [board]

    # find position for qth queen
    my_solutions = []
    i = q  # early optimization: queen i is on row i
    for j in range(n):
        if can_place(board, i, j):
            # print(f"could place queen {q} at {i},{j}")
            candidate = board.copy()
            candidate[i, j] = True
            sub_solutions = place_queens(candidate, q + 1)
            if len(sub_solutions) > 0:
                my_solutions.extend(sub_solutions)
            # we always continue on with the next j, because either (a) there
            # were no solutions for this j, so we want to consider future
            # candidates to find one, or (b) there *were* solutions for this
            # j, but we want to find all solutions, so we need to keep looking
            # through all j assignments.

    # print(f"finished checking queen {q} at board {render(board)}")
    return my_solutions


def render(board: np.ndarray):
    return ["".join(["Q" if cell else "." for cell in row]) for row in board]


class Solution:
    def solveNQueens(self, n: int) -> list[list[str]]:
        board = make_board(n)
        solution_boards = place_queens(board, 0)
        return [render(solution) for solution in solution_boards]


def main() -> None:
    solution = Solution()
    result = solution.solveNQueens(5)
    print(result)


if __name__ == "__main__":
    main()
