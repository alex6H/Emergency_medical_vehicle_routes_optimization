# -*- coding: utf-8 -*-
__authors__ = ("Alexis Huart")
__contact__ = ("alexis.huart@protonmail.com")
__date__ = "05/03/19"
__version__ = "5"

def same_from_to(df):
    """
    Cette fonction supprime les matchs supperposes.
    Ceux-ci genere des vitesses a zero km/h dans la suite 
    du script.
    """

    for i in df.index:
        # Recuperer les lat/long
        cur_long_from = df.loc[i,'long_from']
        cur_lat_from = df.loc[i, 'lat_from']
        cur_long_to = df.loc[i,'long_to'] 
        cur_lat_to = df.loc[i, 'lat_to']
        
        # Marquer les segments partant et arrivant aux memes
        # lat/long.
        if cur_long_from == cur_long_to \
        and cur_lat_from == cur_lat_to:
            # Enregistrer la similarite.
            df.loc[i, 'same_from_to'] = True

        # Ne pas evaluer la derniere ligne (elle n'a pas de
        # next_from/to).
        if i < len(df) - 1:
            # Recuperer les from/to
            cur_from = df.loc[i, 'osm_node_from']
            cur_to = df.loc[i, 'osm_node_to']
            next_from = df.loc[i + 1, 'osm_node_from']
            next_to = df.loc[i + 1, 'osm_node_to']

            # Marquer les segments partant et arrivant aux memes
            # noeuds OSM.
            if cur_from == cur_to \
            or (cur_from == next_from and cur_to == next_to):
                # Enregistrer la similarite.
                df.loc[i, 'same_from_to'] = True

    # Si la colonne existe dans le gdf
    if 'same_from_to' in df:
        
        # Supprimer les segments marques.
        df = df[df.same_from_to != True]

        # Reindexer le gdf
        df = df.reset_index(drop=True)

    return df
