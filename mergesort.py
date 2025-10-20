"""Mergesort

- divide
- conquer (sort)
- merge (easy b/c sorted)

Properties:
- best O(n log n)
- worst O(n log n)
- in general, not in-place;
- in general, needs O(n) extra space
"""

import random


def mergesort(x: list[int]) -> list[int]:
    # 0- or 1-el lists are sorted
    if len(x) <= 1:
        return x

    # divide. as with all binary stuff, OBOB easy to do.
    # n    n // 2   x[:middle], x[middle:]
    # ---  ---      ---
    # 0     0       n/a! would have returned
    # 1     0       n/a! would have returned
    # 2     1       [0], [1]
    # 3     1       [0], [1,2]
    # 4     2       [0,1], [2,3]
    # 5     2       [0,1], [2,3,4]
    # ...
    middle = len(x) // 2

    # conquer
    left = mergesort(x[:middle])
    right = mergesort(x[middle:])

    # merge
    sorted = []
    i, j = 0, 0
    while i < len(left) or j < len(right):
        # if either list is exhausted, add rest from the other. (might as well
        # do all at once.)
        if i == len(left):
            sorted.extend(right[j:])
            j = len(right)
        elif j == len(right):
            sorted.extend(left[i:])
            i = len(left)
        else:
            # standard case, we add whichever is smaller
            if left[i] < right[j]:
                sorted.append(left[i])
                i += 1
            else:
                sorted.append(right[j])
                j += 1
    return sorted


def main() -> None:
    n = 10
    x = random.sample(range(1, n + 1), n)
    print(f"Before: {x}")
    sorted_x = mergesort(x)
    print(f"After:  {sorted_x}")
    assert sorted_x == sorted(x)


if __name__ == "__main__":
    main()
