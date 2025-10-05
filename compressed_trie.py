"""Compressed trie, AKA: compact prefix tree, Patricia tree/trie, radix tree/trie (ish).

This is a simple variant of a vanilla (character-per-node) trie where each node that is
an only child is merged with its parent.
"""

from abc import ABC, abstractmethod
from typing import Optional


def longest_common_start(s1: str, s2: str) -> int:
    """returns number of characters of longest common starting substring of s1 and s2.

    for example:
        0 1 2 3 4 5 6 7
        a r t e r i e s
        a r t
        -> returns 3

        0 1 2 3 4 5 6 7
        a r t e r i e s
        a r t i f a c t
        -> returns 3

        0 1 2 3 4 5
        a r t
        b a n a n a
        -> returns 0
    """
    min_len = min(len(s1), len(s2))
    for i in range(min_len):
        if s1[i] != s2[i]:
            return i
    return min_len


class CTrieNode(ABC):
    __slots__ = ("terminal",)

    def __init__(self, terminal: bool):
        self.terminal: bool = terminal

    # The following abstract methods allow a concrete node subclass to store
    # its edges and children in different data structures. Done this way
    # demonstrate the O(rk) and O(k) lookup approaches.

    @abstractmethod
    def _matches_edge(self, word: str) -> Optional[tuple[str, "CTrieNode"]]:
        """returns (substring, CTrieNode) if there's a substring of word that
        exactly matches an edge, else None.
        """
        pass

    @abstractmethod
    def _overlaps_edge(
        self, word: str
    ) -> tuple[Optional["CTrieNode"], str, int]:
        """Returns any overlapping edge's (node, edge, overlap len),
        or (None, "", 0) if there's none.

        At most 1 edge will have any common start overlap with word b/c no edges
        have any prefix overlap because that's how a prefix data structure works.
        """
        pass

    @abstractmethod
    def _add_child(self, edge: str, terminal: bool) -> "CTrieNode":
        """adds edge pointing to a new node w/ specified terminal set. returns child.

        may validate no shared prefixes, so if modifying, delete before calling this.
        """
        pass

    @abstractmethod
    def _add_child_node(self, edge: str, child: "CTrieNode") -> "CTrieNode":
        """adds new edge pointing to child. returns child.

        may validate no shared prefixes, so if modifying, delete before calling this.
        """
        pass

    @abstractmethod
    def _remove_edge(self, edge: str) -> None:
        """removes edge"""
        pass

    @abstractmethod
    def all_children(self) -> list[tuple[str, "CTrieNode"]]:
        pass

    @abstractmethod
    def _depth_sets(self, level=0) -> list[tuple[int, set[str]]]:
        """helper for fun viz. returns list of [depth, set(strs at depth) ]"""
        pass

    @abstractmethod
    def _n_children(self) -> int:
        """conceptually, self.terminal counts as another child, so its included in the
        total."""
        pass

    @abstractmethod
    def _get_only_child(self) -> tuple[str, "CTrieNode"]:
        """gets the only child's (edge, child). should only be called when
        self._n_children() == 1, and not self.terminal. only used before deeply
        modifying."""
        pass

    # the following happen to be the same implementation, but could be broken
    # out into subclasses if needed.

    def _replace_edge(
        self,
        old_edge: str,
        new_edge: str,
        node: "CTrieNode",
    ) -> None:
        """replaces old_edge with new_edge pointing to node"""
        self._remove_edge(old_edge)
        self._add_child_node(new_edge, node)

    # the following are the main concrete operations implementing the data structure.

    def _find_insertion_node(self, word: str) -> tuple["CTrieNode", str]:
        """returns node where word would be inserted, and how much is left

        returns (node, remainder) where remainder is any trailing substr of word. Note
        that if the word was found, node.terminal() == True and remainder == ''.
        """
        # terminal case
        if len(word) == 0:
            return (self, word)

        # search edges case
        match = self._matches_edge(word)
        if match is None:
            return (self, word)
        substr, node = match
        remainder = word[len(substr) :]
        return node._find_insertion_node(remainder)

    def search(self, word: str) -> bool:
        """Returns whether word is found in this subtree"""
        node, remainder = self._find_insertion_node(word)
        return len(remainder) == 0 and node.terminal

    def insert(self, word: str):
        """inserts word into this subtree"""
        node, remainder = self._find_insertion_node(word)
        if len(remainder) == 0:
            # already have node at terminal! ensure terminal True (already is if exists)
            node.terminal = True
            return

        # otherwise, there's some remainder left. two main cases: (1) there's
        # no matching substr below, so we make a fresh child. (2) we have a
        # partial match with an edge, so we'll have to split.
        subnode, edge, lcs = node._overlaps_edge(remainder)
        if subnode is None:
            # (1). means lcs == 0, so we add all remainder
            assert len(edge) == 0 and lcs == 0
            node._add_child(remainder, True)
        else:
            # (2) split. two suboptions:
            #     (a) our intermediate node is terminal if lcs == len(remainder).
            #         (like []--"artifice"-->[] + "art" = []--"art"-->[]--"ifice"-->[])
            #
            #     (b) our intermediate node isn't terminal and we need another for rest.
            # add intermediate node
            intermediate_is_terminal = lcs == len(remainder)
            node._remove_edge(edge)  # do now for sanity checks
            intermediate = node._add_child(
                remainder[:lcs],
                intermediate_is_terminal,  # for (a)
            )
            # always add back the existing subnode with a shortened edge
            intermediate._add_child_node(edge[lcs:], subnode)
            # for (b), add a new node for this word
            if not intermediate_is_terminal:
                intermediate._add_child(remainder[lcs:], True)

    def _find_parent(self, word: str) -> tuple["CTrieNode", str, "CTrieNode"]:
        """returns (parent, edge, node), where node specifies word. helper for delete().

        very similar to _find_insertion_node(), but we don't have parent
        references. so if we're to delete a node, we need to be looking down
        towards it.
        """
        # search edges case
        match = self._matches_edge(word)
        if match is None:
            raise ValueError(f"word (remainder) '{word}' not found in ctrie")
        substr, node = match
        remainder = word[len(substr) :]
        if len(remainder) == 0:
            return self, substr, node  # found case
        return node._find_parent(remainder)  # recurse case

    def delete(self, word: str):
        print(f"deleting '{word}'")
        parent, edge, node = self._find_parent(word)
        if node.terminal is False:
            raise ValueError(f"Can't delete '{word}' as it wasn't stored")
        node.terminal = False
        if node._n_children() >= 2:
            # easy case: node still used by children. done.
            print("  delete: 2 children case (easy)")
            pass
        elif node._n_children() == 1:
            # node was a terminal with a single option below (conceptually, 2
            # -> 1 children). now that it's no longer a terminal, its should
            # be compressed with its parent. example:
            #
            #             deleted "art", no longer Terminal
            #             v
            # []--"art"-->[]--"ifice"-->[] (-->)
            # parent      node          child
            #
            # should now become:
            #
            # []--"artifice"-->[]
            # parent          child
            #
            # we don't need to worry about parent, because parent must have started with
            # >= 2 children (including 1 if it's terminal). node was 1 of its children,
            # and now child will *still* be 1 of its children.
            print("  delete: 1 child case (medium)")
            child_edge, child = node._get_only_child()
            parent._replace_edge(edge, edge + child_edge, child)
        elif node._n_children() == 0:
            # node had no children, so it can be removed. this means parent's
            # number of children decreases, which means it might need to be
            # merged with its parent if it has 1 left (node's sibling). this will
            # make grandparent point directly to sibling.
            print("  delete: 0 children case (hard)")
            parent._remove_edge(edge)
            if parent._n_children() == 1:
                # example: deleting "artifice":
                #
                #                 +----"ful"----> [] sibling
                #                 |
                # [] ---"art"---> [] --"ifice"--> [] node
                # grandparent   parent
                #
                #                 +----"ful"----> [] sibling
                #                 |
                # [] ---"art"---> []
                # grandparent   parent <-- ! only 1 child! merge w/ grandparent
                #
                # [] ---"artful"---> []
                # grandparent      sibling

                # NOTE: this is inefficient: finding grandparent! should put
                # in _find_parent() but it's annoying to track grandparents.
                grandparent, parent_edge, parent_ = self._find_parent(
                    word[: -len(edge)]
                )
                assert parent_ is parent
                sibling_edge, sibling = parent._get_only_child()
                grandparent._replace_edge(
                    parent_edge, parent_edge + sibling_edge, sibling
                )

        else:
            assert False  # should never have < 0 children

    def traverse(self, prefix: list[str] = []) -> list[str]:
        """O(n), return a list of all stored strings"""
        res = []
        if self.terminal:
            res.append("".join(prefix))
        for edge, child in self.all_children():
            res.extend(child.traverse(prefix + [edge]))
        return res

    def __repr__(self) -> str:
        """O(n), returns all stored strings newline-separated"""
        return "\n".join(self.traverse())

    def print_depths(self) -> None:
        """fun viz (accumulate characters at each tree depth and print).

        In lieu of figuring out how to actually print trees "graphically" in text.
        """
        ss = self._depth_sets()
        for i in range(max(d for d, _cs in ss)):
            d_cs = set()
            for cs in [cs for d, cs in ss if d == i]:
                d_cs.update(cs)
            print(i, d_cs)


