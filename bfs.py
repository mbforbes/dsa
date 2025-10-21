r"""BFS: Breadth-first search.

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

BFS:
- traverses in complete-tree-as-array order (top to bottom by level, and left to right
  within each level)

BFS, interestingly:
- no recursion: doesn't have a natural recursive implementation
- no order: doesn't really have different order traversals (could do right before left,
            which reverses the within-level order)
"""

from collections import deque
from typing import Optional

from binary_tree import TreeNode, T


def bfs(
    root: TreeNode[T],
    results: Optional[list[Optional[T]]] = None,
) -> list[Optional[T]]:
    """BFS, breadth-first, iterative"""
    results = []
    queue: deque[Optional[TreeNode]] = deque([root])
    while len(queue) > 0:
        node = queue.popleft()
        if node is None:
            continue
        results.append(node.val)
        queue.append(node.left)
        queue.append(node.right)

    return results


def main() -> None:
    root = TreeNode.build(list(range(15)))

    # BFS - breadth-first
    print("BFS:", bfs(root))


if __name__ == "__main__":
    main()
