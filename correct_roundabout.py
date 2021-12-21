# -*- coding: utf-8 -*-
import pandas as pd


def s_to_df(my_series):
    '''
    Transforme une serie en dataframe
    '''
    return pd.DataFrame({'index_i': my_series.index,
                         'index_j': my_series.values})


def correct_roundabout(df):
    '''
    Cette fonction corrige les multiples tours d'un carrefour ou
    d'un rond point.
    '''
    # Compte du nombre de loop.
    count = 0

    # Generer un df avec des valeurs quelconques.
    df_list_cor = pd.DataFrame(
        {'index_i': [1, 2, 3], 'index_j': [1, 2, 3]})

    # Recommencer tant qu'il y a des doublons.
    while df_list_cor.empty is False:
        I = []
        J = []

        # Evaluer tout les couples de noeuds from to a eux memes.
        for index_i, i_from, i_to in zip(df.index, 
                                         df.osm_node_from, 
                                         df.osm_node_to):
            for index_j, j_from, j_to in zip(df.index, 
                                             df.osm_node_from, 
                                             df.osm_node_to):

                # Extraire les doublons de segment et ajouter
                # dans une liste.
                if (i_from, i_to) == (j_from, j_to)\
                and (index_i != index_j)\
                and (index_i < index_j):
                    I.append(index_i)
                    J.append(index_j)

        # Integrer les listes dans un df.
        DATA = {'index_i': I, 'index_j': J}
        df_list_loops = pd.DataFrame(DATA)

        # Isoler la valeur maximum par index_i.
        df_list_cor = s_to_df(
            df_list_loops.groupby(
                ['index_i'],
                sort=False)['index_j'].max())

        # Supprimer les segments entre les noeuds en doubles.
        df = df.drop(df.index[(df_list_cor['index_i'].iloc[0] +1):
                              (df_list_cor['index_j'].iloc[0] +1)])
        count += 1

        # Reindexer le gdf.
        df = df.reset_index(drop=True)

        # Afficher dans la console.
        print ('Nombre de loop:', count)
    
    return df
