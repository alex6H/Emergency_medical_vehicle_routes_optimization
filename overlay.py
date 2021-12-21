# -*- coding: utf-8 -*-


def overlay(gdf_trip):
    '''
    La fonction rechercher des matchs se supperposant et supprimer le premier.
    '''
    for i in range(len(gdf_trip) - 1):
        long_match = gdf_trip.loc[i, 'long_match']
        next_long_match = gdf_trip.loc[i + 1, 'long_match']
        lat_match = gdf_trip.loc[i, 'lat_match']
        next_lat_match = gdf_trip.loc[i + 1, 'lat_match']

        if long_match == next_long_match and lat_match == next_lat_match:
            gdf_trip.loc[i, 'overlay'] = True
        else:
            gdf_trip.loc[i, 'overlay'] = False

    # Supprimer les overlay.
    gdf_trip = gdf_trip[gdf_trip.overlay != True]

    # Reindexer le gdf.
    gdf_trip = gdf_trip.reset_index(drop=True)

    return gdf_trip
