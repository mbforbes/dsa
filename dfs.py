r"""DFS: Depth-first search.

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

DFS order traversal use cases:

- pre-order:  renders topologically sorted (for every edge (u,v), u comes before v).
              good for copying tree. also, prefix notation.

- in-order:   renders a BST in sorted order

- post-order: render postfix notation (e.g., if internal operators & leaf values).
              also good for deleting tree (removes children first).
"""

from typing import Literal, Optional

from binary_tree import TreeNode, T

Order = Literal["pre", "in", "post"]
ALL_ORDERS: list[Order] = ["pre", "in", "post"]


def dfs_recursive_v1(
    node: TreeNode[T],
    order: Order,
    results: Optional[list[Optional[T]]] = None,
) -> list[Optional[T]]:
    """DFS, depth-first, recursive, kind of gross v1 mutating implementation

    I passed `results` as mutable state into recursive calls. I think
    this is less elegant than using what's returned by the recursion
    as the result.
    """
    # We default argument None, not [], b/c otherwise the default gets mutated!
    if results is None:
        results = []

    if order == "pre":
        results.append(node.val)

    if node.left is not None:
        # NOTE: No need to assign or extend, because
        # - assign? no, we're passing `results` which gets mutated
        # - extend? no, each node's traversal adds itself, so no need to multi-add
        dfs_recursive_v1(node.left, order, results)

    if order == "in":
        results.append(node.val)

    if node.right is not None:
        dfs_recursive_v1(node.right, order, results)

    if order == "post":
        results.append(node.val)

    return results


def dfs(node: Optional[TreeNode[T]]) -> list[Optional[T]]:
    """DFS, depth-first, minimal pure recursive implementation (pre-order)."""
    if node is None:
        return []
    return [node.val, *dfs(node.left), *dfs(node.right)]


def dfs_recursive(
    node: Optional[TreeNode[T]], order: Order
) -> list[Optional[T]]:
    """DFS, depth-first, any-order recursive implementation."""
    if node is None:
        return []
    return [
        *([node.val] if order == "pre" else []),
        *dfs_recursive(node.left, order),
        *([node.val] if order == "in" else []),
        *dfs_recursive(node.right, order),
        *([node.val] if order == "post" else []),
    ]


def dfs_i(root: TreeNode[T]) -> list[Optional[T]]:
    """DFS, depth-first, minimal iterative implementation (pre-order)"""
    res: list[Optional[T]] = []
    stack: list[Optional[TreeNode[T]]] = [root]
    while len(stack) > 0:
        node = stack.pop()
        if node is None:
            continue
        res.append(node.val)
        stack.append(node.right)
        stack.append(node.left)

    return res


def dfs_iterative(root: TreeNode[T], order: Order) -> list[Optional[T]]:
    """DFS, depth-first, iterative

    we add values back to the stack to control the traversal order. this two-pass
    approach lets us decide explicitly when to extract a node's value.
    """
    results = []
    stack: list[TreeNode[T] | Optional[T]] = [root]
    while len(stack) > 0:
        node_or_value = stack.pop()

        # we allow None to simplify adding vals (Optional[T])
        if node_or_value is None:
            continue

        # if we got a value on the stack, that means we should add it
        # to the results.
        if not isinstance(node_or_value, TreeNode):
            val = node_or_value
            results.append(val)
            continue

        # remember to add things "backwards" because stack will pop latest first
        node = node_or_value
        if order == "post":
            stack.append(node.val)
        if node.right is not None:
            stack.append(node.right)
        if order == "in":
            stack.append(node.val)
        if node.left is not None:
            stack.append(node.left)
        if order == "pre":
            stack.append(node.val)
    return results


def main() -> None:
    root = TreeNode.build(list(range(15)))

    # DFS - depth-first
    for order in ALL_ORDERS:
        recursive_v1 = dfs_recursive_v1(root, order)
        recursive = dfs_recursive(root, order)
        iterative = dfs_iterative(root, order)
        assert recursive_v1 == recursive
        assert recursive == iterative
        print(f"DFS ({order}):", recursive)

    # also check the minimal implementations are correct
    assert dfs(root) == dfs_recursive(root, "pre")
    assert dfs_i(root) == dfs_recursive(root, "pre")


if __name__ == "__main__":
    main()
