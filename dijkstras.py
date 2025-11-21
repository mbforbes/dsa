# import heapq

from typing import Optional

import networkx as nx

from graph_utils import (
    GraphVisualizer,
    create_fixed_graph,
    create_random_graph,
)

GREEN = "#22C55E"
DARK_GREEN = "#15803d"
BLUE = "#22D3EE"


def pop_min(
    distances: dict[str, float], remaining: set[str]
) -> tuple[str, float]:
    min_node = None
    min_dist = float("inf")
    for node in remaining:
        dist = distances[node]
        if dist < min_dist:
            min_node = node
            min_dist = dist
    if min_node is None:
        raise ValueError(f"No node had non-inf dist: {distances}")
    remaining.remove(min_node)
    return min_node, min_dist


def dijkstra(
    graph: nx.Graph[str],
    start: str,
    end: str,
    visualizer: GraphVisualizer,
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
    distances = {
        node: (float("inf") if node != start else 0) for node in graph.nodes()
    }
    previous: dict[str, Optional[str]] = {
        node: None for node in graph.nodes()
    }
    remaining = set(graph.nodes())
    finished = set()
    # TODO: update elements in python's heapq by in-place writes and then sort? but
    # how to lookup by name?
    while len(remaining) > 0:
        node, dist = pop_min(distances, remaining)

        finished.add(node)

        # draw node
        visualizer.save_frame(
            output_dir=output_dir,
            arrows=[(n, p) for n, p in previous.items() if p is not None],
            prefix="dijkstra",
            node_colors={**{n: DARK_GREEN for n in finished}, node: GREEN},
            node_labels={
                node: f"{node}\n{distances[node]}" for node in graph.nodes()
            },
            edge_colors={
                (n, p): DARK_GREEN
                for n, p in previous.items()
                if p is not None and n in finished and p in finished
            },
            title=f"Considering: {node}",
        )

        # stop early once end found
        if node == end:
            break

        for neighbor, edge in graph[node].items():
            # I think we don't need to consider paths to neighbors if they're already
            # finished because we're guaranteed to already have the shortest path
            # to them.
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
                    node: f"{node}\n{distances[node]}"
                    for node in graph.nodes()
                },
                edge_labels={
                    (
                        node,
                        neighbor,
                    ): f"is {neighbor_dist} < {distances[neighbor]} ?"
                },
                title=f"Considering: {node} → {neighbor}",
            )

            if distances[neighbor] > neighbor_dist:
                distances[neighbor] = neighbor_dist
                previous[neighbor] = node

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
                node: f"{node}\n{distances[node]}" for node in graph.nodes()
            },
            edge_labels={},
            title=f"What next? Choose smallest in queue. Available:\n{', '.join([f'({d[0]}: {d[1]})' for d in display])}",
        )

    # Show final path
    rev_path = []
    cur = end
    while cur is not None:
        rev_path.append(cur)
        cur = previous[cur]
    path = list(reversed(rev_path))
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
    # graph, name = create_fixed_graph(), "example"
    graph, name = (
        create_random_graph(num_nodes=7, seed=seed),
        f"random-{seed}",
    )
    viz = GraphVisualizer(graph, name, layout="spring")
    output_dir = "output/dijkstra/"

    start_node = list(graph.nodes())[0]
    end_node = "E" if name == "example" else list(graph.nodes())[-1]
    dijkstra(graph, start_node, end_node, viz, output_dir=output_dir)
    print(f"Frames for {name} graph saved to: {output_dir}")


if __name__ == "__main__":
    main()
