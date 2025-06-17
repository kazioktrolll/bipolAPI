import math


def best_factor_pair(n: int) -> tuple[int, int]:
    """Gets two factors of n or lower, that are as close to each other as possible.
    No idea how it works, I don't care, chat made it, and it seems to work fine."""
    best_a, best_b = 1, n  # start with the worst case
    min_diff = abs(best_a - best_b)
    max_product = best_a * best_b

    for a in range(1, int(math.sqrt(n)) + 1):
        b = n // a
        product = a * b
        diff = abs(a - b)

        if product <= n:
            if (diff < min_diff) or (diff == min_diff and product > max_product):
                best_a, best_b = a, b
                min_diff = diff
                max_product = product

    return best_a, best_b

def distribute_units(total_units: int, weights: list[float]) -> list[int]:
    """Returns a distribution of given number of units, according to given weights."""
    total_weight = sum(weights)
    ideal_allocations = [w / total_weight * total_units for w in weights]

    allocations = [int(x) for x in ideal_allocations]
    remainders = [(i, ideal_allocations[i] - allocations[i]) for i in range(len(weights))]

    # Calculate how many units remain to be distributed
    remaining = total_units - sum(allocations)

    # Distribute remaining units to entries with largest remainders
    remainders.sort(key=lambda x: -x[1])  # sort descending by remainder
    for i in range(remaining):
        allocations[remainders[i][0]] += 1

    return allocations

def sort_loop(points):
    cx = sum(x for x, y in points) / len(points)
    cy = sum(y for x, y in points) / len(points)

    def angle(p):
        x, y = p
        return math.atan2(y - cy, x - cx)

    # Sort counterclockwise by angle
    sorted_points = sorted(points, key=angle)

    # Rotate so it starts from point with max x
    max_x_index = max(range(len(sorted_points)), key=lambda i: sorted_points[i][0])
    return sorted_points[max_x_index:] + sorted_points[:max_x_index]
