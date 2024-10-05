import networkx as nx
from typing import TypeAlias, Any, Tuple
import matplotlib.pyplot as plt
import osmnx as ox
import pickle
import buses
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker
from dataclasses import dataclass
from itertools import pairwise


@dataclass
class Parada:
    nom: str
    coordenades: tuple[int, int]


@dataclass
class Bus:
    linia: str
    longitud: int
    parada_anterior: Any
    proxima_parada: Any


@dataclass
class Cruïlla:
    identificador: int
    coordenades: tuple[int, int]


@dataclass
class Carrer:
    nom: str
    longitud: int
    punt1: Any
    punt2: Any


CityGraph: TypeAlias = nx.Graph
OsmnxGraph: TypeAlias = nx.MultiDiGraph
BusesGraph: TypeAlias = nx.Graph
Path: list[int] = list()
Coord: TypeAlias = tuple[float, float]   # (latitude, longitude)


def get_osmnx_graph() -> OsmnxGraph:
    """Obté el graf dels carrers de Bracelona"""
    return ox.graph_from_place('Barcelona, Spain')


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    """Guarda el graf g al fitxer filename"""

    pickle_out = open(filename, "wb")  # Guarda el graf en l'arxiu graf_carrers
    pickle.dump(g, pickle_out)
    pickle_out.close()


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    """Retorna el graf guardat al fitxer filename"""
    pickle_in = open(filename, "rb")
    graf = pickle.load(pickle_in)

    return graf


def get_nodes_cruïlla(g1: OsmnxGraph, graf_ciutat: CityGraph) -> None:
    """Agrega els nodes dels carrers de barcelona al
    graf ciutat amb els atributs de tipus Cruïlla"""

    for node in g1.nodes.data():

        identificador, atributs = node
        coordenades_cruïlla = (atributs['y'], atributs['x'])
        atributs_cruïlla = Cruïlla(identificador, coordenades=coordenades_cruïlla)
        graf_ciutat.add_node(identificador, Cruïlla=atributs_cruïlla)


def get_edges_carrer(g1: OsmnxGraph, graf_ciutat: CityGraph) -> None:
    """Agrega totes les arestes del graf de
    barcelona al graf ciutat amb el tipus Carrer"""
    for aresta in g1.edges.data():

        node1, node2, atributs_aresta = aresta

        nom = atributs_aresta.get('name')

        distancia = atributs_aresta.get('length')
        velocitat_caminant = 5
        time = distancia/velocitat_caminant

        aresta = Carrer(nom, distancia, node1, node2)

        graf_ciutat.add_edge(node1, node2, Carrer=aresta, time=time)


def connectar_parada_cruïlla(g: CityGraph, g1: OsmnxGraph) -> None:
    """Connecta cada node tipus Parada amb el node Cruïlla més proper"""

    X: list[int] = list()
    Y: list[int] = list()

    atributs_parada = nx.get_node_attributes(g, 'Parada')

    for parada in atributs_parada.keys():
        x, y = atributs_parada[parada].coordenades
        X.append(x)
        Y.append(y)

    id_cruilles = ox.nearest_nodes(g1, Y, X, return_dist=False)
    paradacruilla = list(zip(atributs_parada.keys(), id_cruilles))

    for aresta in paradacruilla:
        node1, node2 = aresta
        g.add_edge(node1, node2)


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    """Retorna un graf fusió de graf de
    carrers de barcelona i el graf de buses"""

    graf_ciutat: CityGraph = CityGraph()

    get_nodes_cruïlla(g1, graf_ciutat)
    get_edges_carrer(g1, graf_ciutat)

    graf_ciutat = nx.compose(graf_ciutat, g2)

    connectar_parada_cruïlla(graf_ciutat, g1)

    return graf_ciutat


