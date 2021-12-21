# -*- coding: utf-8 -*-
"""
Ce script traite les erreurs de correspondance d'OSRM.
Ensuite, les distances entre chaque match sont calcules en
suivant le reseau.
De ces distances sont extraites les vitesses entre chaque match.
Enfin, les vitesses pour chaque segment sont attribues.

"""
__authors__ = ("Alexis Huart")
__contact__ = ("alexis.huart@protonmail.com")
__date__ = "05/03/19"
__version__ = "47"

# importer les lib
import sys
sys.path.append("C:\SYNC\SYNCulb\Memoire\DB\Python\Fonctions")

import json
import psycopg2
import numpy as np
import pandas as pd
import geopandas as gpd
import time
import sqlalchemy

from shapely.geometry import Point, LineString
from psycopg2.extensions import register_adapter, AsIs

# Importer mes fonctions.
import correct_roundabout as roundabout
import same_from_to as sft
import backward
import overlay
import azimut
import edge_intersect_by_match as eibm
import distance_following_network as dfn
import get_distance_to_next_match as get_dtnm
import assign_edge_speed as aes


def wkb_hexer(line):
    # Generation des WKB
    return line.wkb_hex


def process_time():
    # Enregistrer et afficher le temps de traitement
    gdf_all_trips['python_computation_time'] = computation_time = (
        (time.time()) - start_time)
    print('Traitement :', computation_time, 'sec')


def re_assign_edge_id(gdf_edges):
    # Reassigner les edge_id apres le traitement
    first_edge_id = gdf_edges['edge_id'].iloc[0]
    a = 0
    for i in gdf_edges.index:
        gdf_edges.loc[i, 'edge_id'] = first_edge_id + a
        a += 1
    return gdf_edges


def addapt_numpy_float64(numpy_float64):
    # Transformer les float64 numpy en float classique.
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    # Transformer les int64 numpy en int classique.
    return AsIs(numpy_int64)


# Variables d'affichage et d'attribution des id.
number_of_trip = total_edge_id = 0

# Liste des trips a traiter.
trips_id = []

# Confidence en dessous de laquelle le trip ne sera pas traite.
confidence_treshold = 0.7

# Marge d'erreur (en millieme) entre la distance du trip et les
# distance_to_next_match calculees.
error_range = 5

# Changement d'azimut (en degree) au dela duquel le match sera
# supprime.
max_bearing = 160

# Table contenant les points a traiter.
points_table = 'citygis.points'
points_name = points_table.replace('citygis.', '')

# Table contenant les interventions
interventions_table = 'citygis.interventions'

# Table allant contenir les segments des traces.
osrm_edges_table = 'citygis.osrm_edges'
osrm_edges_name = osrm_edges_table.replace('citygis.', '')

# Table allant contenir les trips.
osrm_trips_table = 'citygis.osrm_trips'
osrm_trips_name = osrm_trips_table.replace('citygis.', '')

# Tables temporaires.
temp_table_1 = 'citygis.temp_table_1'
temp_name_1 = temp_table_1.replace('citygis.', '')
temp_table_2 = 'citygis.temp_table_2'
temp_name_2 = temp_table_2.replace('citygis.', '')

# Connexion a la DB.
try:
    connection = psycopg2.connect(
        "dbname='postgres' user='postgres' host='127.0.0.1' port = '5432' password=''")
    engine = sqlalchemy.create_engine(
        "postgresql://**************")
    cursor = connection.cursor()
except BaseException:
    print ("Unable to connect to the database!")

# Recuperer la liste de trips a traiter
with open('first24000.txt', 'r') as inputfile:
    trips_id = inputfile.readlines()

# Changer le type de str a int
trips_id = list(map(int, trips_id))

# Recuperer la liste de trip deja traitee
try:
    sql = """
            SELECT  DISTINCT trip_id
            FROM    {}
            """.format(temp_table_1)
    df_already_done = pd.read_sql_query(sql, connection)

except Exception:
    pass

