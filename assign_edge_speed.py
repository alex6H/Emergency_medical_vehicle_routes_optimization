# -*- coding: utf-8 -*-


def assign_edge_speed(gdf_edges, gdf_trip):
    '''
    Sur base des speed_to_next_match, cette fonction attribue une
    vitesse a chaque segment.
    '''
    # Derniere speed_tnm mise en memoire
    last_speed_to_next_match = 0

    # Examiner les segments.
    for i in gdf_edges.index:
        cur_edge_id = gdf_edges.loc[i, 'edge_id']

        # Si le segment est croise par un/des match(s).
        if gdf_edges.loc[i, 'edge_is_intesected']:
            cumul_of_section_speed = 0
            cur_edge_length = gdf_edges.loc[i, 'edge_length']

            # Examiner tout les matchs:
            for j in gdf_trip.index:
                cur_dtnm = gdf_trip.loc[j,'distance_to_next_match']
                cur_dfes = gdf_trip.loc[j, 'dist_from_edge_start']

                # Si le match evalue croise le segment courant ou 
                # le meme match croise un autre segment (cas ou un
                # match se trouve a la fin du premier et au debut
                # du second segment)
                if gdf_trip.loc[j,'edge_id_who_is_intersected'] == cur_edge_id or gdf_trip.loc[j,'second_edge_id_who_is_intersected'] == cur_edge_id:
                    per_100_from_edge_start = cur_dfes / cur_edge_length
                    rest_in_per_100 = 1 - per_100_from_edge_start
                    current_speed_tnm = gdf_trip.loc[j,'speed_to_next_match']

                    if j > 0:
                        last_speed_to_next_match = gdf_trip.loc[j - 1, 'speed_to_next_match']

                    nb_of_point_who_intersect = gdf_edges.loc[i, 'nb_point_who_intersect']
                    order_of_match_on_same_edge = gdf_trip.loc[j, 'order_of_match_on_same_edge']

                    # Si un seul match croise le segment:
                    if nb_of_point_who_intersect == 1:
                        # print('LA')
                        # Le premier match n'a pas de
                        # speed_to_next_match precedent
                        if j > 0:
                            section_1 = per_100_from_edge_start * last_speed_to_next_match
                            section_2 = rest_in_per_100 * current_speed_tnm
                            gdf_edges.loc[i,'edge_speed'] = section_1 + section_2
                            
                        # Le segment comprenant le premier match
                        # recupere le speed_to_next_match en
                        # totalite
                        else:
                            gdf_edges.loc[i,'edge_speed'] = current_speed_tnm

                    # Si plusieurs matchs croisent le meme segment:
                    elif nb_of_point_who_intersect > 1:
                        # print('ICI')
                        # Traiter le premier match du segment:
                        if order_of_match_on_same_edge == 1:
                            # Calculer la vitesse entre l'origine 
                            # du segment et le premier match
                            first_section = per_100_from_edge_start * last_speed_to_next_match
                            # Calculer la vitesse entre le premier
                            # match et le second
                            per_100_of_second_section = cur_dtnm / cur_edge_length
                            second_section = per_100_of_second_section * current_speed_tnm

                        # Traiter les matchs du segment sauf le
                        # premier et dernier
                        elif 1 < order_of_match_on_same_edge < nb_of_point_who_intersect:
                            per_100_of_edge_length = cur_dtnm / cur_edge_length
                            in_between_section = per_100_of_edge_length * current_speed_tnm
                            cumul_of_section_speed += in_between_section

                        # Le match est le dernier qui croise le
                        # segment
                        elif order_of_match_on_same_edge == nb_of_point_who_intersect:
                            # Calculer la vitesse entre le dernier
                            # match et la fin du segment
                            last_section = rest_in_per_100 * current_speed_tnm
                            # Additionner les vitesses des sections
                            # et les enregistrer
                            gdf_edges.loc[i, 'edge_speed'] = first_section + second_section + cumul_of_section_speed + last_section

                        else:
                            print('SomethingIsMissing_3')
                    else:
                        print('SomethingIsMissing_4')

        # Si le segment n'est pas croise par un match:
        elif gdf_edges.loc[i, 'edge_is_intesected'] == False:
            # La vitesse attribuee est celle qui correspond au
            # speed_to_next_match du match precedent
            gdf_edges.loc[i,'edge_speed'] = last_speed_to_next_match

    return [gdf_edges, gdf_trip]
