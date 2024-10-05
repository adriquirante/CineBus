import billboard
import buses
import city
from yogi import read
import os
from typing import TypeAlias
from itertools import pairwise


Path: list[int] = list()

Coord: TypeAlias = tuple[float, float]


def crear_graf_busos() -> buses.BusesGraph:
    """Crea el graf de busos desde 0 si no està guardat,
    i si no el descarrega del directori"""

    if os.path.exists('graf_busos.p'):
        graf_busos = city.load_osmnx_graph('graf_busos.p')

    else:
        graf_busos = buses.get_buses_graph()
        city.save_osmnx_graph(graf_busos, 'graf_busos.p')
    return graf_busos


def crear_graf_carrers() -> city.OsmnxGraph:
    """Crea el graf de la ciutat de barcelona si no està guardat,
    i si no el descarrega del directori"""

    if os.path.exists('barcelona.grf'):
        graf_carrers = city.load_osmnx_graph('barcelona.grf')

    else:
        graf_carrers = city.get_osmnx_graph()
        city.save_osmnx_graph(graf_carrers, 'barcelona.grf')

    return graf_carrers


def crear_graf_ciutat(graf_carrers: city.OsmnxGraph, graf_busos: city.BusesGraph) -> city.CityGraph:
    """Crea el graf de busos desde 0 si no està guardat,
    i si no el descarrega del directori"""

    if os.path.exists('graf_ciutat.p'):
        graf_ciutat = city.load_osmnx_graph('graf_ciutat.p')

    else:
        graf_ciutat = city.build_city_graph(graf_carrers, graf_busos)
        city.save_osmnx_graph(graf_ciutat, 'graf_ciutat.p')

    return graf_ciutat


def trobar_cami(ox_g: city.OsmnxGraph, graf_ciutat: city.CityGraph, billboard: billboard) -> None:
    """Mostra el camí més curt per anar a vuere una película"""

    dict_hora_cine: dict[str, list[str]] = {}
    llista_hores_possibles: list[str] = list()

    dict_projeccions = billboard.projections()
    coordenades = billboard.coordenades()

    pelicula_client = input('Quina película vols veure?').split()
    pelicula_client = " ".join(pelicula_client)

    print('Quines son les teves coordenades?')
    src = read(float), read(float)

    print('A partir de quina hora vols veure la película?')
    hora_client = read(str)

    for projeccio in dict_projeccions:
        cine, peli, hora = projeccio
        if peli == pelicula_client and hora > hora_client:
            if hora not in dict_hora_cine:
                dict_hora_cine[hora] = []
            else:
                dict_hora_cine[hora].append(cine)
            llista_hores_possibles.append(hora)

    llista_hores_possibles.sort()

    for hora in llista_hores_possibles:
        cines = dict_hora_cine[hora]
        for cine in cines:
            temps_camí = 0
            dst = coordenades[cine]['y'], coordenades[cine]['x']
            path = city.find_path(ox_g, graf_ciutat, src, dst)

            # Trobem el temps en arribar al cine amb la projecció més d'hora
            for node1, node2 in pairwise(path):
                aresta = graf_ciutat[node1][node2]
                if len(aresta) == 0:
                    pass
                else:
                    if 'Carrer' in aresta:
                        long = aresta['Carrer'].longitud
                        # velocitat promig d'una persona caminant
                        velocitat_caminant = 6
                        time = long/velocitat_caminant
                    else:
                        long = aresta['Bus'].longitud
                        # velocitat promig d'un bus
                        velocitat_bus = 12
                        time = long/velocitat_bus
                    temps_camí += time

            # Calculem si arriba a la película o no

            # Passem a segons l'hora del client
            hores, minuts = map(int, hora_client.split(":"))
            segons_client = hores*3600 + minuts*60

            # Passem a segons l'hora de la peli
            hores, minuts = map(int, hora.split(":"))
            segons_peli = hores*3600 + minuts*60

            if segons_client + temps_camí < segons_peli:
                return path


def mostrar_cartellera(cartellera: billboard.Billboard) -> None:
    """Mostrar el contingut de la cartellera de forma ordenada"""

    dict_cartellera = cartellera.dict_cartellera()
    dict_films = cartellera.films()

    for cinema in dict_cartellera:
        print(cinema)
        print('------------------------')
        for pelicula in dict_cartellera[cinema]:
            film = dict_films[pelicula]
            print('Nom:', pelicula)
            print('Directors:', *film.directors)
            print('Actors:', *film.actors)
            print('Gènere:', *film.genre)
            print('Hores:', *dict_cartellera[cinema][pelicula])
            print('*****')
        print('\n')


