from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import json
from typing import Any


@dataclass
class Film:
    title: str
    genre: list[str]
    directors: list[str]
    actors: list[str]


@dataclass
class Cinema:
    name: str
    address: str


@dataclass
class Projection:
    film: Film
    cinema: Cinema
    time: tuple[int, int]   # hora:minut
    language: str


class Billboard:
    _films: dict[str, Film]
    _cinemas: dict[str, Cinema]
    _projections: dict[Any, Projection]
    # La clau de les projeccions es una tupla del seu cinema, película i hora

    def __init__(self, films: dict[str, Film], cinemas: dict[str, Cinema], projection: dict[Any, Projection]):
        """Constructor del billboard"""
        self._films = films
        self._cinemas = cinemas
        self._projections = projection

    def films(self) -> dict[str, Film]:
        """Retorna un diccionari llista de películes"""
        return self._films

    def cinemas(self) -> dict[str, Cinema]:
        """Retorna un diccionari de cinemes"""
        return self._cinemas

    def projections(self) -> dict[Any, Projection]:
        """Retorna un diccionari de projeccions"""
        return self._projections

    def dict_cartellera(self) -> dict[Cinema, dict[Film, tuple[int, int]]]:
        """Crea un diccionari amb la informació de la cartellera organitzada"""

        dict_cinemes: dict[Cinema, dict[Film, tuple[int, int]]] = {}
        projeccions_dict = self.projections()

        for projeccio in projeccions_dict:
            nom_cinema, nom_peli, hora = projeccio

            if nom_cinema not in dict_cinemes:
                dict_cinemes[nom_cinema] = {}

            if nom_peli not in dict_cinemes[nom_cinema]:
                dict_cinemes[nom_cinema][nom_peli] = []
                dict_cinemes[nom_cinema][nom_peli].append(hora)
            else:
                dict_cinemes[nom_cinema][nom_peli].append(hora)

        return dict_cinemes

    def mostrar_pelicules(self) -> None:
        """Retorna un llistat de les películes disponibles d'aquell dia"""
        for pelicula in self.films():
            print(pelicula)

    def filtrar_per_director(self, director: str) -> None:
        """Retorna un llistat de películes d'un director en concret"""
        dict_pelicules = self.films()
        print('********')
        for pelicula in self.films():
            if director in dict_pelicules[pelicula].directors:
                print(pelicula)
        print('********')

    def filtrar_per_actor(self, actor: str) -> None:
        """Retorna un llistat de películes on apareix un actor concret"""
        dict_pelicules = self.films()
        print('********')
        for pelicula in self.films():
            if actor in dict_pelicules[pelicula].actors:
                print(pelicula)
        print('********')

    def opcions_pelicula(self, pelicula: str) -> None:
        """Retorna les opcions(cinemes i hores) per veure una película"""

        dict_cartellera = self.dict_cartellera()
        dict_cinemes = self.cinemas()

        for cinema in dict_cartellera:
            if pelicula in dict_cartellera[cinema]:
                print(cinema)
                print('--------')
                print(dict_cinemes[cinema].address)
                print('Hores:', *dict_cartellera[cinema][pelicula])
            print('\n')

    def filtrar_per_cine(self, cine: str) -> None:
        """Retorna la capçelera per un cine concret"""
        dict_cartellera = self.dict_cartellera()
        dict_films = self.films()

        cinema = dict_cartellera[cine]
        print(cine)
        print('------------------------')
        for pelicula in cinema:
            film = dict_films[pelicula]
            print('Nom:', pelicula)
            print('Directors:', *film.directors)
            print('Actors:', *film.actors)
            print('Gènere:', *film.genre)
            print('Hores:', *cinema[pelicula])
            print('*****')
        print('\n')

    def coordenades(self) -> dict[str, tuple[float, float]]:
        """Retorna un diccionari amb les coordenades de cada cinema"""
        dict_coordenades = {
         "Arenas Multicines 3D": {"x": 2.1492547843193073,
                                  "y": 41.37646939337358},
         "Aribau Multicines": {"x": 41.386277920277706,
                               "y": 2.162694921760187},
         "Bosque Multicines": {"x": 2.1518885468259557,
                               "y": 41.40152114130492},
         "Cinema Comedia": {"x": 2.1675852046767448,
                            "y": 41.38960330077992},
         "Cinemes Girona": {"x": 2.1645598733643348,
                            "y": 41.39966027433518},
         "Cines Verdi Barcelona": {"x": 2.1569082116829934,
                                   "y": 41.40415457993846},
         "Cinesa Diagonal 3D": {"x": 2.1362338852834113,
                                "y": 41.393820278366256},
         "Cinesa Diagonal Mar 18": {"x": 2.2165112520703834,
                                    "y": 41.41038995560875},
         "Cinesa La Maquinista 3D": {"x": 2.198351242325446,
                                     "y": 41.439599242032735},
         "Cinesa SOM Multiespai": {"x": 2.1807989925693656,
                                   "y": 41.435483866264974},
         "Glòries Multicines": {"x": 2.1926361001670647,
                                "y": 41.40580598426224},
         "Gran Sarrià Multicines": {"x": 2.1340071926598903,
                                    "y": 41.39498512702421},
         "Maldá Arts Forum": {"x": 2.173917798428675,
                              "y": 41.3832600699012},
         "Renoir Floridablanca": {"x": 2.162505363014305,
                                  "y": 41.381773404049355},
         "Sala Phenomena Experience": {"x": 2.171797398165092,
                                       "y": 41.40909876614961},
         "Yelmo Cines Icaria 3D": {"x": 2.198168960433586,
                                   "y": 41.39094506004838},
         "Boliche Cinemes": {"x": 2.1536373359852115,
                             "y": 41.395331636035905},
         "Zumzeig Cinema": {"x": 2.145234833133575,
                            "y": 41.377530212926565},
         "Balmes Multicines": {"x": 2.138635645269617,
                               "y": 41.40723455196959},
         "Cinesa La Farga 3D": {"y": 41.36317928996277,
                                "x": 2.1047759361301166},
         "Filmax Gran Via 3D": {"x": 2.128473953063911,
                                "y": 41.35837195121502},
         "Full HD Cinemes Centre Splau": {"x": 2.078726642257926,
                                          "y": 41.347498581621295},
         "Cine Capri": {"x": 2.0952819228917035,
                        "y": 41.325792919567945},
         "Ocine Màgic": {"x": 2.2305183067930323,
                         "y": 41.44380761685543},
         "Cinebaix": {"x": 2.045032967264372,
                      "y": 41.38216564352179},
         "Cinemes Can Castellet": {"x": 2.0405817672406714,
                                   "y": 41.345105769191505},
         "Cinemes Sant Cugat": {"x": 2.090104829963655,
                                "y": 41.469629295798455},
         "Cines Montcada": {"x": 2.1802955447178034,
                            "y": 41.49419046011285},
         "Yelmo Cines Baricentro": {"x": 2.138402345183364,
                                    "y": 41.50834927343643},
         "Yelmo Cines Sant Cugat": {"x": 2.0537567747778427,
                                    "y": 41.48349434469893}}
        return dict_coordenades


