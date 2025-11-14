"""
UNFINISHED

Using heaps for the fun trick of maintaining the kth smallest element.

- use a max-heap `smallest` of the k-smallest to always have the kth smallest ready.
- use a min-heap `rest` of everything else, if we need to support deletions

at any given point in time, `smallest` has the smallest k elements. say the largest
value in `smallest` is K.

to insert a new value V:
- if V < K, then evict K (to rest) and add V to heap
- if V > K, add V to rest

to delete a value D:
- find whether in smallest (max-heap) or rest (min-heap)
    - if this isn't known, check D <= K
- if deleting from rest, just delete it
- if deleting from smallest, then add the min value of rest to smallest after
"""

import heapq


class FrequentKSmallest:
    def __init__(self, k: int):
        # python's heapq operates on standard arrays
        self.smallest = []
        self.rest = []
        self.k = k

    def insert(self, v: int) -> None:
        if len(self.smallest) < self.k:
            heapq.heappush_max(self.smallest, v)


# NOTE: Unfinished!