class CTrieNodeEdgeIterate(CTrieNode):
    """This is a data structure for a Compressed Trie Node that looks up edges by
    iterating over them, which is O(rk), where r is the radix, AKA the set of unique
    characters, and k is the length of a key (stored word). (For example, if storing
    lowercase English letters only, r = 26, and when storing 'apple', k = 5)

    This class contains the methods for getting/storing edges, and doing substring
    lookups. The core data structure methods search(), insert(), and delete() are
    implemented on the superclass CTrieNode.
    """

    __slots__ = ("_children",)

    def __init__(self, terminal: bool):
        super().__init__(terminal)
        self._children: dict[str, CTrieNode] = {}

    def _matches_edge(self, word: str) -> Optional[tuple[str, "CTrieNode"]]:
        """
        This is one of the core O(rk) operations we can speed up to O(k)
        """
        for substr, node in self._children.items():  # O(r)
            if word.startswith(substr):  # O(k)
                return (substr, node)
        return None

    def _overlaps_edge(
        self, word: str
    ) -> tuple[Optional["CTrieNode"], str, int]:
        """
        This is one of the core O(rk) operations we can speed up to O(k)
        """
        # due to that this is still a prefix trie, only one child will have a
        # common start > 0. because if multiple children did, that shared
        # prefix should already have been split down into its own node.
        for edge, node in self._children.items():  # O(r)
            lcs = longest_common_start(edge, word)  # O(k)
            if lcs > 0:
                return node, edge, lcs
        return None, "", 0

    def _add_child(self, edge: str, terminal: bool) -> "CTrieNode":
        return self._add_child_node(edge, CTrieNodeEdgeIterate(terminal))

    def _add_child_node(self, edge: str, child: "CTrieNode") -> "CTrieNode":
        self._children[edge] = child
        assert sum(edge[0] == w[0] for w in self._children.keys()) == 1
        return child

    def _remove_edge(self, edge: str) -> None:
        del self._children[edge]

    def all_children(self) -> list[tuple[str, "CTrieNode"]]:
        return list(self._children.items())

    def _depth_sets(self, level=0) -> list[tuple[int, set[str]]]:
        res = [
            (
                level,
                set(f"{c} ({n.terminal})" for c, n in self._children.items()),
            )
        ]
        for node in self._children.values():
            res.extend(node._depth_sets(level + 1))
        return res

    def _n_children(self) -> int:
        return len(self._children) + (1 if self.terminal else 0)

    def _get_only_child(self) -> tuple[str, "CTrieNode"]:
        assert not self.terminal and self._n_children() == 1
        for edge, node in self._children.items():
            return edge, node
        assert False


