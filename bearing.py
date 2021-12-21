# -*- coding: utf-8 -*-


def bearing(max_bearing, gdf_trip, gdf_all_trips):
    '''
    Calcule l'azimut (bearing) des matchs et supprime les changements trop brusques au dela de max_bearing (ex: aller-retour sur un meme segment). 
    Utilise la fonction calculate_initial_compass_bearing cree par Jerome Renard et disponible sur github https://gist.github.com/jeromer/2005586
    '''

    for i in gdf_trip.index:
        if i < len(gdf_trip) - 1:
            # Structurer les lat/long pour la fonction.
            cur_point = (gdf_trip.loc[i, 'lat_match'],
                         gdf_trip.loc[i, 'long_match'])
            next_point = (gdf_trip.loc[i + 1, 'lat_match'],
                          gdf_trip.loc[i + 1, 'long_match'])

            # Calculer et enregistrer les azimuts dans le gdf. la
            # fonction calculate_initial_compass_bearing renvoie
            # l'azimut entre deux points en degre.
            gdf_trip.loc[i, 'bearing'] = \
                calculate_initial_compass_bearing(cur_point,
                                                  next_point)

        # Calculer la difference d'azimuts entre les matchs.
        for i in gdf_trip.index:
            if i < len(gdf_trip) - 1:
                # Recuperer les azimuts
                cur_bearing = gdf_trip.loc[i, 'bearing']
                next_bearing = gdf_trip.loc[i + 1, 'bearing']

                # Calculer la difference entre le courant et son
                # suivant.
                bearing_delta = cur_bearing - next_bearing

                # Enregistrer la valeur absolue.
                gdf_trip.loc[i,'bearing_delta']= abs_bearing_delta\
                                               = abs(bearing_delta)

                # Si le changement d'azimut est trop brusque,
                # marquer le point.
                if abs_bearing_delta > max_bearing:
                    # Enregistrer
                    gdf_trip.loc[i + 1, 'illegal_turn'] = \
                        gdf_all_trips['illegal_turn'] = True

        if 'illegal_turn' in gdf_trip:
            # Supprimer les matchs avec changement d'azimut trop
            # brusque.
            gdf_trip = gdf_trip[gdf_trip.illegal_turn != True]
            # Supprimer la colonne du gdf.
            del gdf_trip['illegal_turn']
            # Reindexer le gdf.
            gdf_trip = gdf_trip.reset_index(drop=True)

    return gdf_trip
