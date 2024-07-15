from fire import Fire
from pyvis.network import Network

from . import URLGraph


def resize(nodes, weights):
    for n in nodes:
        w = weights[n["label"]]
        n["size"] = w
        n["font"] = {"size": w / 2 + 2}


def visualize(graph, weights=None, **kwargs):
    nt = Network(directed=True, **kwargs)
    nt.from_nx(graph)

    if weights:
        resize(nt.nodes, weights)

    nt.repulsion()
    nt.show("urlgraph.html", notebook=False)


def main(*roots, time=10, workers=20):
    g = URLGraph()

    for root in roots:
        g.add(root)

    g.build(time, workers)
    visualize(g.graph, weights=g.weights)


if __name__ == "__main__":
    Fire(main)
