r"""Minimal generic binary tree (node) used in both DFS and BFS.

TreeNode.build() builds an array from a complete binary tree
representation. `None`s are fine, just not as parents.
Using 0-based indexing.

           0
        /     \
      1          2
    /  \       /   \
   3    4     5     6
  / \  / \   / \   / \
 7  8 9 10  11 12 13 14

node i,'s children are:
    left: i*2 + 1
    right: i*2 + 2
"""

from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class TreeNode(Generic[T]):
    __slots__ = ("val", "left", "right")

    def __init__(
        self,
        val: Optional[T] = None,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        l = self.left.val if self.left is not None else "None"
        r = self.right.val if self.right is not None else "None"
        return f"TreeNode({self.val}, L={l}, R={r})"

    @staticmethod
    def build(complete: list[Optional[T]]) -> "TreeNode[T]":
        """Returns root or errors if not possible (just to minimize None checks)."""
        if len(complete) == 0 or complete[0] is None:
            raise ValueError(f"Must pass root. Complete was: {complete}")

        root = TreeNode(complete[0])
        flat_nodes: list[Optional["TreeNode[T]"]] = [None] * len(complete)
        for i, val in enumerate(complete):
            if i == 0:
                flat_nodes[0] = root
                continue
            if val is None:
                continue
            parent_idx = (i - 1) // 2
            parent = flat_nodes[parent_idx]
            if parent is None:
                raise ValueError(
                    f"Node {i} ({val})'s parent {parent_idx} must exist, but was None"
                )
            node = TreeNode(val=val)
            if (parent_idx * 2) + 1 == i:
                parent.left = node
            else:
                assert (parent_idx * 2) + 2 == i
                parent.right = node
            flat_nodes[i] = node
        return root


def main() -> None:
    root = TreeNode.build(list(range(15)))
    print("root:", root)


if __name__ == "__main__":
    main()
