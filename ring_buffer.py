"""queue/stack on an array with wrapping.

How it works:
- have fixed capacity
- expand (double) if adding and full
- head (h) points to top of queue/stack
- tail (t) points to first open slot at end
- if head == tail, buffer is either full or empty
- so, track # stored to differentiate full vs empty
- enqueues are at tail
- dequeues are from head

Examples showing internal state:

    start
    [_, _, _, _]
     h
     t

    enqueue(1)
    [1, _, _, _]
     h  t

    enqueue(2), enqueue(3)
    [1, 2, 3, _]
     h        t

    enqueue(4)
    [1, 2, 3, 4]
     h
     t

    dequeue() -> 1
    [_, 2, 3, 4]
     t  h

    dequeue() -> 2
    [_, _, 3, 4]
     t     h

    enqueue(5)
    [5, _, 3, 4]
        t  h

    enqueue(6)
    [5, 6, 3, 4]
           h
           t

    enqueue(7):

        _full() so _resize(): copy over in head -> tail order
        [3, 4, 5, 6, _, _, _, _]
        h
                    t

        then add:
        [3, 4, 5, 6, 7, _, _, _]
        h              t

as a party trick, added push() to support stack semantics as well
- push() adds to the head
- what about pop()? that's just dequeue() (from head)

push() example follows. we'll make space first to show both ordinary and wrapping push().

    dequeue() -> 3
    [_, 4, 5, 6, 7, _, _, _]
        h           t

    push(3)
    [3, 4, 5, 6, 7, _, _, _]
     h              t

    push(2)
    [3, 4, 5, 6, 7, _, _, 2]
                    t     h

    push(1)
    [3, 4, 5, 6, 7, _, 1, 2]
                    t  h

Other notes:
- I didn't add removing from the tail but you could
- __getitem__ (i.e., rb[index]) naturally supports peek() via rb[0]
- with __len__, you can do rb[len(rb) - 1] to get the tail item
- __iter__ is cool
- added a few other dunder methods too
"""


class RingBuffer:
    __slots__ = ["ring", "head", "tail", "stored"]

    def __init__(self, capacity: int = 10):
        self.ring = [None] * capacity  # len(self.ring) for capacity checks
        self.head = 0
        self.tail = 0
        self.stored = 0  # how much have we actually stored

    def _full(self):
        """Returns whether storage is at current underlying buffer capacity."""
        if self.stored == len(self.ring):
            assert self.head == self.tail  # sanity check
            return True
        return False

    def _expand(self):
        """Doubles capacity, copies into new buffer. Call when full.
        Copies so head starts @ [0] and tail is @ [len()].
        """
        if not self._full():
            print("WARNING: Expanding when not full")
        old_capacity = len(self.ring)
        new_capacity = 2 * old_capacity  # could easily make 2x configurable
        new_ring = [None] * new_capacity
        old_i, new_i = self.head, 0
        while new_i < len(self.ring):
            new_ring[new_i] = self.ring[old_i]
            old_i = (old_i + 1) % len(self.ring)
            new_i += 1
        self.ring = new_ring
        self.head = 0
        self.tail = new_i
        # print(f"LOG: Expanded capacity from {old_capacity} to {new_capacity}")

    def enqueue(self, item):
        """queue enqueue (add to tail)"""
        if self._full():
            self._expand()
        self.ring[self.tail] = item
        self.tail = (self.tail + 1) % len(self.ring)
        self.stored += 1

    def dequeue(self):
        """queue dequeue / stack pop (remove from head)"""
        if self.stored == 0:
            print("WARNING: Tried to dequeue from empty")
            return None
        item = self.ring[self.head]
        self.ring[self.head] = None
        self.head = (self.head + 1) % len(self.ring)
        self.stored -= 1
        return item

    # adding push() so this also works like a stack. push() adds to top, at head.

    def push(self, item):
        """stack push (add to head)"""
        if self._full():
            self._expand()
        self.head -= 1
        if self.head < 0:
            self.head = len(self.ring) - 1
        self.ring[self.head] = item
        self.stored += 1

    # here's some dunder support to make this feel more like a first-class Python thing

    def __len__(self):
        return self.stored

    def __bool__(self):
        return self.stored > 0

    def __iter__(self):
        # print("Using iterator")
        i = self.head
        for _ in range(self.stored):
            yield self.ring[i]
            i = (i + 1) % len(self.ring)

    def __repr__(self):
        return f"RingBuffer(capacity={len(self.ring)}, stored={self.stored}, head={self.head}, tail={self.tail})"

    def __contains__(self, item):
        """O(n) check"""
        # clever: any() short-circuits, and we use our iterator (__iter__).
        # this checks the sequence in order, and any() stops on first match.
        return any(element == item for element in self)

    def __getitem__(self, index):
        """O(1). [0] is top of data structure, [len() - 1] is bottom. Note that:
        - push() adds to top, dequeue() pops from top
        - enqueue() adds to bottom

        doesn't support negative index.
        """
        # this also handles the empty case, because then self.stored == 0, and no value
        # is both >= 0 and < 0. also note the cool three-part comparison.
        if not 0 <= index < self.stored:
            raise IndexError(
                f"index {index} out of range; need 0 <= index < {self.stored}"
            )
        return self.ring[(self.head + index) % len(self.ring)]