def show(g: CityGraph) -> None:
    """Mostra el citygraph visualment"""

    plt.figure(figsize=(200, 200))

    atributs_nodes_parada = nx.get_node_attributes(g, 'Parada')
    pos = {node: atributs_nodes_parada[node].coordenades for node in atributs_nodes_parada}

    atributs_nodes_cruïlla = nx.get_node_attributes(g, 'Cruïlla')

    for node in atributs_nodes_cruïlla:
        pos[node] = atributs_nodes_cruïlla[node].coordenades

    nx.draw(g, pos, node_color='lightblue', node_size=5, edge_color='gray', width=1, font_size=5)
    plt.interactive(True)
    plt.show()
    plt.pause(1000)


def plot(g: CityGraph, filename: str) -> None:
    """Desa el citygraph com una imatge amb el mapa
    de la cuitat de fons en larxiu filename"""

    mapa_barcelona = StaticMap(1920, 1080)

    atributs_nodes_parada = nx.get_node_attributes(g, 'Parada')
    coordenades = {node: atributs_nodes_parada[node].coordenades for node in atributs_nodes_parada}

    atributs_nodes_cruïlla = nx.get_node_attributes(g, 'Cruïlla')

    for node in atributs_nodes_cruïlla:
        coordenades[node] = atributs_nodes_cruïlla[node].coordenades

    for aresta in g.edges:
        node1 = aresta[0]
        node2 = aresta[1]

        lat1, lon1 = coordenades[node1]
        coordenades1 = (lon1, lat1)
        lat2, lon2 = coordenades[node2]
        coordenades2 = (lon2, lat2)

        mapa_barcelona.add_line(Line([coordenades1, coordenades2], 'red', 1))

    image = mapa_barcelona.render()

    plt.imshow(image)
    plt.axis('off')
    plt.show()

    image.save(filename)


def find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> Path:
    """Retorna una llista tipus Path que mostra el camí entre les coordenades
    src i dst. Retorna una llista dels nodes ordenats que pertanyen al camí"""

    src_y, src_x = src
    dst_y, dst_x = dst

    node_src = ox.distance.nearest_nodes(ox_g, src_x, src_y)
    node_dst = ox.distance.nearest_nodes(ox_g, dst_x, dst_y)

    path = ox.distance.shortest_path(g, node_src, node_dst, cpus=None, weight='time')

    return path


def plot_path(g: CityGraph, p: Path, filename: str) -> None:
    """Mostra el camí p en l'arxiu filename, demanera que les
    parts a peu es mostren en vermell i els trossos en bus es mostres blau"""

    mapa_barcelona = StaticMap(1920, 1080)

    for node1, node2 in pairwise(p):

        aresta = g[node1][node2]

        atributs1 = g.nodes[node1]
        atributs2 = g.nodes[node2]

        if 'Cruïlla' in atributs1:
            lat1, lon1 = atributs1['Cruïlla'].coordenades
            coord1 = (lon1, lat1)
            mapa_barcelona.add_marker(CircleMarker(coord1, 'red', 10))
        else:
            lat1, lon1 = atributs1['Parada'].coordenades
            coord1 = (lon1, lat1)
            mapa_barcelona.add_marker(CircleMarker(coord1, 'blue', 10))

        if 'Cruïlla' in atributs2:
            lat2, lon2 = atributs2['Cruïlla'].coordenades
            coord2 = (lon2, lat2)
            mapa_barcelona.add_marker(CircleMarker(coord2, 'red', 10))
        else:
            lat2, lon2 = atributs2['Parada'].coordenades
            coord2 = (lon2, lat2)
            mapa_barcelona.add_marker(CircleMarker(coord2, 'blue', 10))

        if 'Carrer' in aresta:
            mapa_barcelona.add_line(Line([coord1, coord2], 'red', 5))
        else:
            mapa_barcelona.add_line(Line([coord1, coord2], 'blue', 5))

    image = mapa_barcelona.render()

    plt.imshow(image)
    plt.axis('off')
    plt.show()

    image.save(filename)
