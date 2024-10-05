# Mòdul BILLBOARD


## Diccionaris en comptes de llistes
-En el aquest mòdul he deicidit fer un petit canvi en els atributs de la classe billboard. En comptes de llistes de pelis, cinemes i projeccions he fet que siguin diccionaris. Un motiu pel qual he fet aquest canvi és per motius d'eficiència, ja que a l'hora de crear la cartellera per mostrarla, em convenia mes que fossin diccionaris per accedir directament a una peli concreta o un cinema cincret i no recorrer tota la llista en busca d'aquesta peli o cinema. Això es pot veure clarament en la funció dict_cartellera. A més, alhora de recolectar les películes i les projeccions em permet programar fàcilment que no hi hagin películes o projeccions repetides

## Funcionament del BIllboard
-En primer lloc tenim la classe billboard amb els seus paràmetres i els seus mètodes propis per filtrar películes.
-A part de la classe trobem le funció principal "read" que llegueix les dades de la web SensaCine i obté una variable billboard. Dins del read, per cada link(cadascuna de les tres pàgines) primer actualitzem el diccionari de cinemes amb la funció "get_cinemes" i després, per cada película, actualitzem el diccionari de películes amb la funció "get_films" i les projeccions amb la funció "get_projections" només d'aquelles películes que es fagin en cinemes de Barcelona, de manera que la demo no doni problemes al buscar el camí a un cinema (ja que molts cinemes estan fora de barcelona i el graf es de la ciutat de barcelona).


## Diccionari de coordenades en comptes de geocode
-He deicidit fer un diccionari amb les coordenades exactes de cada cinema perquè les adreçes extretes de la web SensaCine venen en un format que dona problemes amb la funció goecode. D'aquesta manera és més fàcil a accedir a les coordenades de cada cinema.

-Per aprofitar la funció get_cinemes, que recopila tots els cinemes disponibles, en la opció de la demo (2.Cercar a la cartellers - 4.Mostrar totes les opcions per anar a veure una película) es donen les adreçes de cada cinema, de manera que l'usuari pugui veure on estan els cinemes.


## Solució per no agafar les películes de dies diferents
-Hi ha un problema amb les classes item_resa de la web SensaCine i és que els dies son independents de les classes. En sonseqüència, si busquem totes les classes item_res agafa les películes de la cartellera de tots els dies. Per solucionar-ho he deicidit crear una diccionari amb una tupla de cine i película com a clau. D'aquesta manera, només afegeix les películes del primer dia.


# Mòdul Buses

## Funcionament mòdul buses
La funció "get_buses_graph" s'encarrega d'obtenir el graf de buses amb les dades de l'AMB de manera que per cada línia de bus, obtenim els nodes de cada parada amb la funció "get_nodes" i establim cada aresta entre parades amb la funció  "get_edges" (que utilitza la llista de nodes que li passa la funció anterior). La funció "show" mostra el el graf sense el mapa (en aquest cas he programat que surti el graf amb tots els noms de cada parada i cada línia, per això surt un graf brut ple de lletres, amb el city he cambiat això). La funció "plot" mostra el graf sobre el mapa de barcelona.



## Posar atribut "time" com a atribut de cada node i de no de cada classe
En primer lloc, en el meu cas els tipus de nodes o arestes en el meu graf (tant de bus com de ciutat) estan dins d'un atribut que els identifica. Per exemple un node Cruïlla té un identificador del seu node i després un atribut 'Cruïlla' que es una classe Cruïlla amb els seus atributs a la vegada. 
Dit això, he decidit que la variable temps que indica quan temps es tarda en passar per una aresta, posarla com a atribut del node i no com a atribut de cada classe 'Carrer' o 'Bus'. El motiu es perquè pugues agafar aquest atribut concret i fer el dijkstra en un funció del temps. 


# Mòdul City

## Funcionament mòdul city
La funció principal es "build_city_graph" que crea el city graph en tres passos. El primer pas es assignar al graf de carrers de barcelona el tipus 'Cruïlla' als seus nodes i el tipus 'Carrer' a les seves arestes. Les funcions que s'encarreguen d'això son les funcions 'get_nodes_cruïlla' i 'get_edges_carrer'. El segon pas és, un cop tots els nodes i arestes d'ambòs grafs estan ben classificats, juntar els dos grafs en el citygraph. Per últim, establim les arestes entre cada node parada i el seu node cruïlla mes proper amb la funció 'connectar_parada_cruïlla'. Les funcion 'plot' i 'show' fan el mateix que en el buses, però la funció 'show' en aquest cas mostra el graf sense els noms dels nodes i arestes. Per últim la funció 'get_osmnx_graph' agafa el graf de carrers de barcelona i les funcions 'save_osmnx_graph' i 'load_osmnx_graph' s'encarreguen de guardar i baixar respectiavemnt un graf del directori que estiguem.

## Guardar grafs
He decidit guardar tots els grafs(buses, carrers i el de city) mitjançant la llibreria pickle de manera que només s'hagin de crear una vegada. Això fa el programa més ràpid d'executar.

## Funció get_nodes_cruïlla
Aquesta funció serveix per etiquetar cada node del gram de barcelona d'osmnx amb un atribut cruïlla de la mateixa manera que estan etiquetats amb un atribut 'Parada' els nodes del graf de busos. D'aquesta manera és més fàcil treballar amb els dos tipus de node perquè tenen el mateix format.


## Plot Camí
Al mostrar un camí concret, els trossos del camí on s'hagi d'anar caminant(les arestes tipus Carrer), es mostren en color vermell i els trossos en bus es mostren en blau.


# Mòdul Demo

## Funcionament mòdul Demo
A l'executar la funció main, s'obre el menú del CineBus i es mostren 7 opcions. La primera mostra el nom dels autors del projecte. La segona mostra tota la cartellera mitjançant la funció 'mostrar_cartellera'. La tercera mostra les opcions per cercar a la cartellera mitjançant la funció 'filtrar': cada una de les funcions té el sue mètode respectiu de la variable 'billboard'. La quarta opció és crear el graf de busos(si no ha sigut creat i guardat prèviament) i mostrar-lo o bé a sobre del mapa o sol. La cinquena opció és el metaiex però amb el graf ciutat. En aquestes dues opcions s'utilitzens les funcions 'crear_graf_busos', 'crear_graf_carrer' i 'crear_graf_ciutat'. La sisena opció es la de mostrar el camí per veure una película donant la película que es vol veure i l'hora a partir de la qual es vol veure la película, mitjançant la funció 'trobar_camí'.


## Algorisme
L'algorisme per trobar el camí per veure una película és ordenar les projeccions de manera que primer estiguin les projeccions més d´hora i per cada una d'aquestes projeccions buscar si per anar al seu cinema arribarem abans que comenci la película o no. Si troba un camí factible el mostra per pantalla. Si mostra una direcció errònia és que el cinema està fora de barcelona(en principi no hauria de passar al haver fet el filtre en el billboard)