def test_basic() -> None:
    rb = RingBuffer(4)
    res = []
    for i in range(20):
        rb.enqueue(i)
    for i in range(10):
        res.append(rb.dequeue())
    for i in range(20, 40):
        rb.enqueue(i)
    for i in range(30):
        res.append(rb.dequeue())

    # print("Got:")
    # print(res)
    assert res == list(range(40))

    print("test_basic() passed")


def test_stack() -> None:
    rb = RingBuffer(4)
    rb.enqueue(3)
    rb.enqueue(4)
    rb.enqueue(5)
    rb.push(2)
    rb.push(1)
    rb.push(0)
    assert list(iter(rb)) == list(range(6))

    print("test_stack() passed")


def test_dunders() -> None:
    rb = RingBuffer(4)

    assert not rb

    for i in range(6):
        rb.enqueue(i)
    for i in range(2):
        rb.dequeue()

    # should now be:
    # [None, None, 2, 3, 4, 5, None, None]
    #              h             t

    # __len__
    assert len(rb) == 4

    # __bool__
    assert rb

    # __iter__
    assert list(iter(rb)) == [2, 3, 4, 5]

    # __repr__
    # brittle and silly test I know
    assert str(rb) == "RingBuffer(capacity=8, stored=4, head=2, tail=6)"

    # __contains__
    assert 2 in rb
    assert 5 in rb
    assert 1 not in rb
    assert 6 not in rb

    # __getitem__
    for i, e in enumerate([2, 3, 4, 5]):
        assert rb[i] == e

    print("test_dunders() passed")


def test_vs_reference(n_ops: int = 1000) -> None:
    """Uses both RingBiffer and a collections.deque as queues (and stack pushes!).
    Performs a bunch of operations on each and checks that they match."""
    from collections import deque
    import random

    rb = RingBuffer()
    dq = deque()
    stored = 0

    operations = ["enqueue", "dequeue", "push", "len", "peek"]
    for _ in range(n_ops):
        op = random.choice(operations)
        # print(f"Testing op {_}/{n_ops}: {op}")
        if op == "enqueue":
            val = random.randint(0, n_ops * 10)
            rb.enqueue(val)
            dq.append(val)
        elif op == "dequeue":
            if stored == 0:
                continue
            val1 = rb.dequeue()
            val2 = dq.popleft()
            assert val1 == val2
        elif op == "len":
            assert len(rb) == len(dq)
        elif op == "peek":
            if stored == 0:
                continue
            assert rb[0] == dq[0]
        elif op == "push":
            val = random.randint(0, n_ops * 10)
            rb.push(val)
            dq.appendleft(val)
        else:
            assert False, f"unsupported op: {op}"

    # final party trick: everything left should match
    assert all(i == j for i, j in zip(iter(rb), iter(dq)))

    # print("Final state:")
    # print("RingBuffer:", list(iter(rb)))
    # print("deque:     ", list(iter(dq)))

    print("test_vs_reference() passed")


def main() -> None:
    test_basic()
    test_stack()
    test_dunders()
    test_vs_reference()


if __name__ == "__main__":
    main()
