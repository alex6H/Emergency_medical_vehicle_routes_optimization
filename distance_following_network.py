# -*- coding: utf-8 -*-


def distance_following_network(gdf_edges, gdf_trip):
    '''
    #Calculer les distances entre les matchs en suivant le reseau.
    '''

    # Variable de distance sans match..
    dist_without_match = 0

    # Examiner chaque segment.
    for i in gdf_edges.index:
        # Variables de compte.
        false_count = count_point_who_intesect = 0

        # Recuperer les donnees des segments.
        cur_edge = gdf_edges.loc[i, 'geometry']
        cur_edge_id = gdf_edges.loc[i, 'edge_id']

        # Calculer la longueur total du segment.
        edge_length = gdf_edges.loc[i,'edge_length']\
                    = (cur_edge).length

        # Examiner chaque point matche.
        for j in gdf_trip.index:
            # Recuperer les donnees du match courant.
            cur_point = gdf_trip.loc[j, 'geometry']

            # Enregistrer si le segment a rencontre un premier
            # match ou non.
            edge_id_intersected = \
                gdf_trip.loc[j,'edge_id_intersected']

            # Si le match croise le segment traite.
            if cur_edge_id == edge_id_intersected:
                
                # Compter le nombre de match qui croise le segment.
                count_point_who_intesect += 1

                # Enregistrer l'ordre du match sur le segment.
                gdf_trip.loc[j,'order_of_match_in_same_edge'] = \
                    count_point_who_intesect

                # Calculer la distance entre l'origine du segment
                # et le match.
                gdf_trip.loc[j, 'dist_from_edge_start'] = \
                    cur_edge.project( cur_point)

                # Traiter le premier segment du trajet.
                if i == 0:
                    # Enregistrer l'id du segment que le match
                    # croise.
                    gdf_trip.loc[j,'edge_id_who_is_intersected']=\
                    cur_edge_id

                # Traiter les segments suivants.
                else:
                    # Si un match croise deux segments consecutifs
                    # (match positione a 100% sur le premier
                    # segment et a 0% du second) alors les edge_id
                    # sont enregistres dans deux colonnes separees.
                    if gdf_trip.loc[j,'edge_id_who_is_intersected'] == gdf_edges.loc[i - 1,'edge_id']:
                        # Enregistrer l'id du segment qui croise le
                        # match dans une seconde colonne
                        gdf_trip.loc[j,'second_edge_id_who_is_intersected'] = cur_edge_id

                        # Puisque le match est a  0% sur le second
                        # segment, il faut inclure la distance du
                        # premier segment dans 
                        # la dist_without_match
                        dist_without_match += edge_length

                        # Sauf pour le premier segment et s'il
                        # existe des segments precedent n'ayant pas
                        # croise de match.
                        if j > 0 \
                        and 'total_next_edge_length_whitout_match'\
                        in gdf_trip:
                            # Ajouter la longueur du segment
                            # precedent a  dist_without_match
                            # precedente.
                            gdf_trip.loc[j -1, 'total_next_edge_length_whitout_match'] += gdf_edges.loc[i - 1, 'edge_length']

                        # Enregistrer le nombre de match croisant
                        # chaque edge
                        gdf_edges.loc[i,'nb_point_who_intersect'] = count_point_who_intesect

                    # Si le match evalue ne croise qu'un seul
                    # segment.
                    else:

                        # Enregistrer l'id du segment que le match
                        # croise.
                        gdf_trip.loc[j,'edge_id_who_is_intersected'] = cur_edge_id

                        # Sauf pour le premier segment et s'il
                        # existe des segments precedent n'ayant pas
                        # croise de match.
                        if 0 < j:
                            # Enregistrer les distances des 
                            # segments sans match precedent 
                            # le match courant.
                            gdf_trip.loc[j - 1,'total_next_edge_length_whitout_match'] = dist_without_match

                            # Remise a  zero des distances sans
                            # match puisque le segment est croise
                            # par un match.
                            dist_without_match = 0

            # Si le match ne croise pas le segment evalue.
            elif edge_id_intersected != cur_edge_id:
                # Compter le nombre de match qui ne croisent pas le
                # segment
                false_count += 1

                # Si le segment evalue n'a aucun match qui le
                # croise.
                if false_count == len(gdf_trip):
                    gdf_edges.loc[i, 'edge_is_intesected'] = False

                    # Collecter la longueurs du segments evalue
                    dist_without_match += edge_length

            # Enregistrer le nombre de match croisant chaque
            # segment.
            gdf_edges.loc[i,'nb_point_who_intersect'] \
                = count_point_who_intesect

    return [gdf_edges, gdf_trip]
