"""Trie - a basic prefix tree.

Stores a value for each string (default just 1). This conveniently doubles as
indicating that we've reached a terminus (i.e., we've hit a stored word),
necessary for non-leaf termination (e.g., if storing all of 'i', 'in', and
'inn')
"""

# import code
from typing import Optional


class TrieNode:
    __slots__ = ("children", "value")
    """nice trick: for type checker to verify attrs"""

    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.value: Optional[int] = None

    def insert(self, s: str, v: int = 1):
        """We store v (int) as payload data associated with s. For only storing
        a set of strings, it might as well be a single bit to indicate possible
        non-leaf termination (e.g., if storing all of 'i', 'in', and 'inn')."""
        # terminal
        if len(s) == 0:
            self.value = v
            return

        # any continuations
        c, rest = s[0], s[1:]
        if c not in self.children:
            self.children[c] = TrieNode()
        self.children[c].insert(rest, v)

    def traverse(self, accum: list[str] = []) -> list[str]:
        """Returns a list of all stored words."""
        res = []

        # terminal
        if self.value is not None:
            res.append("".join(accum) + f" ({self.value})")

        # any continuations
        for c, node in self.children.items():
            res.extend(node.traverse(accum + [c]))

        return res

    def _depth_sets(self, level=0):
        """helper for fun viz"""
        res = [(level, set(c for c in self.children.keys()))]
        for node in self.children.values():
            res.extend(node._depth_sets(level + 1))
        return res

    def print_depths(self):
        """fun viz (accumulate characters at each tree depth and print).

        In lieu of figuring out how to actually print trees "graphically" in text.
        """
        ss = self._depth_sets()
        for i in range(max(d for d, _cs in ss)):
            d_cs = set()
            for cs in [cs for d, cs in ss if d == i]:
                d_cs.update(cs)
            print(i, d_cs)

    def __repr__(self):
        return "\n".join(self.traverse())

    def search(self, s: str) -> Optional["TrieNode"]:
        """Returns node if it's found in the trie, else None."""
        if len(s) == 0:
            if self.value is not None:
                return self  # found
            return None  # not here (no terminal)
        c, rest = s[0], s[1:]
        if c not in self.children:
            return None  # no path
        return self.children[c].search(rest)  # continue

    def delete(self, s: str) -> bool:
        """returns whether this node can be fully deleted"""
        if len(s) == 0:
            # end of the line. mark no longer terminal.
            self.value = None

            # now, check whether there's children. if so, we leave everything
            # because continuations below us depend on us and our parents. but
            # if not, we can start propagating deletes upwards.
            return len(self.children) == 0

        # send down to children to delete
        c, rest = s[0], s[1:]
        if c not in self.children:
            raise ValueError(f"continuation {c} not found where expected")
        child_can_be_deleted = self.children[c].delete(rest)
        if child_can_be_deleted:
            del self.children[c]
            # continue propagating deletes up if we've no children and nonterminal
            return len(self.children) == 0 and self.value is None
        return False


def main() -> None:
    t = TrieNode()
    t.insert("hello", 47)
    t.insert("goodbye", 19)
    t.insert("i")
    print(t)
    t.print_depths()
    print()

    print("Search:")
    print("hello:", t.search("hello"))
    print("hell:", t.search("hell"))
    print("goodbye:", t.search("goodbye"))
    print("goodbyee:", t.search("goodbyee"))
    print("", t.search(""))
    print()

    print("Adding hell, good")
    t.insert("hell")
    t.insert("good")
    print(t)
    t.print_depths()
    print()

    print("Delete")
    print("delete hello")
    t.delete("hello")
    print(t)
    t.print_depths()
    print("delete good")
    t.delete("good")
    print(t)
    t.print_depths()
    print("delete goodbye")
    t.delete("goodbye")
    print(t)
    t.print_depths()

    # code.interact(local=dict(globals(), **locals()))


if __name__ == "__main__":
    main()
