"""AKA cumulative sum, scan.

For an input array x, its prefix sum is a new array y, where each entry y[i]
is the cumulative sum of x from x[0] through x[i].
"""

prefix_sum_oneliner = lambda x: [sum(x[:i]) for i in range(len(x))]
"""cute O(n^2) prefix sum that's a python one-liner."""


def prefix_sum(xs: list[int]) -> list[int]:
    """Returns prefix sum of xs in O(n)."""
    y = [0] * len(xs)
    for i, x in enumerate(xs):
        y[i] = x + (y[i - 1] if i > 0 else 0)
    return y


def main() -> None:
    a = [1, 2, 3, 4, 5]
    b = prefix_sum(a)
    print(a)
    print(b)


if __name__ == "__main__":
    main()
