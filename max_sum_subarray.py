"""Kadane's algorithm for finding the maximum sum sub-array in O(n)."""

from typing import Optional


def kadane_no_indices(xs: list[int]) -> Optional[int]:
    """easy mode: just returns best sum (or None if empty)"""
    best_sum, cur_sum = None, 0
    for x in xs:
        cur_sum = max(cur_sum + x, x)  # continue or restart
        best_sum = max(best_sum, cur_sum) if best_sum is not None else cur_sum
    return best_sum


def kadane(xs: list[int]) -> tuple[int, int, Optional[int]]:
    """returns (best_start, best_end (inclusive!), best_sum | None if empty)"""
    cur_start, cur_end = 0, 0
    best_start, best_end = 0, 0
    cur_sum = 0
    best_sum = None
    for i, x in enumerate(xs):
        if x > cur_sum + x:
            # starting new
            cur_start = i
            cur_end = i
            cur_sum = x
        else:
            # continue sum
            cur_sum = cur_sum + x
            cur_end = i

        # if new best, also update saved indices
        if best_sum is None or cur_sum > best_sum:
            best_start = cur_start
            best_end = cur_end
            best_sum = cur_sum

    return best_start, best_end, best_sum


def main() -> None:
    a = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    best_start, best_end, best_sum = kadane(a)
    print(a)
    print(f"best: sum(a[{best_start}:{best_end}]) (inclusive)")
    print(f"    = sum({a[best_start : best_end + 1]})")
    print(f"    = {sum(a[best_start : best_end + 1])}")
    print(f"    = {best_sum}")
    print(f"    = {kadane_no_indices(a)}")


if __name__ == "__main__":
    main()
