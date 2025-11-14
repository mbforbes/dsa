from typing import Optional


class Node:
    """Linked list node."""

    __slots__ = ["val", "next_"]

    def __init__(self, val: int, next_: Optional["Node"] = None):
        self.val = val
        self.next_ = next_

    def __repr__(self) -> str:
        return f"Node({self.val}, ->({self.next_.val if self.next_ is not None else None}))"


def build_list_with_cycle():
    start = Node(0)
    start.next_ = Node(1)
    start.next_.next_ = Node(2)
    start.next_.next_.next_ = Node(3)
    start.next_.next_.next_.next_ = start.next_  # -> 1
    return start


def floyd_cycle_detection(start: Node):
    """Returns None if no cycle, or a Node within the cycle if there is one."""
    slow = start.next_
    fast = start.next_.next_ if start.next_ is not None else start.next_

    # slow wont' get None before fast does, but it makes type checker happy
    while fast is not None and slow is not None and slow is not fast:
        slow = slow.next_
        fast = fast.next_.next_ if fast.next_ is not None else fast.next_

    # we've finished! either something was None (terminated), or they're equal (cycle).
    # if fast finished, it was None, so we return None to indicate no cycle. if they
    # were equal, we'll return the Node to give a representative Node within the cycle.
    # either way, we can just return fast.
    return fast


def main() -> None:
    ll = build_list_with_cycle()
    maybe_cycle_node = floyd_cycle_detection(ll)
    assert maybe_cycle_node is not None
    print(f"Found cycle at {maybe_cycle_node}")


if __name__ == "__main__":
    main()
