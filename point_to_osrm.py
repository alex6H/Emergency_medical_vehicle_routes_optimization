# -*- coding: utf-8 -*-
"""
Ce script recupere les donnees de position de la bd et les formates
pour la requete vers le serveur Open Source Routing Machine (OSRM).
La reponse d'OSRM est stockee dans la db en geojson.

"""
__authors__ = ("Alexis Huart")
__contact__ = ("alexis.huart@protonmail.com")
__date__ = "05/04/19"
__version__ = "6"

import requests
import psycopg2
import numpy as np
import pandas as pd
import geopandas as gpd
import sqlalchemy
import time

# Liste allant contenir les trips a traiter.
trips_id = []

# Compte des trips traites.
number_of_trip = 0

# Parametres du serveur OSRM. La reponse est en geojson.
serveur = 'http://192.168.56.101:5000'
tidy = 'true'
geometries = 'geojson'
steps = 'false'
overview = 'full'
gaps = 'ignore'
annotations = 'true'
radius_in_meter = '25;'

# Connexion a la DB avec psycopg2 et sqlAlchimy.
connection = psycopg2.connect("dbname='postgres' user='postgres' host='127.0.0.1' port = '5432' password=''")
engine = sqlalchemy.create_engine("postgresql://*********************")
cursor = connection.cursor()

# Tables contenant les points a traiter.
points_table = 'citygis.points'
table_name = points_table.replace('citygis.', '')

# Table allant contenir les trips.
osrm_trips_table = 'citygis.osrm_trips'
osrm_trips_name = osrm_trips_table.replace('citygis.', '')

# Recuperer la liste de trips a traiter (les id des trips sont
# repartis en 4 listes afin de beneficier des 4 cores du CPU.
with open('first24000.txt', 'r') as inputfile:
    trips_id = inputfile.readlines()

# Changer le type de str a int.
trips_id = list(map(int, trips_id))

# Recuperer la liste des trips deja traitee.
try:
    sql = """
            SELECT  DISTINCT trip_id
            FROM    {}
            """.format(osrm_trips_table)
    df_already_done = pd.read_sql_query(sql, connection)

except Exception:
    pass

for trip in trips_id:

    # Compte des trips traites.
    number_of_trip += 1

    # Afficher dans la console.
    print('trips_id:', trip)
    print('# du trips traite:', number_of_trip)

    # Suivi du temps.
    begin_start_time = time.time()

    # Suivi du temps de traitement.
    print('execution debutee a :', time.asctime(
        time.localtime(begin_start_time)))

    # Creer gdf_all_trips pour stocker les informations generales
    # sur le trip. Toutes les colonnes ne sont pas utiles a ce
    # stade. Elles seront deja crees dans la db et mise a jour dans
    # les porchains scripts.
    gdf_all_trips = gpd.GeoDataFrame(
        columns=[
            'trip_id',
            'geojson',
            'confidence',
            'radius',
            'osrm_msg',
            'geometry',
            'total_trip_length',
            'total_dtnm_length',
            'delta',
            'is_equality',
            'osrm_computation_time',
            'osrm_computation_time',
            'confidence_treshold',
            'error_range',
            'backward',
            'roundabout'])

    # Modifier le type par defaut
    gdf_all_trips['confidence'].astype(np.float64)

    # Enregistrer dans le df
    gdf_all_trips['trip_id'] = pd.Series(trip)
    gdf_all_trips['radius'] = radius_in_meter

    # Suivre le temps de traitement.
    start_time = time.time()

    # Listes pour le serveur OSRM.
    coord, timestamp, waypoint = [], [], []

    # Si le trip a deja ete traite passer au trip suivant.
    try:

        if trip in df_already_done.values:
            print('Trip deja traite.')
            continue

    except Exception:
        pass

   # Recuperer les donnees du trip a traiter.
    try:
        sql = """SELECT  point_id,
                        {}.timedate as time,
                        longitude,
                        latitude,
                        EXTRACT(EPOCH FROM{}.timedate) as timestamp
                FROM    {}
                WHERE   trips_id={}
                ORDER BY trips_id, timedate
                """.format(table_name, table_name, points_table, trip)
    except (Exception, psycopg2.Error) as error:
        print("Error to fetch data from trip:", error)

    # Injecter les informations du trip dans un nouveau gdf.
    gdf_trip = gpd.GeoDataFrame(
        pd.read_sql(sql, engine, index_col=None))

    # Afficher le nombre de points a matcher.
    print ('Nbr de points a matcher:', len(gdf_trip))

    # Formater les elements pour la requete a OSRM.
    for index in gdf_trip.index:

        # Recuperer les longitudes et latitudes.
        coord.append(gdf_trip.loc[index, 'longitude'])
        coord.append(',')
        coord.append(gdf_trip.loc[index, 'latitude'])
        coord.append(';')

        # Recuperer les timestamps.
        timestamp.append(gdf_trip.loc[index, 'timestamp'])
        timestamp.append(';')

        # Introduire le radius autant de fois qu'il y a de
        # coordonnees a matcher.
        radius = len(gdf_trip) * radius_in_meter

    # Fixer la premiere et la derniere coordonnee comme waypoint.
    waypoint.append('&waypoints=0;')
    waypoint.append(len(gdf_trip) - 1)

    # Formattage des donnees recuperees de la DB pour le serveur
    # OSRM.
    coord = str(coord).replace( '[','').replace(']','')\
            .replace("'",'').replace(" ",'').replace(",,,",',')\
            .replace(",;,",';')
    timestamp = str(timestamp).replace('[','').replace(']','')\
                .replace(".0",'').replace("'",'').replace(" ",'')\
                .replace(",;,",';')
    waypoint = str(waypoint).replace( '[','').replace(']','')\
                .replace("'",'').replace(" ",'').replace(",",'')

    # Creation de la requete OSRM.
    url = serveur + "/match/v1/driving/" + coord[:-2] + "?timestamps=" + str(timestamp[:-2]) + waypoint + "&tidy=" + tidy + "&geometries=" + geometries + "&steps=" + steps + "&overview=" + overview + "&gaps=" + gaps + "&annotations=" + annotations + "&radiuses=" + radius[:-1]

    # Recuperer la reponse OSRM et l'enregistrer.
    contents = requests.get(url)
    gdf_all_trips['geojson'] = contents.text

    # Calculer et enregistrer le temps de traitement du trip.
    computation_time = ((time.time()) - start_time)
    print('Traitement :', computation_time, 'sec')

    # Enregistrer 
    gdf_all_trips['osrm_computation_time'] = computation_time

    # Injecter les gdf dans la bd
    gdf_all_trips.to_sql(
        name=osrm_trips_name,
        con=engine,
        schema='citygis',
        if_exists='append',
        index=False)


connection.close()
