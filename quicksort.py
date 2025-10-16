"""Quicksort:
- choose pivot element
- partition into < and > the pivot
- put pivot right at that boundary
- quicksort each partition

Key properties:
- worst case: O(n^2)
- average case: O(n log n)
- in-place
- space: O(log n) b/c you gotta have a O(log n) call stack
    - wikipedia says you gotta use "Sedgewick's trick" to sort the larger
      partition using tail recursion or iteration, else you might use O(n)
      recursive calls. hmm.

Quicksort's degenerate case is on an already sorted array:
- say we choose the pivot to be the last element
- the "< pivot" boundary moves from 0 to the last element (O(n))
- then, the left partition has n-1 elements, and the right partition is empty
- we quicksort the left partition, which happens O(n) times recursively
"""

import random


def quicksort(x: list[int], start: int = 0, end: int = -1) -> None:
    """in-place quicksorts x from start through end, both inclusive."""
    if end == -1:
        end = len(x) - 1

    # base case: any sequence of 0 or 1 (or negative, lol) elements is sorted
    if start >= end:
        return

    # conceptual notes:
    # - boundary is inclusive
    # - i >= boundary, i.e., we'll iterate at least as fast as the boundary grows
    # - we compare up to pivot (exclusive)
    pivot = x[end]  # subject of comparison
    boundary = start - 1  # invariant: all els <= boundary will be <= pivot
    for i in range(start, end):
        if x[i] <= pivot:
            # if x[i] <= pivot, it should live in the left (<= boundary)
            # region. we can accomplish this by:
            # - extending the boundary by one to accommodate it, then
            # - swapping it with whatever is there. this is ok b/c:
            #      - conceptually, we're swapping left (i >= boundary)
            #      - so either now i == boundary (and swap is noop),
            #      - or i > boundary, and what we're swapping x[i] with at
            #        x[boundary] has already been checked, and is > pivot
            #        anyway, so it's fine staying right of the boundary, moving
            #        potentially much further right to wherever x[i] is
            boundary += 1
            x[i], x[boundary] = x[boundary], x[i]
        else:
            # x[i] > pivot, so it should live right of the boundary. this is
            # fine, we just keep boundary where it is.
            pass

    # now, we have two partitions, and the pivot:
    # x[start : boundary + 1] (i.e., boundary-inclusive) that's <= pivot
    # x[boundary + 1 : end] (i.e., pivot-exclusive) that's > pivot
    # x[end] the pivot
    #
    # if we swap the pivot into right after the boundary, it'll live at the right place.
    # (bounds ok? yes: boundary is at most the same as end.)
    x[end], x[boundary + 1] = x[boundary + 1], x[end]

    # now the partitions and the pivot are at:
    # x[start : boundary + 1]  <-- <= pivot
    # x[boundary + 1]          <-- pivot
    # x[boundary + 2 : end]    <-- > pivot
    #
    # we quicksort the partitions
    quicksort(x, start, boundary)  # not `boundary + 1`, b/c inclusive
    quicksort(x, boundary + 2, end)  # boundary + 2 ok? just check in call


def main() -> None:
    n = 10
    x = random.sample(range(1, n + 1), n)
    print(f"Before: {x}")
    quicksort(x)
    print(f"After:  {x}")
    assert x == sorted(x)


if __name__ == "__main__":
    main()
