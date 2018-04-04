import collections
import pysal as ps
from adjacency_graphs.utils import create_polymap
from adjacency_graphs import MgggGraph
 """ testtesttest"""

def _twostep(polymap):
    """ Set the self.neighbors
    """
    vertices = collections.defaultdict(set)
    for i, s in polymap.items():
        newvertices = s.vertices[:-1]
        for v in newvertices:
            vertices[v].add(i)

    w = collections.defaultdict(set)
    for neighbors in vertices.values():
        for neighbor in neighbors:
            w[neighbor] = w[neighbor] | neighbors
    return w


def TwoStepGraph(shp_path, id_column):
    """ Take in a path to a shapefile and create a graph.
        Analysis of adjacency is done with the two-step
        algorithm defined in
        http://conference.scipy.org/proceedings/scipy2014/laura.html

        Input:
            shp_path (string): A path /path/to/shapefile.shp as a string.
            id_column (string): The column on which create vertices.

        Output:
            graph (MgggGraph): See adjacency_graphs/mggg_graph for details.

    """

    data = ps.pdio.read_files(shp_path)
    data['CENTROID_XCOORDINATES'] = data.apply(
        lambda x: x['geometry'].centroid[0], 1
    )
    data['CENTROID_YCOORDINATES'] = data.apply(
        lambda x: x['geometry'].centroid[1], 1
    )

    loaded_geodata = ps.open(shp_path)
    loaded_polymap = create_polymap(shp_path,
                                    loaded_geodata,
                                    id_column)
    neighbors = _twostep(loaded_polymap)
    return MgggGraph(shp_path=shp_path,
                     id_column=id_column,
                     shape_df=data,
                     loaded_geodata=loaded_geodata,
                     loaded_polymap=loaded_polymap,
                     neighbors=neighbors)