def get_films(f: Any, films_dict: dict[str, Film]) -> dict[str, Film]:
    """Retorna la llista de totes les películes
    del mateix dia que apareixen a la web SensaCine"""

    data_movie = json.loads(f.div["data-movie"])
    film_title = data_movie['title']

    if film_title not in films_dict:
        films_dict[film_title] = Film(film_title, data_movie['genre'], data_movie['directors'], data_movie['actors'])

    return films_dict


def get_projections(f: Any, projections_dict: dict[list[Any], Projection], cinemas_dict: dict[str, Cinema], films_dict: dict[str, Film], dict_tuple: dict[Any, Projection]) -> tuple[dict[Any, Projection], dict[Any, Projection]]:
    """Retorna totes les projeccions disponibles del
    dia que apareixen a la web SensaCine"""

    ciutat_cinema = json.loads(f.div["data-theater"])['city']
    if ciutat_cinema == 'Barcelona':
        cinema_film = json.loads(f.div["data-theater"])['name']
        film_title = json.loads(f.div["data-movie"])['title']

        # Per eliminar posibles espais adicionals en els noms dels cinemes
        cinema_film = cinema_film.split()
        cinema_film = " ".join(cinema_film)

        pelicula = films_dict[film_title]
        cine = cinemas_dict[cinema_film]

        # Per treure el llenguatge de la peli
        info_llenguatge = f.find_all('span', class_='bold')
        llenguatge = info_llenguatge[0].text.strip()

        if llenguatge == 'Versión Original':
            language = 'Versión Original'
        else:
            language = 'Spanish'

        tupla = cinema_film, film_title

        if tupla not in dict_tuple:

            hores = f.find('ul', class_='list_hours')
            llista_hores = hores.find_all('em')

            for sessio in llista_hores:
                hora = str(sessio.text.strip())
                projeccio = Projection(pelicula, cine, hora, language)
                projections_dict[cinema_film, film_title, hora] = projeccio

            dict_tuple[cinema_film,  film_title] = projeccio

        return projections_dict, dict_tuple


def get_cinemas(soup: BeautifulSoup, cinemas_dict: dict[str, Cinema]) -> dict[str, Cinema]:
    """Retorna el diccionari de tots els cinemes
    del mateix que apareixen a la web SensaCine"""

    info_cinemas = soup.find_all('div', class_="margin_10b j_entity_container")

    for c in info_cinemas:
        info_cinema = c.find('a', class_="no_underline j_entities")
        name_cinema = info_cinema.text.strip()
        info_adress = c.find_all('span', class_='lighten')
        adress_cinema = str(info_adress[1].text.strip())
        cinemas_dict[name_cinema] = Cinema(name_cinema, adress_cinema)

    return cinemas_dict


def read() -> Billboard:
    """Retorna la cartellera de SensaCine del dia actual,
    és a dir, una variable Billboard que conté tres diccionaris:
    un amb les pelicules, una altra amb els cinemes i la última
    amb totes les projeccions d'aquell dia"""

    films_dict: dict[str, Film] = {}
    cinemas_dict: dict[str, Cinema] = {}
    projections_dict: dict[Any, Projection] = {}

    dict_tuples: dict[Any, Projection] = {}

    links = ["https://www.sensacine.com/cines/cines-en-72480/",
             "https://www.sensacine.com/cines/cines-en-72480/?page=2",
             "https://www.sensacine.com/cines/cines-en-72480/?page=3"]

    for link in links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Obtenció de cinemes
        cinemas_dict = get_cinemas(soup, cinemas_dict)

        # Obtenció de películes i sessions
        info_films = soup.find_all('div', class_="item_resa")

        # f es cada classe item_resa(representa la classe de cada película)
        for f in info_films:
            ciutat_cinema = json.loads(f.div["data-theater"])['city']
            if ciutat_cinema == 'Barcelona':
                films_dict = get_films(f, films_dict)
                projections_dict, dict_tuples = get_projections(f, projections_dict, cinemas_dict, films_dict, dict_tuples)

    return Billboard(films_dict, cinemas_dict, projections_dict)
