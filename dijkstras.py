import heapq
from typing import Optional

import networkx as nx

from graph_utils import (
    GraphVisualizerSpec,
    GraphVisualizer,
    DummyGraphVisualizer,
    create_fixed_graph,
    create_random_graph,
)

GREEN = "#22C55E"
DARK_GREEN = "#15803d"
BLUE = "#22D3EE"


def get_path(previous: dict[str, Optional[str]], end: str) -> list[str]:
    rev_path = []
    cur = end
    while cur is not None:
        rev_path.append(cur)
        cur = previous[cur]
    return list(reversed(rev_path))


class HeapNode:
    __slots__ = ["name", "dist"]

    def __init__(self, name: str, dist: float):
        self.name = name
        self.dist = dist

    def __lt__(self, other: "HeapNode"):
        """Only comparison required to support heap operations."""
        return self.dist < other.dist


def dijkstra(
    graph: nx.Graph[str],
    start: str,
    end: str,
    visualizer: GraphVisualizerSpec,
    output_dir: str,
):
    """
    Dijkstra's algorithm with visualization.

    Args:
        graph: The graph to search
        start: Starting node
        end: Goal node
        visualizer: GraphVisualizer instance for rendering
        output_dir: Directory to save visualization frames
    """
    distances: dict[str, float] = {start: 0}
    previous: dict[str, Optional[str]] = {start: None}
    # python's heapq doesn't support lookup by index or (publicly) decrease-key. but we
    # can add duplicates when a shorter path is found, and it will be popped first.
    # ignore any already-popped nodes later on. O(E) <= O(V^2) heap size with
    # duplicates, but as heap operations are log(n), log(V^2) = 2log(V). so operating on
    # a heap with V^2 entries is still big-O like operating on V entries, because log
    # dominates the polynomial so hard.
    heap: list[HeapNode] = [HeapNode(start, 0)]
    finished: set[str] = set()
    while len(heap) > 0:
        heap_node = heapq.heappop(heap)
        node, dist = heap_node.name, heap_node.dist

        # allowing heap duplicates for lowering key (see above)
        if node in finished:
            continue

        assert dist == distances[node]
        finished.add(node)

        # draw node
        visualizer.save_frame(
            output_dir=output_dir,
            arrows=[(n, p) for n, p in previous.items() if p is not None],
            prefix="dijkstra",
            node_colors={**{n: DARK_GREEN for n in finished}, node: GREEN},
            node_labels={
                node: f"{node}\n{distances[node] if node in distances else ''}"
                for node in graph.nodes()
            },
            edge_colors={
                (n, p): DARK_GREEN
                for n, p in previous.items()
                if p is not None and n in finished and p in finished
            },
            title=f"Considering: {node}",
        )

        # optional: stop early once end found
        if node == end:
            break

        for neighbor, edge in graph[node].items():
            # we don't need to consider paths to neighbors if they're already
            # finished because we're guaranteed to already have the shortest
            # path to them.
            if neighbor in finished:
                continue
            weight = edge["weight"]
            neighbor_dist = dist + weight

            visualizer.save_frame(
                output_dir=output_dir,
                prefix="dijkstra",
                node_colors={
                    neighbor: BLUE,
                    **{n: DARK_GREEN for n in finished},
                    node: GREEN,
                },
                arrows=[(n, p) for n, p in previous.items() if p is not None]
                + [(node, neighbor)],
                edge_colors={
                    **{
                        (n, p): DARK_GREEN
                        for n, p in previous.items()
                        if p is not None and n in finished and p in finished
                    },
                    **{(node, neighbor): BLUE},
                },
                node_labels={
                    node: f"{node}\n{distances[node] if node in distances else ''}"
                    for node in graph.nodes()
                },
                edge_labels={
                    (
                        node,
                        neighbor,
                    ): f"is {neighbor_dist} < {distances[neighbor]} ?"
                    if neighbor in distances
                    else f"new: {neighbor_dist}"
                },
                title=f"Considering: {node} → {neighbor}",
            )

            if (
                neighbor not in distances
                or neighbor_dist < distances[neighbor]
            ):
                distances[neighbor] = neighbor_dist
                previous[neighbor] = node
                heapq.heappush(heap, HeapNode(neighbor, neighbor_dist))

        display = sorted(
            (
                (n, (str(d) if d != float("inf") else "∞"), d)
                for n, d in distances.items()
                if n not in finished
            ),
            key=lambda i: i[2],
        )

        visualizer.save_frame(
            output_dir=output_dir,
            prefix="dijkstra",
            node_colors={
                **{n: DARK_GREEN for n in finished},
            },
            arrows=[(n, p) for n, p in previous.items() if p is not None],
            edge_colors={
                **{
                    (n, p): DARK_GREEN
                    for n, p in previous.items()
                    if p is not None and n in finished and p in finished
                },
            },
            node_labels={
                node: f"{node}\n{distances[node] if node in distances else ''}"
                for node in graph.nodes()
            },
            edge_labels={},
            title=f"What next? Choose smallest in queue. Available:\n{', '.join([f'({d[0]}: {d[1]})' for d in display])}",
        )

    # Show final shortest path from start to end
    path = get_path(previous, end)
    arrows = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    visualizer.save_frame(
        output_dir=output_dir,
        prefix="dijkstra",
        node_colors={n: GREEN for n in path},
        arrows=arrows,
        edge_colors={(p, n): GREEN for p, n in arrows},
        title="Final path found",
    )

    return distances, previous


def main() -> None:
    seed = 5

    # Choose graph
    graph, name = create_fixed_graph(), "example"
    # graph, name = (
    #     create_random_graph(num_nodes=7, seed=seed),
    #     f"random-{seed}",
    # )

    # viz or not
    # viz = GraphVisualizer(graph, name, layout="spring")
    viz = DummyGraphVisualizer(graph, name, layout="spring")
    output_dir = "output/dijkstra/"

    start = list(graph.nodes())[0]
    end = "E" if name == "example" else list(graph.nodes())[-1]
    distances, previous = dijkstra(
        graph, start, end, viz, output_dir=output_dir
    )
    print("Distances:", distances)
    print("Previous:", previous)
    print("Path:", get_path(previous, end))
    if isinstance(viz, GraphVisualizer):
        print(f"Frames for {name} graph saved to: {output_dir}")


if __name__ == "__main__":
    main()
