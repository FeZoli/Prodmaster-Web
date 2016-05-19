# -*- coding: utf-8 -*-

import local_settings

def index():
    r = db.product_subgroup_map
    maxtextlengths = {'product_subgroup_map.product': local_settings.product_name_max_length}
    
    grid = SQLFORM.grid(r,
                        create=True,
                        searchable=True,
                        csv=True,
                       maxtextlengths=maxtextlengths)

    return dict(grid=grid)
