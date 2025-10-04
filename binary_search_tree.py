"""Super basic BST, no balancing, just to get the BST flavor.

Had basically all functional, migrated more to being instance methods, but a few
functional-ish ones remain (_traverse(), _search(), maybe _replace() counts too).
"""

import random
from typing import Optional


class BinaryTreeNode:
    def __init__(
        self,
        value: int,
        parent: Optional["BinaryTreeNode"],
        left: Optional["BinaryTreeNode"],
        right: Optional["BinaryTreeNode"],
    ):
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({self.value})"

    def insert(self, new: "BinaryTreeNode"):
        """inserts new into self.

        i preferred the non-class more recursive version from before, with the pattern:
            n.left = insert(n.left, new)
            n.left.parent = n
            return n

        ... but this convention only makes sense if you recurse down to calling on None
        and just returning new, which you can't do as an instance method. so making
        this an instance method meant changing this to the more branching way.
        """
        # equal; shouldn't happen
        if self.value == new.value:
            print("Error: assuming unique values. Not inserting.")

        if new.value < self.value:
            if self.left is not None:
                self.left.insert(new)
            else:
                self.left = new
                new.parent = self
        else:
            if self.right is not None:
                self.right.insert(new)
            else:
                self.right = new
                new.parent = self

    def minimum(self: "BinaryTreeNode") -> "BinaryTreeNode":
        """Traverse to leftmost leaf to find minimum."""
        # I kept the `self is None`` case in the BST's call, because we don't
        # actually want to recurse until None, we want to stop at a leaf.
        if self.left is None:
            return self
        return self.left.minimum()

    def maximum(self: "BinaryTreeNode") -> "BinaryTreeNode":
        """Traverse to rightmost leaf to find maximum node."""
        if self.right is None:
            return self
        return self.right.maximum()

    def successor(self: "BinaryTreeNode") -> Optional["BinaryTreeNode"]:
        """returns the node with the smallest value > the self's value, None if max."""
        # the logic here was quite tricky to convince myself of. x's successor is either:
        # 1. _minimum(x.right) if x.right exists, else
        # 2. move upwards until you go up-right (↗) once, then return that
        if self.right is not None:
            return self.right.minimum()

        cur, parent = self, self.parent
        while parent is not None and parent.right is cur:
            cur = parent
            parent = parent.parent
        return parent

    def predecessor(self: "BinaryTreeNode") -> Optional["BinaryTreeNode"]:
        """returns the node with the greatest value < the self's value, None if min."""
        # x's predecessor is either:
        # 1. _maximum(x.left) if x.left exists, else
        # 2. move upwards until you go up-left (↖) once, then return that
        if self.left is not None:
            return self.left.maximum()

        cur, parent = self, self.parent
        while parent is not None and parent.left is cur:
            cur = parent
            parent = parent.parent
        return parent

    def delete(self: "BinaryTreeNode", node: "BinaryTreeNode"):
        """
        Returns this subtree

        Assumes:
        - NO MORE node is not self (already checked in BST not root)
           - --> NO MORE node has a parent
        - node is in self's tree
        """
        n_children = len([c is None for c in [node.left, node.right]])

        # three cases:
        # (1) if node is a leaf, it's simply replaced by None
        if n_children == 0:
            _replace(node, None)
            return self if node is not self else None

        # (2) node has only one child. it's simply replaced by its child.
        # (makes sense because any values that would have been correctly
        # routed to it are fine being routed to its only child, because its
        # only child obeys the order node had with its parent.)
        if n_children == 1:
            child = node.left if node.left is not None else node.right
            _replace(node, child)
            return self if node is not self else child

        # (3) node has two children. we'll use its successor S to replace it.
        # (predecessor works too apparently.) two subcases:
        #    (a) node.right == S. this implies S.left is None (else S.left would be the
        #        successor), so S can replace node, adopting node's left child and
        #        keeping S's right child unchanged
        #
        #    (b) S is deeper in node.right's subtree.
        #
        #           we know this because the successor is either node.right.minimum() if
        #           node.right exists, or a traversal upwards, but node.right *must*
        #           exist because we have 2 children in this case. so S must be in
        #           node.right's subtree.
        #
        #        again we know S.left is None. we:
        #           - replace S with S.right
        #           - S replaces node
        s = node.successor()
        assert s is not None  # else node would be a leaf
        if node.right is s:
            # (a) case
            s.left = node.left
            _replace(node, s)
        else:
            # (b) case
            _replace(s, s.right)
            _replace(node, s)
            s.left = node.left
            s.right = node.right
        return self if node is not self else s