class CTrieNodeCharLookup(CTrieNode):
    """This is a data structure for a Compressed Trie Node that looks up edges by
    indexing by the first letter, which is O(1), then comparing strings, which is O(k).

    This class contains the methods for getting/storing edges, and doing substring
    lookups. The core data structure methods search(), insert(), and delete() are
    implemented on the superclass CTrieNode.
    """

    __slots__ = ("_children",)

    def __init__(self, terminal: bool):
        super().__init__(terminal)
        self._children: dict[str, tuple[str, CTrieNode]] = {}
        """dict from {edge's first char: (edge, node)}, like {'a': ('apple', node)}"""

    def _matches_edge(self, word: str) -> Optional[tuple[str, "CTrieNode"]]:
        """
        This is one of the core O(k) operations we sped up from O(rk)
        """
        if len(word) > 0 and word[0] in self._children:  # O(1)
            edge, node = self._children[word[0]]
            if word.startswith(edge):  # O(k)
                return (edge, node)
        return None

    def _overlaps_edge(
        self, word: str
    ) -> tuple[Optional["CTrieNode"], str, int]:
        """
        This is one of the core O(k) operations we sped up from O(rk)
        """
        if len(word) > 0 and word[0] in self._children:  # O(1)
            edge, node = self._children[word[0]]
            lcs = longest_common_start(edge, word)  # O(k)
            if lcs > 0:
                return node, edge, lcs
        return None, "", 0

    def _add_child(self, edge: str, terminal: bool) -> "CTrieNode":
        return self._add_child_node(edge, CTrieNodeCharLookup(terminal))

    def _add_child_node(self, edge: str, child: "CTrieNode") -> "CTrieNode":
        first = edge[0]
        if first in self._children:
            raise ValueError(
                f"cannot add edge {edge} when {self._children[first][0]} already stored"
            )
        self._children[first] = (edge, child)
        return child

    def _remove_edge(self, edge: str) -> None:
        del self._children[edge[0]]

    def all_children(self) -> list[tuple[str, "CTrieNode"]]:
        return list(self._children.values())

    def _depth_sets(self, level=0) -> list[tuple[int, set[str]]]:
        res = [
            (
                level,
                set(
                    f"{c} ({n.terminal})" for c, n in self._children.values()
                ),
            )
        ]
        for _, node in self._children.values():
            res.extend(node._depth_sets(level + 1))
        return res

    def _n_children(self) -> int:
        return len(self._children) + (1 if self.terminal else 0)

    def _get_only_child(self) -> tuple[str, "CTrieNode"]:
        assert not self.terminal and self._n_children() == 1
        for edge, node in self._children.values():
            return edge, node
        assert False


def main() -> None:
    # test helpers
    assert longest_common_start("art", "arteries") == 3
    assert longest_common_start("artifact", "arteries") == 3
    assert longest_common_start("art", "banana") == 0

    # to switch between node implementations
    # Node = CTrieNodeEdgeIterate
    Node = CTrieNodeCharLookup

    t1 = Node(False)
    t1.insert("artifact")
    t1.insert("artifice")
    t1.insert("art")
    t1.insert("artificial")
    print(t1)
    t1.print_depths()

    # ctrie.delete("art")  # 1 child (medium)
    # ctrie.delete("artificial") # 0 children (hard)
    # 2 children (following two lines): easy
    t1.insert("artful")
    t1.delete("art")
    print(t1)
    t1.print_depths()

    t2 = Node(False)
    t2.insert("julie")
    t2.insert("july")
    # t.delete("jul")  # value error
    t2.insert("julius")
    t2.delete("julie")
    # t.insert("abcdefghijklmnopqrstuvwxyz")
    # t.insert("abra")
    t2.print_depths()


if __name__ == "__main__":
    main()