def filtrar(opció2: int, cartellera: billboard) -> None:
    """Conte totes les opcions per filtrar a la cartellera"""
    if opció2 == 1:
        cartellera.mostrar_pelicules()
    elif opció2 == 2:
        director = input('Digues el nom del director:').split()
        director = " ".join(director)
        cartellera.filtrar_per_director(director)
    elif opció2 == 3:
        actor = input('Digues el nom de l actor:').split()
        actor = " ".join(actor)
        cartellera.filtrar_per_actor(actor)
    elif opció2 == 4:
        pelicula = input('Digues el nom de la película:').split()
        pelicula = " ".join(pelicula)
        cartellera.opcions_pelicula(pelicula)
    elif opció2 == 5:
        cine = input('Digues el nom del cine:').split()
        cine = " ".join(cine)
        cartellera.filtrar_per_cine(cine)


def main() -> None:
    cartellera = billboard.read()
    print('Benvingut a CineBus!')
    print('Escull entre les següents opcions:')
    print('1. Mostrar cartellera de SensaCine')
    print('2. Cercar a la cartellera')
    print('3. Mostrar el graf de busos')
    print('4. Mostrar el graf ciutat')
    print('5. Mostrar el camí més proper per anar a veure una película')

    opció = read(int)
    while opció != 6:

        if opció == 1:
            mostrar_cartellera(cartellera)

        elif opció == 2:
            while True:
                print('Opcions per cercar')
                print('---------------------')
                print('1.Mostrar les películes disponibles del mateix dia')
                print('2.Mostrar les películes dispoinbles d un director')
                print('3.Mostrar les películes on aparegui un actor')
                print('4.Mostrar les opcions per anar a veure una película')
                print('5.Mostrar cartellera d un cinema concret')
                print('6.Tornar enrere')

                opció2 = read(int)
                if opció2 == 6:
                    break
                filtrar(opció2, cartellera)

        elif opció == 3:
            graf_buses = buses.get_buses_graph()
            while True:
                print('Opcions per mostrar mapa')
                print('---------------------')
                print('1.Mostrar a sobre del mapa')
                print('2.Mostrar només el graf')
                print('3.Tornar enrere')

                opció2 = read(int)

                if opció2 == 1:
                    buses.plot(graf_buses, 'mapa_graf_busos.png')
                elif opció2 == 2:
                    buses.show(graf_buses)
                elif opció2 == 3:
                    break

        elif opció == 4:
            graf_carrers = crear_graf_carrers()
            graf_busos = crear_graf_busos()
            graf_ciutat = crear_graf_ciutat(graf_carrers, graf_busos)
            while True:
                print('Opcions per mostrar mapa')
                print('---------------------')
                print('1.Mostrar a sobre del mapa')
                print('2.Mostrar només el graf')
                print('3.Tornar enrere')

                opció2 = read(int)

                if opció2 == 1:
                    city.plot(graf_ciutat, 'mapa_graf_ciutat.png')
                elif opció2 == 2:
                    city.show(graf_ciutat)
                elif opció2 == 3:
                    break

        elif opció == 5:
            if os.path.exists('graf_ciutat.p') and os.path.exists('barcelona.grf'):
                graf_ciutat = city.load_osmnx_graph('graf_ciutat.p')
                graf_carrers = city.load_osmnx_graph('barcelona.grf')
            else:
                graf_carrers = crear_graf_carrers()
                graf_busos = crear_graf_busos()
                graf_ciutat = crear_graf_ciutat(graf_carrers, graf_busos)

            path = trobar_cami(graf_carrers, graf_ciutat, cartellera)
            if path is not None:
                city.plot_path(graf_ciutat, path, 'camí_demo.png')
            else:
                print('Aquesta película no està disponible')

        print('Escull entre les següents opcions:')
        print('1. Mostrar cartellera de SensaCine')
        print('2. Cercar a la cartellera')
        print('3. Mostrar el graf de busos')
        print('4. Mostrar el graf ciutat')
        print('5. Mostrar el camí més proper per anar a veure una película')
        print('6. Acabar la cerca')

        opció = read(int)


if __name__ == '__main__':
    main()