def _replace(node: BinaryTreeNode, replacement: Optional[BinaryTreeNode]):
    """replace node by setting node.parent's child to be replacement instead of node

    note that this doesn't alter any other children; that full operation is in delete().
    this just handles the fact that node.parent.child isn't defined because there's two
    children.
    """
    if node.parent is None:
        return  # nothing to wire up
    if node.parent.left is node:
        node.parent.left = replacement
    else:
        node.parent.right = replacement


def _traverse(subtree: Optional[BinaryTreeNode]):
    """Returns list of sorted values at and below subtree"""
    if subtree is None:
        return []

    return [
        *_traverse(subtree.left),
        subtree.value,
        *_traverse(subtree.right),
    ]


def _search(
    subtree: Optional[BinaryTreeNode], want: int
) -> Optional[BinaryTreeNode]:
    """Returns want's node if it's in subtree, else None"""
    if subtree is None:
        return None
    if subtree.value == want:
        return subtree
    if want < subtree.value:
        return _search(subtree.left, want)
    else:
        return _search(subtree.right, want)


class BST:
    """Somewhat awkward, likely unnecessary helper class to handle hanging onto the root
    reference and checking if it's None everywhere."""

    def __init__(self):
        self.root = None

    def insert(self, value: int):
        if self.root is None:
            self.root = BinaryTreeNode(value, None, None, None)
        else:
            self.root.insert(BinaryTreeNode(value, None, None, None))

    def traverse(self):
        return _traverse(self.root)

    def search(self, want: int):
        return _search(self.root, want)

    def minimum(self) -> Optional[BinaryTreeNode]:
        if self.root is None:
            return None
        return self.root.minimum()

    def maximum(self) -> Optional[BinaryTreeNode]:
        if self.root is None:
            return None
        return self.root.maximum()

    def delete(self, node: Optional[BinaryTreeNode]):
        if self.root is None:
            print("Can't delete node when tree root is None")
            return
        if node is None:
            return  # allow passing None just for type checking simplicity
        # NOTE: Could verify that node is in tree.
        self.root = self.root.delete(node)


def main() -> None:
    # shuffled [1, 10]
    vs = list(range(1, 11))
    random.shuffle(vs)
    print("original:     ", vs)

    # build into BST
    tree = BST()
    [tree.insert(v) for v in vs]

    # traverse
    print("BST traversal:", tree.traverse())
    print()

    # search
    print("BST search")
    print("1 in tree:    ", tree.search(1))
    print("7 in tree:    ", tree.search(7))
    print("10 in tree:   ", tree.search(10))
    print("0 in tree:    ", tree.search(0))
    print("-5 in tree:   ", tree.search(-5))
    print("53 in tree:   ", tree.search(53))
    print()

    print("BST Min/max")
    print("minimum:", tree.minimum())
    print("maximum:", tree.maximum())
    print()

    print("BST pred")
    print("5's predecessor:", tree.search(5).predecessor())  # type: ignore
    print("9's predecessor:", tree.search(9).predecessor())  # type: ignore
    print("1's predecessor:", tree.search(1).predecessor())  # type: ignore
    print("10's predecessor:", tree.search(10).predecessor())  # type: ignore
    print()

    print("BST suc")
    print("5's successor:", tree.search(5).successor())  # type: ignore
    print("9's successor:", tree.search(9).successor())  # type: ignore
    print("1's successor:", tree.search(1).successor())  # type: ignore
    print("10's successor:", tree.search(10).successor())  # type: ignore
    print()

    print("BST delete")
    print("root:", tree.root)
    tree.delete(tree.root)
    print("new root:", tree.root)
    print("traversal:", tree.traverse())


if __name__ == "__main__":
    main()
