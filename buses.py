import requests
import json
import networkx as nx
from typing import TypeAlias, Any
import matplotlib.pyplot as plt
from staticmap import StaticMap,  Line
from dataclasses import dataclass
from haversine import haversine
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


BusesGraph: TypeAlias = nx.Graph


def get_nodes(Graf: BusesGraph, dades: Any, i: int) -> list[str]:
    """Retorna la llista de parades d'una línia de
    bus concreta i afageix aquestes al graf."""

    llista_nodes: list[str] = list()

    llista_parades = dades['ObtenirDadesAMBResult']['Linies']['Linia'][i]['Parades']['Parada']

    for j in range(len(llista_parades)):

        identificació = llista_parades[j]['CodAMB']
        nom_parada = llista_parades[j]['Nom']
        coordenades_parada = (llista_parades[j]['UTM_X'], llista_parades[j]['UTM_Y'])

        llista_nodes.append(identificació)

        parada = Parada(nom=nom_parada, coordenades=coordenades_parada)

        Graf.add_node(identificació, Parada=parada)

    return llista_nodes


def get_edges(grafo: BusesGraph, llista_nodes: list[str], dades: Any,  i: int) -> None:
    """Donada la llista de nodes(parades) d'una línia concreta,
      retorna la llista d'arestes d'aquesta línia"""

    noma_linia = dades['ObtenirDadesAMBResult']['Linies']['Linia'][i]['Nom']

    for node1, node2 in pairwise(llista_nodes):

        coord1 = grafo.nodes[node1]['Parada'].coordenades
        coord2 = grafo.nodes[node2]['Parada'].coordenades

        distancia = haversine(coord1, coord2)

        velocitat_bus = 12
        time = distancia/velocitat_bus

        aresta = Bus(noma_linia, distancia, node1, node2)

        grafo.add_edge(node1, node2, Bus=aresta, time=time)


def get_buses_graph() -> BusesGraph:
    """Descarrega totes les dades de l'AMB i
    retorna un graf de networkx amb les dades"""
    grafo: BusesGraph = BusesGraph()

    llista_nodes: list[str] = list()

    link = 'https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json'
    page = requests.get(link)
    dades = json.loads(page.content)

    num_linies = len(dades['ObtenirDadesAMBResult']['Linies']['Linia'])

    for i in range(num_linies):

        llista_nodes = get_nodes(grafo, dades, i)
        get_edges(grafo, llista_nodes, dades, i)

    return grafo


def show(g: BusesGraph) -> None:
    """Mostra un graf interactiu amb totes
    les parades i linies de bus de Barcelona (AMB)"""

    atributs_nodes = nx.get_node_attributes(g, 'Parada')
    pos = {node: atributs_nodes[node].coordenades for node in atributs_nodes}

    plt.figure(figsize=(200, 200))
    nx.draw(g, pos, node_color='lightblue', node_size=5, edge_color='gray', width=1, font_size=5)

    noms = {node: atributs_nodes[node].nom for node in atributs_nodes}
    nx.draw_networkx_labels(g, pos, labels=noms, font_size=5)

    # Mostrar nom de les línies
    atributs_arestes = nx.get_edge_attributes(g, 'Bus')
    atributs = {aresta: atributs_arestes[aresta].linia for aresta in atributs_arestes}
    nx.draw_networkx_edge_labels(g, pos, edge_labels=atributs, font_size=5)

    plt.interactive(True)
    plt.show()
    plt.pause(1000)


def plot(g: BusesGraph, nom_fitxer: str) -> None:
    """Mostra el graf de busos sobre el mapa de barcelona"""
    # Els dos primers paràmetres són la mida del mapa que es crearà
    mapa_barcelona = StaticMap(1920, 1080)

    atributs_nodes = nx.get_node_attributes(g, 'Parada')
    coordenades = {node: atributs_nodes[node].coordenades for node in atributs_nodes}

    for aresta in g.edges:
        node1 = aresta[0]
        node2 = aresta[1]

        lat1, lon1 = coordenades[node1]
        coordenades1 = (lon1, lat1)
        lat2, lon2 = coordenades[node2]
        coordenades2 = (lon2, lat2)

        mapa_barcelona.add_line(Line([coordenades1, coordenades2], 'purple', 1))

    image = mapa_barcelona.render()

    plt.imshow(image)
    plt.axis('off')
    plt.show()

    image.save(nom_fitxer)
