import os
import random
from typing import Optional, Literal

import matplotlib.pyplot as plt
import networkx as nx

NODE_SIZE = 800


class GraphVisualizer:
    """A simple API for visualizing graph algorithm steps."""

    __slots__ = ["graph", "name", "layout", "pos", "figure_count"]

    def __init__(
        self,
        graph: nx.Graph,
        name: str,
        layout: Literal["spring", "circular", "kamada"] = "kamada",
    ):
        self.graph = graph
        self.name = name
        self.layout = layout
        self.pos = self._compute_layout(layout)
        self.figure_count = 0

    def _compute_layout(self, layout):
        """Compute node positions."""
        if layout == "spring":
            return nx.spring_layout(self.graph, seed=42)
        elif layout == "circular":
            return nx.circular_layout(self.graph)
        elif layout == "kamada":
            return nx.kamada_kawai_layout(self.graph)
        else:
            raise ValueError(f"Unsupported layout: {layout}")

    def draw(
        self,
        node_colors: dict[str, str] = {},
        edge_colors: dict[tuple[str, str], str] = {},
        node_labels: dict[str, str] = {},
        edge_labels: dict[tuple[str, str], str] = {},
        arrows: Optional[list[tuple[str, str]]] = None,
        title: str = "",
        save_path: Optional[str] = None,
    ):
        """
        Draw the graph with custom colors and labels.

        Args:
            node_colors: dict mapping node -> color (default: 'lightgray')
            edge_colors: dict mapping (node1, node2) -> color (default: 'black')
            node_labels: dict mapping node -> label text (default: node name)
            edge_labels: dict mapping (node1, node2) -> label text (default: weight)
            arrows: list of (source, target) tuples to draw as directed edges
            title: Plot title
            save_path: If provided, save to this path instead of showing
        """
        plt.figure(figsize=(6, 4))
        # plt.xlim(
        #     [
        #         min(x for x, y in self.pos.values()) - 0.1,
        #         max(x for x, y in self.pos.values()) + 0.1,
        #     ]
        # )
        # plt.ylim(
        #     [
        #         min(y for x, y in self.pos.values()) - 0.1,
        #         max(y for x, y in self.pos.values()) + 0.1,
        #     ]
        # )

        # Default colors
        default_node_color = "lightgray"
        default_edge_color = "lightgray"

        # Prepare node colors
        node_color_list = [
            node_colors.get(node, default_node_color)
            for node in self.graph.nodes()
        ]

        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph,
            self.pos,
            node_color=node_color_list,
            node_size=NODE_SIZE,
        )

        # Draw edges (non-arrows)
        arrow_set = set(arrows) if arrows else set()
        regular_edges = [
            (u, v)
            for u, v in self.graph.edges()
            if (u, v) not in arrow_set and (v, u) not in arrow_set
        ]

        if regular_edges:
            edge_color_list = [
                edge_colors.get(
                    (u, v), edge_colors.get((v, u), default_edge_color)
                )
                for u, v in regular_edges
            ]
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                edgelist=regular_edges,
                edge_color=edge_color_list,
                width=2,
                node_size=NODE_SIZE,
            )

        # Draw arrows
        if arrows:
            arrow_color_list = [
                edge_colors.get((u, v), default_edge_color) for u, v in arrows
            ]
            nx.draw_networkx_edges(
                self.graph,
                self.pos,
                edgelist=arrows,
                edge_color=arrow_color_list,
                width=2,
                arrows=True,
                arrowsize=20,
                arrowstyle="->",
                node_size=NODE_SIZE,
            )

        # Draw node labels
        if len(node_labels) == 0:
            node_labels = {node: str(node) for node in self.graph.nodes()}
        nx.draw_networkx_labels(
            self.graph,
            self.pos,
            node_labels,
            font_size=11,
            font_weight="bold",
        )

        # Draw edge labels
        # if len(edge_labels) == 0:
        #     edge_labels = nx.get_edge_attributes(self.graph, "weight")
        edge_labels = {
            **nx.get_edge_attributes(self.graph, "weight"),
            **edge_labels,
        }
        nx.draw_networkx_edge_labels(
            self.graph,
            self.pos,
            edge_labels,
            font_size=9,
            node_size=NODE_SIZE,
        )

        plt.title(title + "\n" if "\n" not in title else title, fontsize=16)
        ax = plt.gca()
        ax.margins(0.10)  # Adds 10% padding on all sides
        plt.axis("off")
        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            plt.close()
        else:
            plt.show()

    def save_frame(self, output_dir: str, prefix: str, **kwargs):
        """Save a frame with automatic numbering."""
        filename = (
            f"{prefix}_{self.name}_{self.layout}_{self.figure_count:04d}.png"
        )
        filepath = os.path.join(output_dir, filename)
        self.figure_count += 1
        self.draw(save_path=filepath, **kwargs)
        return filepath


def create_fixed_graph() -> nx.Graph:
    """Create a fixed graph for consistent testing."""
    G = nx.Graph()
    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
        ("D", "F", 6),
        ("E", "F", 3),
        ("E", "G", 7),
    ]
    G.add_weighted_edges_from(edges)
    return G


def create_random_graph(num_nodes: int = 10, seed: int = 42) -> nx.Graph:
    """Create a random connected graph."""
    random.seed(seed)
    G = nx.Graph()

    # Create nodes
    nodes = [chr(65 + i) for i in range(num_nodes)]  # A, B, C, ...
    G.add_nodes_from(nodes)

    # Ensure connectivity: create a spanning tree
    unconnected = nodes[1:]
    connected = [nodes[0]]

    while unconnected:
        # Connect a random unconnected node to a random connected node
        u = random.choice(connected)
        v = unconnected.pop(random.randint(0, len(unconnected) - 1))
        weight = random.randint(1, 9)
        G.add_edge(u, v, weight=weight)
        connected.append(v)

    # Add additional random edges (1-3 per node)
    for node in nodes:
        num_extra_edges = random.randint(0, 2)
        for _ in range(num_extra_edges):
            other = random.choice(nodes)
            if other != node and not G.has_edge(node, other):
                weight = random.randint(1, 9)
                G.add_edge(node, other, weight=weight)

    return G
