"""Super basic BST, no balancing, just to get the BST flavor.

Unfinished: deletion!

Style is weird, functional-ish helpers.
"""

import random
from typing import Optional


def _insert(
    subtree: Optional["BinaryTreeNode"], new: "BinaryTreeNode"
) -> "BinaryTreeNode":
    """Returns subtree with new inserted. This might just be new."""
    # if no subtree, new becomes the subtree
    if subtree is None:
        return new

    # equal; shouldn't happen
    if subtree.value == new.value:
        print("Error: assuming unique values. Not inserting.")
        return subtree

    # left
    if new.value < subtree.value:
        subtree.left = _insert(subtree.left, new)
        subtree.left.parent = subtree
    else:
        # right
        subtree.right = _insert(subtree.right, new)
        subtree.right.parent = subtree

    return subtree


def _traverse(subtree: Optional["BinaryTreeNode"]):
    """Returns list of sorted values at and below subtree"""
    if subtree is None:
        return []

    return [
        *_traverse(subtree.left),
        subtree.value,
        *_traverse(subtree.right),
    ]


def _search(subtree: Optional["BinaryTreeNode"], want: int) -> bool:
    """Returns whether want is in subtree"""
    if subtree is None:
        return False
    if subtree.value == want:
        return True
    if want < subtree.value:
        return _search(subtree.left, want)
    else:
        return _search(subtree.right, want)


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


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value: int):
        self.root = _insert(
            self.root, BinaryTreeNode(value, None, None, None)
        )

    def traverse(self):
        return _traverse(self.root)

    def search(self, want: int):
        return _search(self.root, want)

    # deletion: complicated! involves
    # - successor (or predecessor) computation
    # - ~3 cases for replacements, plus 2 sub-cases
    #
    # not sure whether I'll implement.


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

    # search
    print("BST traversal:", tree.traverse())
    print("1 in tree:    ", tree.search(1))
    print("7 in tree:    ", tree.search(7))
    print("10 in tree:   ", tree.search(10))
    print("0 in tree:    ", tree.search(0))
    print("-5 in tree:   ", tree.search(-5))
    print("53 in tree:   ", tree.search(53))


if __name__ == "__main__":
    main()
