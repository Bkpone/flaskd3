ROUND_PRECISION = 2


def logical_xor(lhs, rhs):
    return bool(lhs is not None) != bool(rhs is not None)
