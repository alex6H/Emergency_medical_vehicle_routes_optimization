# -*- coding: utf-8 -*-

def edge_intersect_by_match (gdf_edges,gdf_trip) :
    '''
    Cette fonction determine si les segments sont croises par des matchs et inversement. Si un match ne croise pas de segment, il est supprime.
    '''
    # Pour chaque segment.
    for i in gdf_edges.index:
        current_edge = gdf_edges.loc[i,'geometry']
        current_edge_id = gdf_edges.loc[i,'edge_id']
        
        # Examiner chaque match.
        for j in gdf_trip.index:
            current_point = gdf_trip.loc[j,'geometry']
            
            # Recherche si le match croise le segment avec un 
            # buffer de 10cm (le buffer compense les imprecisions
            # de projection).
            edge_is_intersected_by_match = current_edge\
                .intersects(current_point.buffer(0.1)) 
            
            # Si il y a croisement, annoter les segments et matchs.
            if edge_is_intersected_by_match is True :
                gdf_trip.loc[j,'edge_id_intersected'] \
                    = current_edge_id
                gdf_edges.loc[i,'edge_is_intesected'] \
                    = gdf_trip.loc[j,'point_is_intersected']\
                    = True
                                  
    #Si des segments sont croises par des matchs.
    if 'edge_id_intersected' in gdf_trip :
        # Supprimer les eventuels matchs qui ne croisent plus
        # de segment suite aux filtres.
        gdf_trip = gdf_trip.dropna(axis=0, 
                                   how='any', 
                                   subset=['edge_id_intersected'])
        # Reindexer le gdf.
        gdf_trip = gdf_trip.reset_index(drop=True)
    
    return [gdf_edges,gdf_trip]
