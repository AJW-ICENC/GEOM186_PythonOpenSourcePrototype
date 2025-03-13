
import geopandas as gpd
from shapely.geometry import Polygon

def compare_polygons(poly1, poly2):
    # Ensure both geometries are Polygons
    if not isinstance(poly1, Polygon) or not isinstance(poly2, Polygon):
        raise ValueError("Both geometries must be Polygons")

    # Extract exterior coordinates from both polygons
    coords1 = list(poly1.exterior.coords)
    coords2 = list(poly2.exterior.coords)

    # Find the length of the shorter polygon
    min_length = min(len(coords1), len(coords2))

    # Compare nodes and identify differences
    differences = []
    for i in range(min_length):
        if coords1[i] != coords2[i]:
            differences.append((i, coords1[i], coords2[i]))

    # If one polygon is longer, add the remaining nodes as differences
    if len(coords1) > min_length:
        for i in range(min_length, len(coords1)):
            differences.append((i, coords1[i], None))
    elif len(coords2) > min_length:
        for i in range(min_length, len(coords2)):
            differences.append((i, None, coords2[i]))

    return differences

# Example usage
poly1 = Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
poly2 = Polygon([(0, 0), (1, 1), (2, 0), (0, 0)])

differences = compare_polygons(poly1, poly2)
print("Differences (index, poly1 node, poly2 node):")
for diff in differences:
    print(diff)