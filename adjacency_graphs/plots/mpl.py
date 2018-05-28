import matplotlib.pyplot as plt
import pysal as ps
from matplotlib.collections import LineCollection
from pysal.contrib.viz import mapping as maps
import numpy as np

from bokeh.models import HoverTool
from bokeh.plotting import figure, show, output_file, ColumnDataSource


def visualize_adjacency_graph(mggg_graph, bokeh_graph=False, out_dir=None):
    ''' Visualize an adjacency graph
        Input: 
            mggg_graph (Graph): A graph object from adjacency_graphs.algorithms
            out_dir (string, optional): Path to the output file. If none provided,
                                        no file will be created
        Output:
            fig (matplotlib.pyplot): An object which can be plotted
    '''
    # open the file and obtain pysal geometries
    shp = mggg_graph.loaded_geodata
    # setting up matplot figure
    fig = plt.figure(figsize=(9, 9))
    fig.set_facecolor('white')
    base = maps.map_poly_shp(shp)
    base.set_linewidth(0.75)
    base.set_facecolor('none')
    base.set_edgecolor('0.8')

    # Build a dictionary to associate geoid and index.
    data = mggg_graph.shape_df
    gti = {}
    for index, row in data.iterrows():
        gti[row[mggg_graph.id_column]] = index
    # graph contains polygons matched to their neighbors, uses polygon identifiers
    graph = mggg_graph.neighbors
    # obtain the centroids of polygons

    polygon_centroids = {x: y.centroid for x, y in enumerate(shp)}

    if bokeh_graph == False:
        edge_list = [(polygon_centroids[gti[poly1]],
                      polygon_centroids[gti[poly2]]) for poly1, neighbors in graph.items()
                     for poly2 in neighbors]

        edge_list = LineCollection(edge_list)
        edge_list.set_linewidth(0.20)
        ax = maps.setup_ax([base, edge_list], [shp.bbox, shp.bbox])
        fig.add_axes(ax)

        # save your output
        if(out_dir is not None):
            savefig(out_dir)
        return fig
    else:
        edge_list_bokeh_x = [[polygon_centroids[gti[poly1]][0],
                            polygon_centroids[gti[poly2]][0]] 
                           for poly1, neighbors in graph.items()
                           for poly2 in neighbors]
        edge_list_bokeh_y = [[polygon_centroids[gti[poly1]][1],
                            polygon_centroids[gti[poly2]][1]] 
                           for poly1, neighbors in graph.items()
                           for poly2 in neighbors]
        
        lons, lats = gpd_bokeh(mggg_graph.shape_df)
        source = ColumnDataSource(data=dict(
                                    x=lons,
                                    y=lats,
                                    #color=colors,
                                    name=mggg_graph.shape_df.NAME
                                    #rate=HR90
                                ))

        TOOLS = "pan, wheel_zoom, box_zoom, reset, hover, save"
        p = figure(title="Adjecency Graph", tools=TOOLS,
                  plot_width=900, plot_height=900)

        p.patches('x', 'y', source=source,
                 fill_alpha=0.7, color='white',
                 line_color='black', line_width=0.5)

        hover = p.select_one(HoverTool)
        hover.point_policy = 'follow_mouse'
        hover.tooltips = [
            ("Name", "@name"),
            ("(Long, Lat)", "($x, $y)"),
        ]



        p.multi_line(edge_list_bokeh_x, edge_list_bokeh_y , line_width=1)

        output_file("adjancency.html", title="Adjacency Graph")
        show(p)


def gpd_bokeh(df):
    """Convert geometries from geopandas to bokeh format"""
    nan = float('nan')
    lons = []
    lats = []
    for i,shape in enumerate(df.geometry):
        #print('yes')  

        xy = np.array(list(shape.parts[0]))
        xs = xy[:,0].tolist()
        ys = xy[:,1].tolist()
        lons.append(xs)
        lats.append(ys) 

    return lons,lats
