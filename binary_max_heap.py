"""
Binary (max, WLOG) heap, implements a priority queue.

throughout:
    v = value
    i = index

Storing `int`s as values directly for simplicity.

If this were tracking an order on actual objects, I think there'd be three main
approaches:

    1. store objects themselves in the backing array. access `.priority` to compare,
       swap whole objects

    2. store `{priority, pointer}` in the backing array. access `.priority` to compare,
       swap just mini structs.

    3. store indices into an array `a` of objects in the backing array. `a[i].priority`
       to compare, swap just ints.

(I think 3. is probably the most elegant.)
"""

import random

# index operations for backing the binary heap with an array.
# existence of indices not guaranteed!


def parent(i: int) -> int:
    return (i - 1) // 2  # floor


def children(i: int) -> tuple[int, int]:
    return (2 * i + 1, 2 * i + 2)


# normally not a big class guy, but it beats passing the data array everywhere


class BinaryMaxHeap:
    def __init__(self):
        # dynamic array, handles resizing. thanks python
        self.values: list[int] = []

    def _bubble_up(self, i: int):
        """Recursively swap i with its parent if i is bigger.

        AKA up-heap, percolate-up, sift-up, trickle-up, swim-up, heapify-up,
        cascade-up, fix-up

        O(log n)
        """
        if i == 0:
            return  # at root

        p = parent(i)
        if self.values[i] > self.values[p]:
            self.values[i], self.values[p] = self.values[p], self.values[i]
            self._bubble_up(p)

    def _bubble_down(self, i: int):
        """Recursively swap i with its largest child if either is bigger than it.

        AKA down-heap, percolate-down, sift-down, sink-down, trickle down,
        heapify-down, cascade-down, fix-down, extract-min or extract-max, or
        just heapify

        O(log n)
        """
        c1, c2 = children(i)
        candidates = [c for c in [c1, c2] if c < len(self.values)]  # validate
        if len(candidates) == 0:
            return  # at leaf
        max_val = max(self.values[c] for c in candidates)
        if max_val > self.values[i]:
            max_c = [c for c in candidates if self.values[c] == max_val][0]
            self.values[i], self.values[max_c] = (
                self.values[max_c],
                self.values[i],
            )
            self._bubble_down(max_c)

    # operations
    #
    # going with ValueError because I usually have invalid operations return
    # None, so trying exceptions instead as something new.

    def find_max(self):
        """O(1)"""
        if len(self.values) == 0:
            raise ValueError()
        return self.values[0]  # it's me, Max. I'm always right here.

    def insert(self, v: int):
        """O(log n)"""
        self.values.append(v)
        self._bubble_up(len(self.values) - 1)  # the inserted index

    def size(self) -> int:
        """Only seemed polite since invalid requests raise ValueError.

        O(1)
        """
        return len(self.values)

    def extract(self) -> int:
        """AKA "delete max;" remove and return the max val, O(log n)"""
        if len(self.values) == 0:
            raise ValueError()
        if len(self.values) == 1:
            return self.values.pop()

        ret = self.values[0]  # should I call find_max()?
        self.values[0] = self.values.pop()  # end --> root
        self._bubble_down(0)
        return ret

    def insert_then_extract(self, v: int) -> int:
        """insert a new value and extract the new largest. O(log n)"""
        # if what we're inserting is the new max, we can just return it
        if len(self.values) == 0 or v > self.values[0]:
            return v

        # else, we return the root, and bubble down
        ret = self.values[0]
        self.values[0] = v
        self._bubble_down(0)
        return ret

    def delete(self, i: int) -> int:
        """deletes value at index i and returns it. O(log n)"""
        if i >= len(self.values):
            raise ValueError()
        deleted = self.values[i]
        self.values[i] = self.values.pop()  # last element -> here
        if self.values[i] > deleted:
            # the last element is bigger than what was here, so we may
            # need to move it up
            self._bubble_up(i)
        else:
            # smaller, so may need to move it down
            self._bubble_down(i)
        return deleted

    def search(self, v: int) -> int:
        """Finds the first index i that has the value v, or ValueError if doesn't exist.

        O(n)

        Felt right to add this since so many functions are passed an index i,
        but practically it seems like you'd want to find the index i based on
        a value v."""
        return self.values.index(v)

    def decrease_key(self, i: int, v: int):
        """Decreases the value at index i to be v."""
        if i >= len(self.values):
            raise ValueError()
        self.values[i] = v
        self._bubble_down(i)  # as smaller, maybe move down

    def increase_key(self, i: int, v: int):
        """Increases the value at index i to be v."""
        if i >= len(self.values):
            raise ValueError()
        self.values[i] = v
        self._bubble_up(i)  # as larger, maybe move up

    def modify_key(self, i: int, v: int):
        """Modifies the value at index i to be v.

        Seems like you'd just want this as an API right?
        """
        if i >= len(self.values):
            raise ValueError()
        if v < self.values[i]:
            self.decrease_key(i, v)
        else:
            self.increase_key(i, v)

    def meld(self, other: "BinaryMaxHeap"):
        """AKA 'merge', combines `other` (m) into this (n) heap.

        Does not mutate `other`.

        Binary heaps have no special meld runtime. The two main options are:
            1. insert each of m          - O(m log(n + m))
            2. heapify both from scratch - O(n + m)

        Here we simply do 1.
        """
        # copy values first in case we're doing `h.meld(h)`
        for v in other.values[:]:
            self.insert(v)

    @staticmethod
    def build_heap(vs: list[int]) -> "BinaryMaxHeap":
        """Constructs a heap from provided values vs.

        Rather than inserting n elements (O(n log n), Williams), we
        immediately construct a binary tree (shape property) then order it
        (heap property) (O(n), Floyd).

        Running time is O(n) due to a complicated analysis. Naively we're
        skipping the leaves (~n/2) and doing h (log n) operations per node,
        but this ends up being good enough to reduce us from O(n log n) to
        O(n).
        """
        h = BinaryMaxHeap()
        h.values = vs[:]  # copy over. complete binary tree achieved!

        if len(h.values) == 0:
            return h  # avoid no values edge case range would hit

        # now, make sure every node is bigger than its children, or
        # moves down if not. trivially true for leaf nodes, so start at
        # penultimate level and work back up to root node, inclusive.
        for i in range(len(h.values) // 2, -1, -1):
            h._bubble_down(i)

        return h


def extract_all(h: BinaryMaxHeap) -> list[int]:
    """Calls extract() on h until it's empty. Returns list of results."""
    ordered = []
    while h.size() > 0:
        ordered.append(h.extract())
    return ordered


def main():
    # build from shuffled [1, 10]
    vs = list(range(1, 11))
    random.shuffle(vs)
    h = BinaryMaxHeap.build_heap(vs)
    ordered = extract_all(h)
    print("original:    ", vs)
    print("max heap'd:  ", ordered)

    # build again, this time from inserts, and merge
    for v in vs:
        h.insert(v)
    h.meld(h)
    print("self-melded: ", extract_all(h))

    # try more operations
    h = BinaryMaxHeap.build_heap(vs)
    h.delete(0)  # delete 10
    h.decrease_key(0, 2)  # 9 -> 2
    h.modify_key(0, 2)  # 8 -> 2
    h.increase_key(h.search(1), 2)  # 1 -> 2
    print("7-3, 2 2 2 2:", extract_all(h))


if __name__ == "__main__":
    main()
