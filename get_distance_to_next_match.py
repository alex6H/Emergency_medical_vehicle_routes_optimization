# -*- coding: utf-8 -*-
import numpy as np


def get_distance_to_next_match(gdf_edges, gdf_trip):
    '''
    A partir des distances calculees par la fonction distance_following_network,
    calcule de la vitesse entre chaque match.
    '''
    # Examiner chaque segment.
    for i in gdf_edges.index:

        # Si le segment est croise par un/des match(s).
        if gdf_edges.loc[i, 'edge_is_intesected']:

            # Examiner les matchs:
            for j in gdf_trip.index:

                # Si le match croise le segment et s'il n'est pas 
                # le dernier match (le dernier n'aura pas de
                # distance_to_next_match):
                if gdf_trip.loc[j,'edge_id_who_is_intersected']\
                == gdf_edges.loc[i,'edge_id'] \
                and j < (len(gdf_trip) - 1):

                    # Recuperer le nombre de match croisant le
                    # segment courant.
                    nb_of_point_who_intersect \
                        = gdf_edges.loc[i,'nb_point_who_intersect']

                    # Recuperer de la distance total du segment.
                    edge_length = gdf_edges.loc[i, 'edge_length']

                    # Recuperer la distance entre l'origine du
                    # segment et le match.
                    dist_from_start = \
                        gdf_trip.loc[j,'dist_from_edge_start']

                    # Calcul de la distance entre le match et la
                    # fin du segment.
                    cur_rest = edge_length - dist_from_start

                    # Recuperer dist_from_edge_start du prochain
                    # segment croise par un match.
                    next_dist_from_start = \
                        gdf_trip.loc[j + 1,'dist_from_edge_start']

                    # Recuperer les longueurs des segments sans
                    # match s'il en existe.
                    if 'total_next_edge_length_whitout_match' in gdf_trip:
                        dist_without_match = gdf_trip.loc[j, 'total_next_edge_length_whitout_match']

                    # Si un seul match croise le segment:
                    if nb_of_point_who_intersect == 1:

                        # Si le match courant ne chevauche pas deux
                        # segments et que le suivant oui:
                        if np.isnan(gdf_trip.loc[j, 'second_edge_id_who_is_intersected']) and np.isfinite(gdf_trip.loc[j + 1, 'second_edge_id_who_is_intersected']):
                            # Additionner la distance restante du
                            # segment precedent, les segments non
                            # croise intermediaire et la distance
                            # totale du segment du match suivant
                            # pour obtenir la distance 
                            # to next match.
                            gdf_trip.loc[j, 'distance_to_next_match'] = cur_rest + dist_without_match

                        # Si le match courant est a cheval sur deux
                        # segments et que le suivant l'est aussi:
                        if np.isfinite(gdf_trip.loc[j, 'second_edge_id_who_is_intersected']) and np.isfinite(gdf_trip.loc[j + 1, 'second_edge_id_who_is_intersected']):
                            gdf_trip.loc[j,'distance_to_next_match'] = dist_without_match

                        # Si le match courant ne chevauche pas deux
                        # segments.
                        elif np.isnan(gdf_trip.loc[j, 'second_edge_id_who_is_intersected']):
                            # Additionner la distance
                            # restante du segment precedent et les
                            # segments non croise intermediaire 
                            # pour obtenir la distance 
                            # to next match.
                            gdf_trip.loc[j, 'distance_to_next_match'] = cur_rest + next_dist_from_start + dist_without_match

                        # Si le match courant est a cheval sur deux
                        # segments.
                        else:
                            # Additionner les segments non croise
                            # intermediaire pour obtenir la 
                            # distance to next match et 
                            # la distance origine du prochain 
                            # segment vers prochain match.
                            gdf_trip.loc[j, 'distance_to_next_match'] = next_dist_from_start + \
                                dist_without_match

                    # Si plusieurs matchs croisent le meme segment.
                    elif nb_of_point_who_intersect > 1:

                        # Si le match n'est pas le dernier qui
                        # croise le segment.
                        if gdf_trip.loc[j,'order_of_match_on_same_edge'] < nb_of_point_who_intersect:
                            gdf_trip.loc[j,'distance_to_next_match'] = next_dist_from_start - dist_from_start

                        # Si le match est le dernier qui croise le
                        # segment.
                        elif gdf_trip.loc[j, 'order_of_match_on_same_edge'] == nb_of_point_who_intersect:
                            gdf_trip.loc[j, 'distance_to_next_match'] = cur_rest + next_dist_from_start + dist_without_match

                        # Afficher dans la console si un cas de
                        # figure n'est pas pris en compte.
                        else:
                            print('SomethingIsMissing_1')
                    else:
                        print('SomethingIsMissing_2')

    return [gdf_edges, gdf_trip]
