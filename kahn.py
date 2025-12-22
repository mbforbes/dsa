"""Kahn's algorithm to topologically sort a DAG.

Common graph representations:
- adjacency list: each node holds their set of edges (a has a->b, a->c)
- adjacency matrix: there's a VxV matrix where (a,b) has an entry for a->b
- incidence matrix: a VxE matrix, where an edge (a,b) has exactly two entries at a and b

NOTE: To avoid the mental overload of using "dependency" vs "dependant" correctly, I'm
going to abuse "child" and "parent" here.

Kahn's pseudocode:
- answer = []
- worklist = all nodes with no parents (incoming edges)
- while worklist isn't empty:
    - pop item a
    - add to answer
    - for all of a's children b in a->b:
        - remove the edge (a, b) from the graph
        - if b has no more parents (incoming edges), add it to worklist
- answer is a topo sort if the graph has no more edges (AKA len(answer) = |V|)
- otherwise, the graph has at least one cycle

Running time: O(|V| + |E|)
Space: O(|V|)
    - (all nodes will end up in answer; worklist OK as mutually exclusive w/ answer)
    - you don't actually need to mutate the graph if you're counting in-degree

Any worklist ordering is valid, because everything in the worklist has no parents. Thus,
stack vs queue vs random (vs ...) may give different answers.

Kahn's requires a few different graph operations:
1. find all nodes with no parents: O(|V|) is fine because outside of loop

But ideally we'd like to do the next two in O(1) time:
2. remove edge from graph
3. lookup whether node has any parents

2. is trivial in any representation (given the right references), but I think 3.
requires an O(|V|) or O(|E|) scan out of the box. We can track additional data to speed
up 3.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class GraphNode:
    name: str
    children: list["GraphNode"]


def make_indegree_and_edges(graph: list[GraphNode]):
    in_degree: defaultdict[str, int] = defaultdict(lambda: 0)
    n_edges = 0
    for node in graph:
        in_degree[node.name] += 0  # just to ensure it's in the graph
        for child in node.children:
            in_degree[child.name] += 1
            n_edges += 1
    return in_degree, n_edges


def kahn(graph: list[GraphNode]) -> Optional[list[GraphNode]]:
    in_degree, n_edges = make_indegree_and_edges(graph)
    topo = []
    worklist = [node for node in graph if in_degree[node.name] == 0]
    while len(worklist) > 0:
        node = worklist.pop()  # or popleft() if deque
        topo.append(node)
        for child in node.children:
            n_edges -= 1
            in_degree[child.name] -= 1
            if in_degree[child.name] == 0:
                worklist.append(child)

    if n_edges == 0:
        return topo  # ordering
    else:
        return None  # graph had cycles


def make_example_graph():
    """
    c  a
    |  ↓
    |  b
    ↘ ↙
     d
    """
    d = GraphNode("d", [])
    b = GraphNode("b", [d])
    c = GraphNode("c", [d])
    a = GraphNode("a", [b])
    return [a, b, c, d]


def main() -> None:
    graph = make_example_graph()
    topo = kahn(graph)
    print("Found topo ordering:")
    if topo is None:
        print("None: graph had cycles")
    else:
        print(", ".join([n.name for n in topo]))


if __name__ == "__main__":
    main()
