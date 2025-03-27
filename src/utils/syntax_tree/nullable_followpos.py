def compute_nullable_first_last(node):
    if node.is_leaf():
        node.nullable = (node.value == 'ε')
        return

    if node.value == '|':
        compute_nullable_first_last(node.left)
        compute_nullable_first_last(node.right)
        node.nullable = node.left.nullable or node.right.nullable
        node.firstpos = node.left.firstpos | node.right.firstpos
        node.lastpos = node.left.lastpos | node.right.lastpos

    elif node.value == '.':
        compute_nullable_first_last(node.left)
        compute_nullable_first_last(node.right)
        node.nullable = node.left.nullable and node.right.nullable
        if node.left.nullable:
            node.firstpos = node.left.firstpos | node.right.firstpos
        else:
            node.firstpos = node.left.firstpos
        if node.right.nullable:
            node.lastpos = node.left.lastpos | node.right.lastpos
        else:
            node.lastpos = node.right.lastpos

    elif node.value == '*':
        compute_nullable_first_last(node.left)
        node.nullable = True
        node.firstpos = node.left.firstpos
        node.lastpos = node.left.lastpos

    elif node.value == '+':
        compute_nullable_first_last(node.left)
        node.nullable = node.left.nullable
        node.firstpos = node.left.firstpos
        node.lastpos = node.left.lastpos

    elif node.value == '?':
        compute_nullable_first_last(node.left)
        node.nullable = True
        node.firstpos = node.left.firstpos
        node.lastpos = node.left.lastpos


def compute_followpos(node, followpos):
    if node is None:
        return

    if node.value == '.':
        for i in node.left.lastpos:
            followpos[i] |= node.right.firstpos

    elif node.value in {'*', '+'}:
        for i in node.lastpos:
            followpos[i] |= node.firstpos

    compute_followpos(node.left, followpos)
    compute_followpos(node.right, followpos)
