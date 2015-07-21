# -*- coding: utf-8 -*-

@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='public market manager'))
def index():

    return dict(grid=SQLFORM.grid(db.market_event_category,
                                  orderby=db.market_event_category.name))
