"""backtracking, trying the N queens problem. more:
- https://en.wikipedia.org/wiki/Backtracking
- https://en.wikipedia.org/wiki/Eight_queens_puzzle

takeaways from backtracking:

1.  I always called the technique  "recursive backtracking", but most just
    call it "backtracking" because recursion is so commonly used. (could do
    iter + stack if wanted.)

2. backtracking feels morally similar to brute force. (still seems exponential
   or super-exponential.) though cutting off whole search subtrees is
   undoubtedly good. (e.g., if can't place 6th queen from these 5, no need to
   also try placing 7th and 8th)

3. even simple heuristics dramatically reduce search space. for example,
   knowing there's 1 queen per row, so searching row-by-row, enormously
   reduces the search space.

some things i learned with display: - clearing screen is really easy - seeing
the attempts is really fun - doing so makes attempts 2-3 ORDERS OF MAGNITUDE
slower
    - e.g., 300 vs 270,000 attempts per second
- as always, measure before optimizing is good
    - (this i/o bound was sufficient to remove for what i wanted to try)

better implementations would probably use bitmaps and vector ops to check
row/col/diag collisions, rather than iterating like I do here

one surprising thing is that stupider searching (trying each queen placement
from [0][0] through [n][n]) checks 4x attempts/second vs smarter search
(automatically assigning queen i to row i, and only searching [i][0] through
[i][n])
"""

import os
import time
from typing import Optional

attempt = 0

last_reported = time.time()
attempts_since_last_report = 0
report_interval_s = 1


def render(board_size: int, queens: set[tuple[int, int]]):
    global attempt
    attempt += 1
    for row in range(board_size):
        buf = []
        for col in range(board_size):
            if (row, col) in queens:
                buf.append("[Q]")
            else:
                buf.append("[ ]")
        print("".join(buf))
    print(f"{len(queens)} queens (attempt {attempt})")


def render_lite(board_size: int, queens: set[tuple[int, int]]):
    global attempt, last_reported, attempts_since_last_report
    attempt += 1
    attempts_since_last_report += 1
    now = time.time()
    delta = now - last_reported
    if delta > report_interval_s:
        last_reported = now
        clear()
        aps = int(attempts_since_last_report / delta)
        attempts_since_last_report = 0
        print(
            f"attempt {attempt} (@{len(queens)}/{board_size} queens) ({aps} attempts/s)"
        )


def clear():
    os.system("cls" if os.name == "nt" else "clear")
    # print()
    pass


def tick():
    # time.sleep(0.01)
    pass


def collides(board_size: int, queens: set[tuple[int, int]]):
    for queen in queens:
        in_row = len([q for q in queens if q[0] == queen[0]])
        if in_row > 1:
            # print(f"{queen} collides row {queen[0]}")
            return True
        in_col = len([q for q in queens if q[1] == queen[1]])
        if in_col > 1:
            # print(f"{queen} collides col {queen[1]}")
            return True
        # 2 diagonal checks.
        # (1) UL --> BR
        r, c = queen
        n_ulbr = 0
        while r >= 0 and c >= 0:
            if (r, c) in queens:
                n_ulbr += 1
            r -= 1
            c -= 1
        r, c = queen[0] + 1, queen[1] + 1
        while r < board_size and c < board_size:
            if (r, c) in queens:
                n_ulbr += 1
            r += 1
            c += 1
        if n_ulbr > 1:
            # print(f"{queen} collides UL -> BR")
            return True
        # (1) BL --> UR
        # - to BL: rows increase, columns decrease
        r, c = queen
        n_blur = 0
        while r < board_size and c >= 0:
            if (r, c) in queens:
                n_blur += 1
            r += 1
            c -= 1
        # - to UR: rows decrease, columns increase
        r, c = queen[0] - 1, queen[1] + 1
        while r >= 0 and c < board_size:
            if (r, c) in queens:
                # print(f"({r}, {c}) in queens")
                n_blur += 1
            r -= 1
            c += 1
        if n_blur > 1:
            # print(f"{queen} collides BL -> UR")
            return True
    return False


def test_collides():
    assert collides(8, set([(0, 0), (0, 1)]))
    assert collides(8, set([(0, 0), (1, 0)]))
    assert collides(8, set([(0, 0), (1, 1)]))

    assert collides(8, set([(7, 7), (7, 0)]))
    assert collides(8, set([(7, 7), (7, 6)]))
    assert collides(8, set([(7, 7), (0, 7)]))
    assert collides(8, set([(7, 7), (6, 7)]))
    assert collides(8, set([(7, 7), (0, 0)]))

    assert collides(8, set([(3, 3), (2, 2)]))
    assert collides(8, set([(3, 3), (4, 4)]))
    assert collides(8, set([(3, 3), (4, 2)]))
    assert collides(8, set([(3, 3), (2, 4)]))

    assert not collides(8, set([(0, 0), (1, 2)]))
    assert not collides(8, set([(0, 0), (2, 1)]))
    assert not collides(8, set([(0, 0), (2, 3)]))


def place_queen_naive(
    board_size: int, queens: set[tuple[int, int]]
) -> Optional[set[tuple[int, int]]]:
    """with rendering, this checked like ~300 attempts per second, which is hilariously
    low"""
    # print(f"place_queen(board_size={board_size}, queens={len(queens)})")
    # base case: we're done when we've placed board_size queens
    if len(queens) == board_size:
        return queens
    # brute force w/ .... backtracking?
    for r in range(board_size):
        for c in range(board_size):
            if (r, c) in queens:
                continue
            attempt = queens | {(r, c)}

            # ~300 aps
            # tick()
            # clear()
            # render(board_size, attempt)

            # ~270,000 aps
            render_lite(board_size, attempt)

            if not collides(board_size, attempt):
                # attempt is viable, so proceed
                continuation = place_queen_naive(board_size, attempt)
                if continuation is not None:
                    return continuation  # full solution
                # otherwise, we just continue (loops to next C)
    return None


def place_queen_byrow(
    board_size: int, queens: set[tuple[int, int]]
) -> Optional[set[tuple[int, int]]]:
    """with rendering, this checked like ~300 attempts per second, which is hilariously
    low"""
    # print(f"place_queen(board_size={board_size}, queens={len(queens)})")
    # base case: we're done when we've placed board_size queens
    if len(queens) == board_size:
        return queens
    # by row, still brute force w/ .... backtracking?
    r = len(queens)  # 1 queen / row (else trivial collision)
    for c in range(board_size):
        if (r, c) in queens:
            continue
        attempt = queens | {(r, c)}

        # ~300 aps
        # tick()
        # clear()
        # render(board_size, attempt)

        # ~70,000 aps
        render_lite(board_size, attempt)

        if not collides(board_size, attempt):
            # attempt is viable, so proceed
            continuation = place_queen_byrow(board_size, attempt)
            if continuation is not None:
                return continuation  # full solution
            # otherwise, we just continue (loops to next C)
    return None


def main() -> None:
    test_collides()

    # placements = place_queen_naive(8, set())  # solution @ 1,502,346
    # placements = place_queen_byrow(8, set())  # few seconds, solution @ 876
    placements = place_queen_byrow(20, set())  # ~1min, solution @ 3,992,511
    if placements is not None:
        render(len(placements), placements)
    print(f"Complete, result was: {placements}")

    # board_size = 8
    # clear()
    # render(board_size, set([(1, 2), (7, 7)]))
    # tick()
    # clear()
    # render(board_size, set([(0, 0), (0, 7)]))


if __name__ == "__main__":
    main()
