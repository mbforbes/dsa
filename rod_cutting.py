"""Dynamic programming problem, from the Algorithms book, 15.1.

The Algorithms book is:

    Introduction to Algorithms (2009)
    Cormen, Thomas H., Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein
    3rd ed. Cambridge, MA: MIT Press

intuition for why a single recursive call works (instead of two):

    any such segment you might further divide up, e.g.,
    pulling the left 3 off of an 8

    ===/=====

    ... and then splitting further into 2/1

    ==/=/=====

    ... will also be caught if you first split off 2:

    ==/======

    ... and then further the right piece, where you might
    split off 1, and then continue

    ==/=/=====

    in other words, if the first segment is of length i, and
    we're splitting from 0 through i, any smaller split of
    the i-length segment will already have been considered
    by a previous j < i.
"""

ROD_PRICES = {
    1: 1,
    2: 5,
    3: 8,
    4: 9,
    5: 10,
    6: 17,
    7: 17,
    8: 20,
    9: 24,
    10: 30,
}


r_cache = {}
"""recursive cache"""

i_cache = {}
"""iterative cache"""


def cut_rod(n: int):
    if n == 0:
        return 0
    if n in r_cache:
        return r_cache[n]
    best = 0
    for i in range(1, n + 1):
        remainder = n - i
        # make sure we don't recursively call on n, because
        # we'd loop forever
        i_price = ROD_PRICES.get(i, 0)
        remainder_best_price = cut_rod(remainder)
        best = max(best, i_price + remainder_best_price)
        # print(
        #     f"   {i}/{remainder} best = {best} = {i_price}+{remainder_best_price}"
        # )
    r_cache[n] = best
    return best


def cut_rod_iterative(n: int):
    # build up table
    i_cache[0] = 0
    for l in range(1, n + 1):
        # print(f"l={l}")
        # inner loop with cut of len i
        best = 0
        for i in range(1, l + 1):
            remainder = l - i
            best = max(best, ROD_PRICES.get(i, 0) + i_cache[remainder])
            # print(
            #     f"   {i}/{remainder} best = {best} = {ROD_PRICES.get(i, 0)}+{cache[remainder]}"
            # )
        i_cache[l] = best
    return i_cache[n]


def main() -> None:
    for i in range(1, 20):
        print(i, "\t", cut_rod(i), cut_rod_iterative(i))
        # print(i, "\t", cut_rod(i))
        # print(i, "\t", cut_rod_iterative(i))


if __name__ == "__main__":
    main()
