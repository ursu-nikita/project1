"""Dependency-first loading order and explicit cycle diagnostics."""


def loading_order(graph):
    """Return DFS postorder and back edges using an explicit stack."""
    colors = {}
    order = []
    cycles = []
    stack = [(graph.root, False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            colors[node] = 2
            order.append(node)
            continue
        color = colors.get(node, 0)
        if color:
            continue
        colors[node] = 1
        stack.append((node, True))
        for child in reversed(graph.edges[node]):
            child_color = colors.get(child, 0)
            if child_color == 1:
                cycles.append((node, child))
            elif child_color == 0:
                stack.append((child, False))
    return order, cycles
