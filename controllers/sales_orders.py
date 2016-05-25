# -*- coding: utf-8 -*-

import local_settings


def index():
    q = db.sales_order
    mos = SQLFORM.smartgrid(q,
                            linked_tables=['sales_order_item'],
                            maxtextlengths={'sales_order.partner' : local_settings.partner_name_max_length},
                            orderby='status, delivery_date',
                            deletable=False)

    return dict(mos=mos)