for trip in trips_id:

    # Suivre le temps de traitement.
    start_time = time.time()

    # Liste pour updater la table point_table.
    osrm_answer = []

    # Listes pour l'update de la table osm_edges.
    osm_point, osm_node_id, osm_node_from, osm_node_to, list_edge_id = [
    ], [], [], [], []

    # Compte a afficher
    number_of_trip += 1

    # Creer gdf_all_trips pour stocker les informations generales 
    # sur le trip.
    gdf_all_trips = gpd.GeoDataFrame(
        columns=[
            'trip_id',
            'geojson',
            'confidence',
            'osrm_msg',
            'geometry',
            'total_trip_length',
            'total_dtnm_length',
            'delta',
            'is_equality',
            'osrm_computation_time',
            'python_computation_time',
            'confidence_treshold',
            'error_range',
            'backward',
            'u_turn',
            'roundabout',
            'illegal_turn'])

    # Creer gdf_trips qui contiendra les donnees sur les points et
    # les matchs.
    gdf_trip = gpd.GeoDataFrame(
        columns=[
            'point_id',
            'time',
            'timestamp',
            'long_match',
            'lat_match',
            'geometry',
            'bearing',
            'bearing_delta',
            'point_is_intersected',
            'edge_id_intersected',
            'order_of_match_on_same_edge',
            'edge_id_who_is_intersected',
            'second_edge_id_who_is_intersected',
            'dist_from_edge_start',
            'total_next_edge_length_whitout_match',
            'distance_to_next_match',
            'speed_to_next_match'])

    # Creation du gdf_edges allant contenir les segments OSM.
    gdf_edges = gpd.GeoDataFrame(
        columns=[
            'edge_id',
            'trip_id',
            'osm_node_from',
            'osm_node_to',
            'long_from',
            'lat_from',
            'long_to',
            'lat_to',
            'geom_from',
            'geom_to',
            'edgeline',
            'edge_length',
            'edge_is_intesected',
            'nb_point_who_intersect',
            'edge_speed',
            'u_turn',
            'same_from_to'])

    # Attribution de projection
    gdf_edges.crs = {'init': 'epsg:31370'}

    # Modifier le type par defaut.
    gdf_all_trips[['trip_id',
                   'total_trip_length',
                   'total_dtnm_length',
                   'confidence_treshold']].astype(int)
    gdf_all_trips[['confidence',
                   'python_computation_time',
                   'delta']].astype(np.float64)
    gdf_all_trips[['is_equality',
                   'backward',
                   'roundabout',
                   'illegal_turn']].astype(bool)

    # Afficher dans la console.
    print('\n')
    print('N de trip:', number_of_trip)
    print('trips_id:', trip)

    try:
        # Si le trip a deja ete traite par le passe:
        if trip in df_already_done.values:
            # Passer au trip suivant
            print('Trip deja traite')
            continue

    except Exception:
        pass

    # Recuperer la geometrie du lieu d'intervention sur base de
    # intervention_id (pour une facilite de visualisation sur QGIS).
    sql = """
            SELECT  DISTINCT point
            FROM    {} inter
                    JOIN {} pt ON inter.id = pt.intervention_id
            WHERE pt.trips_id = {}
            """.format(interventions_table, points_table, trip)
    cursor.execute(sql)

    # Injecter le trip_id et la geometrie dans le gdf. Attribuer
    # une projection a la geometrie.
    gdf_all_trips['trip_id'] = pd.Series(trip)
    gdf_all_trips['geometry'] = cursor.fetchall()

   # Recuperer les info du trip a traiter
    try:
        sql = """SELECT  point_id,
                        {}.timedate as time,
                        EXTRACT(EPOCH FROM{}.timedate) as timestamp
                FROM    {}
                WHERE   trips_id={}
                ORDER BY trips_id, timedate
                """.format(points_name, 
                            points_name, 
                            points_table, 
                            trip)

    except (Exception, psycopg2.Error) as error:
        print("Error to fetch data from trip:", error)

    # Recuperer les donnees dans un df intermediaire
    gdf_distribution = gpd.GeoDataFrame(
        pd.read_sql(sql, engine, index_col=None))

    # Injecter les donnees du trip dans le gdf_trip.
    gdf_trip['point_id'] = gdf_distribution['point_id']
    gdf_trip['time'] = gdf_distribution['time']
    gdf_trip['timestamp'] = gdf_distribution['timestamp']

    # Supprimer le gdf distribution
    del gdf_distribution

    # Afficher le nombre de points a traiter.
    print ('Nbr de points a traiter:', len(gdf_trip))

    # Recuperer le geojson a traiter
    try:
        sql = """SELECT  geojson
                FROM    {}
                WHERE   trip_id={}
                """.format(osrm_trips_table, trip)

    except (Exception, psycopg2.Error) as error:
        print("Error to fetch data from trip:", error)

    # Injecter les donnees du trip dans le gdf_trip.
    gdf_all_trips['geojson'] = pd.read_sql(
        sql, engine, index_col=None)

    # Recuperer la reponse OSRM (la boucle for n'est pas necessaire
    # mais je n'ai pas trouve d'autre solution pour extraire 
    # un Json enregistre comme text depuis une serie pandas)
    for contents in gdf_all_trips['geojson']:
        Geojson = json.loads(contents)

    # Attribuer une projection aux gdf.
    gdf_trip.crs = {'init': 'epsg:31370'}
    gdf_all_trips.crs = {'init': 'epsg:31370'}

    # Extraction depuis le Geojson.
    # Si le trace n'est pas matche, passer au trip suivant.
    if Geojson['code'] != "Ok":
        # Enregistrer et afficher dans la console.
        gdf_all_trips['osrm_msg'] = pd.Series(Geojson['code'])
        print('Non matche')

        # Calculer et enregistrer le temps de traitement du trip.
        process_time()

        # Injecter le gdf dans la db.
        gdf_all_trips.to_sql(
            name=temp_name_1,
            con=engine,
            schema='citygis',
            if_exists='append',
            index=False)

        # Passer au trip suivant.
        continue

    # Si la confidence est sous le seuil etabli, passer au trip
    # suivant.
    elif Geojson['matchings'][0]['confidence'] \
            < confidence_treshold:
        # Extraction de la confidence depuis le Json
        gdf_all_trips['confidence'] = confidence \
            = Geojson['matchings'][0]['confidence']

        # Enregistrer dans le df et afficher dans la console.
        gdf_all_trips['osrm_msg'] = 'low_confidence'
        print('Confidence faible:', confidence)

        # Calculer et enregistrer le temps de traitement du trip et
        # passer au trip suivant.
        process_time()

        # Injecter le gdf dans la db.
        gdf_all_trips.to_sql(
            name=temp_name_1,
            con=engine,
            schema='citygis',
            if_exists='append',
            index=False)

        continue

    # Si le trip est matche, extraire les informations du GeoJson.
    else:

        # Valeurs par defaut
        gdf_all_trips[['backward',
                       'illegal_turn',
                       'roundabout']] = False

        # Injecter le code du serveur OSRM dans le gdf
        gdf_all_trips['osrm_msg'] = pd.Series(Geojson['code'])

        # Extraction de la confidence depuis le Json et injecter
        # dans le gdf
        gdf_all_trips['confidence'] = confidence \
            = Geojson['matchings'][0]['confidence']

        # Recuperer les coordonnees des points matchees.
        for xy in Geojson['tracepoints']:
            if xy is None:
                osrm_answer.append(xy)
            elif isinstance(xy, dict):
                osrm_answer.append(xy['location'])
            else:
                continue

        # Enlever la ponctuation de la reponse OSRM et la
        # transformer en list.
        osrm_answer = str(osrm_answer).replace('[','')\
                    .replace(']','').replace(' ','')\
                    .replace('None','None,None')
        osrm_answer = osrm_answer.split(',')

        # Isoler longitude et latitude et les ajouter au gdf_trip.
        gdf_trip['long_match'] = pd.Series(
            (osrm_answer[0:][::2]), index=gdf_trip.index)
        gdf_trip['lat_match'] = pd.Series(
            (osrm_answer[1:][::2]), index=gdf_trip.index)

        # Remplacer les None par des Nan.
        gdf_trip = gdf_trip.replace('None', np.nan).astype(object)

        # Supprimer les entrees du gdf_trip qui n'ont pas trouve de
        # match et reindexer le df
        gdf_trip = gdf_trip.dropna(axis=0, 
                                   how='any',
                                   subset=['long_match',
                                           'lat_match'])\
                                            .reset_index()
        gdf_trip = gdf_trip.reset_index(drop=True)

        # Convertir le gdf de string en int.
        gdf_trip['long_match'] = pd.to_numeric\
                                (gdf_trip['long_match'])
        gdf_trip['lat_match'] = pd.to_numeric\
                                (gdf_trip['lat_match'])

        # Supprimer les segments partant et arrivant au meme noeud
        # OSM ou long/lat
        gdf_edges = sft.same_from_to(gdf_edges)

        # Calculer l'azimut (bearing) des matchs et supprimer les
        # changements trop brusque (aller-retour sur un meme
        # segment).
        gdf_trip = azimut.bearing(
            max_bearing, gdf_trip, gdf_all_trips)

        # Creer des geometries a partir des latitutes longitudes 
        # des matchs.
        geom_match = [Point(xy) for xy in zip(
                        gdf_trip['long_match'],
                        gdf_trip['lat_match'])]
        geom_match = gpd.GeoSeries(geom_match)

        # Initier et changer la projection.
        geom_match.crs = {'init': 'epsg:4326'}
        geom_match = geom_match.to_crs({'init': 'epsg:31370'})

        # Inserer les geom_match dans le gdf.
        gdf_trip['geometry'] = gpd.GeoSeries(geom_match)

        # Extraction des noeudsOSM de l'itineraire depuis le Json.
        for i in Geojson['matchings'][0]['legs']\
                    [0]['annotation']['nodes']:
            osm_node_id.append(i)

        # Generer les edge_id et les injecter dans le gdf.
        for i in range(len(osm_node_id) - 1):
            list_edge_id.append(total_edge_id)
            total_edge_id += 1
        gdf_edges['edge_id'] = list_edge_id

        # Separer les noeuds en osm_node_from et osm_node_to pour
        # obtenir les sens de circulation.
        osm_node_from = osm_node_id[:]
        osm_node_to = osm_node_id[:]

        # Supprimer la derniere et la premiere valeur de la liste.
        del osm_node_from[-1]
        del osm_node_to[0]

        # Injecter dans le gdf.
        gdf_edges['osm_node_from'] = pd.Series(osm_node_from)
        gdf_edges['osm_node_to'] = pd.Series(osm_node_to)
        gdf_edges['trip_id'] = trip

        # Extraction des lat/long des noeuds OSM de l'itineraire
        # depuis le Json.
        for i in Geojson['matchings'][0]['geometry']\
                                    ['coordinates']:
            osm_point.append(i)

        # Enlever la ponctuation de la reponse OSRM et la
        # transformer en list.
        osm_point = str(osm_point).replace( '[', '')\
                                    .replace( ']', '')\
                                    .replace(' ', '')
        osm_point = osm_point.split(',')

        # Isoler longitude et latitude dans deux listes.
        OSMlong = osm_point[0:][::2]
        OSMlat = osm_point[1:][::2]

        # Separer les From des To pour les longitudes.
        OSMlong_from = OSMlong[:]
        OSMlong_to = OSMlong[:]

        # Supprimer la premiere et la derniere valeur de la liste.
        del OSMlong_from[-1]
        del OSMlong_to[0]

        # Separer les From des To pour les latitudes.
        OSMlat_from = OSMlat[:]
        OSMlat_to = OSMlat[:]

        # Supprimer la premiere et la derniere valeur de la liste.
        del OSMlat_from[-1]
        del OSMlat_to[0]

        # Injecter les long/lat des noeuds OSM dans gdf_edges.
        gdf_edges['long_from'] = pd.Series(OSMlong_from, 
                                             dtype=float)
        gdf_edges['lat_from'] = pd.Series(OSMlat_from,
                                             dtype=float)
        gdf_edges['long_to'] = pd.Series(OSMlong_to,
                                             dtype=float)
        gdf_edges['lat_to'] = pd.Series(OSMlat_to, 
                                             dtype=float)

        # Supprimer les segments partant et arrivant au meme noeud
        # OSM ou long/lat
        gdf_edges = sft.same_from_to(gdf_edges)

        # Traiter les rondpoints pris de multiple fois.
        gdf_edges = roundabout.correct_roundabout(gdf_edges)

        # Si le trace arrive par un segment (noeud from/to), fait
        # une boucle et repart par le meme segment (noeud to/from)
        gdf_edges = backward.backward(gdf_edges, gdf_all_trips)

        # Reattribuer les edge_id afin qu'ils se suivent si le df
        # n'est pas vide apres traitement.
        if not gdf_edges.empty:
            re_assign_edge_id(gdf_edges)

        # Cas ou les traitements des rond point, aller retour, etc
        # suppriment la totalite des segments.
        else:
            # Calculer et enregistrer le temps de traitement du
            # trip.
            gdf_all_trips['osrm_msg'] = 'gdf_edges_is_empty'
            process_time()

            # Injecter le gdf dans la db.
            gdf_all_trips.to_sql(
                name=temp_name_1,
                con=engine,
                schema='citygis',
                if_exists='append',
                index=False)

            # Passer au trip suivant.
            continue

        # Creer les geometries.
        geom_from = [Point(xy) for xy in zip(
                gdf_edges['long_from'],
                gdf_edges['lat_from'])]
        geom_to = [Point(xy) for xy in zip(
                gdf_edges['long_to'],
                gdf_edges['lat_to'])]

        # Injecter les geometries dans le gdf_edges.
        gdf_edges['geom_from'] = pd.Series(geom_from)
        gdf_edges['geom_to'] = pd.Series(geom_to)

        # Creer les segments a partir de geom_from et geom_to.
        edgeline = [LineString([gdf_edges.loc[i, 'geom_from'],
                                gdf_edges.loc[i, 'geom_to']])\
                                for i in gdf_edges.index]
        edgeline = gpd.GeoSeries(edgeline)

        # Attribuer une projection et la transformer en Lambert.
        edgeline.crs = {'init': 'epsg:4326'}
        edgeline = edgeline.to_crs({'init': 'epsg:31370'})

        # Injecter dans le gdf_edges
        gdf_edges['geometry'] = gpd.GeoSeries(edgeline)

        # Supprimer les entrees du gdf_trip qui n'ont pas trouve de
        # match et reindexer le df
        gdf_trip = gdf_trip.dropna( axis=0, 
                                   how='any', 
                                   subset=['long_match', 
                                           'lat_match', 
                                           'geometry'])
        gdf_trip = gdf_trip.reset_index()

        # Mettre des Nan comme valeurs par defaut pour
        # edge_id_who_is_intersected et
        # second_edge_id_who_is_intersected sans quoi une erreur
        # survient
        gdf_trip['edge_id_who_is_intersected'] = np.nan
        gdf_trip['second_edge_id_who_is_intersected'] = np.nan

        # Identifier si les segments sont croises par des matchs et
        # supprimer ceux qui ne le sont pas.
        gdf_edges, gdf_trip = eibm.edge_intersect_by_match(
                gdf_edges, 
                gdf_trip)
        
        # Re calculer et supprimer les azimuts trop brusques avec
        # les nouvelles successions de points matches.
        gdf_trip = azimut.bearing(max_bearing,
                                  gdf_trip, 
                                  gdf_all_trips)
        
        # Si le gdf_trip a moins de deux matchs ou qu'aucun segment
        # n'est croise, passer au trip suivant.
        if (len(gdf_trip) < 2)\
        or ( gdf_edges['edge_is_intesected'].all() is False):
            # Calculer et enregistrer le temps de traitement du
            # trip.
            process_time()

            # Enregistrer la cause de la fin de traitement
            gdf_all_trips['osrm_msg'] = 'not_enough_match'

            # Injecter le gdf dans la db.
            gdf_all_trips.to_sql(
                name=temp_name_1,
                con=engine,
                schema='citygis',
                if_exists='append',
                index=False)

            # Passer au trip suivant.
            print("Plus assez d'element pour traiter le trip")
            continue

        # Calculer les distances en suivant le  reseau.
        gdf_edges, gdf_trip = dfn.distance_following_network(
                                                    gdf_edges,
                                                    gdf_trip)

        # Calculer les distances entre les matchs,
        # ou distance_to_next_match (dtnm).
        gdf_edges, gdf_trip = get_dtnm.get_distance_to_next_match(
                                                        gdf_edges,
                                                        gdf_trip)
        
        # Calculer l'intervalle de temps entre les points matches.
        gdf_trip["time"] = (gdf_trip["time"].shift(-1) \
                            - gdf_trip["time"])

        # Calculer les vitesses entre chaque match,
        # ou speed_to_next_match (speed_tnm).
        for i in gdf_trip.index:
            # Exclure le dernier de la liste qui n'aura pas de
            # speed_to_next_match
            if i < (len(gdf_trip.index) - 1):
                # Calculer la vitesse en m/s et passer en km/h
                gdf_trip.loc[i,'speed_to_next_match'] = \
                (gdf_trip.loc[i,'distance_to_next_match']\
                 / gdf_trip.loc[i,"time"].seconds) * 3.6

        # Attribuer une vitesse a chaque segment sur base des
        # speed_to_next_match.
        gdf_edges, gdf_trip = aes.assign_edge_speed(
            gdf_edges, gdf_trip)
        
        # Additionner toutes les longueurs des segments.
        total_trip_length = gdf_all_trips['total_trip_length']\
                          = gdf_edges['edge_length'].sum()

        # Additionner toutes les longueurs des
        # distance_to_next_match (dtnm).
        total_dtnm_length = gdf_all_trips['total_dtnm_length']\
                          = gdf_trip['distance_to_next_match']\
                          .sum()
        gdf_all_trips['delta'] = delta \
                               = total_trip_length \
                                   - total_dtnm_length

        # Calculer un millieme de la dtnm.
        minus_x_per1000 = total_dtnm_length \
                            - ((total_dtnm_length / 1000)\
                               * error_range)
        plus_x_per1000 = total_dtnm_length \
                        + ((total_dtnm_length / 1000)\
                           * error_range)

        # Verifier que la somme de tous les segments d'un trip est
        # dans un intervalle de 0.X% en moins et en plus de 
        # la somme de toutes les distance_to_next_match du meme trip.
        if minus_x_per1000 < total_trip_length < plus_x_per1000:
            gdf_all_trips['is_equality'] = is_equality = True
        else:
            gdf_all_trips['is_equality'] = is_equality = False

        # Afficher dans la console s'il y a une egalite entre le
        # total des longueurs des segments et le total des dtnm
        # calculees.
        print('is_equality:', is_equality, 'delta:', delta)

        # Calculer et enregistrer le temps de traitement du trip.
        process_time()

        # Enregistrer les parametres du traitement.
        gdf_all_trips['confidence_treshold'] = confidence_treshold
        gdf_all_trips['error_range'] = error_range

        # Modifier le type des colonnes qui posent probleme dans
        # l'update (traitement des float/int numpy par SqlAlchimy).
        gdf_trip['order_of_match_on_same_edge'] = \
        gdf_trip['order_of_match_on_same_edge'].values.astype(int)
        
        gdf_trip['point_is_intersected'] = \
        gdf_trip['point_is_intersected'].values.astype(int)
        
        gdf_trip['edge_id_intersected'] = \
        gdf_trip['edge_id_intersected'].values.astype(int)
        
        gdf_trip['dist_from_edge_start'] = \
        gdf_trip['dist_from_edge_start'].values.astype(float)
        
        gdf_trip['edge_id_who_is_intersected'] = \
        gdf_trip['edge_id_who_is_intersected'].values.astype(int)
        
        gdf_trip['second_edge_id_who_is_intersected'] = \
        gdf_trip['second_edge_id_who_is_intersected']\
        .values.astype(int)
        
        gdf_trip['total_next_edge_length_whitout_match'] = \
        gdf_trip['total_next_edge_length_whitout_match']\
        .values.astype(float)
        
        register_adapter(np.float64, addapt_numpy_float64)
        register_adapter(np.int64, addapt_numpy_int64)

        # Transformer les geom en WKB.
        # Pour gdf_trip
        gdf_trip['geometry'] = gdf_trip['geometry']\
                                .apply(wkb_hexer)
        gdf_trip = gdf_trip.rename(columns={
                                'geometry': 'geom_match'}) 

        # Pour gdf_edges.
        gdf_edges['geom_from'] = gdf_edges['geom_from']\
                                .apply( wkb_hexer)
        gdf_edges['geom_to'] = gdf_edges['geom_to']\
                                .apply(wkb_hexer)
        gdf_edges['geometry'] = gdf_edges['geometry']\
                                .apply(wkb_hexer)
        gdf_edges = gdf_edges.rename(columns={
                                'geometry': 'edgeline'})

        # Injecter les gdf dans la db. Deux tables sont 
        # des temporaires, elles serviront a mettre a jour
        # les tables permanentes par la suite.
        gdf_edges.to_sql(
            name=osrm_edges_name,
            con=engine,
            schema='citygis',
            if_exists='append',
            index=False)
        gdf_all_trips.to_sql(
            name=temp_name_1,
            con=engine,
            schema='citygis',
            if_exists='append',
            index=False)
        gdf_trip.to_sql(
            name=temp_name_2,
            con=engine,
            schema='citygis',
            if_exists='append',
            index=False)

        # Afficher l'heure de fin de traitement.
        print('Fin de traitement a:',
              time.asctime(
                time.localtime(
                    time.time())))
        continue

connection.close()
