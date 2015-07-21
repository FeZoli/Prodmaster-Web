# -*- coding: utf-8 -*-

@auth.requires(auth.has_membership(role='general manager') or
               auth.has_membership(role='public market manager'))
def index():

    grid = SQLFORM.grid(db.market_cassa,
                        deletable=False,
                        editable=True,
                        onvalidation=cassa_validate,
                        orderby=~db.market_cassa.id)
    session.flash=""

    return dict(grid=grid)


def cassa_validate(form):

    #### check whether user wants to modify a record other than the last one
    if request.args(0) == 'edit':
        next_row = db(db.market_cassa.id>request.args(2)).select(db.market_cassa.id,
                                                                 orderby=~db.market_cassa.id,
                                                                 limitby=(0,1)).first()

        last_movement_amount = db(db.market_cassa.id==request.args(2)).select(db.market_cassa.movement_amount)[0].movement_amount

        if next_row and last_movement_amount != form.vars.movement_amount:
            form.errors.movement_amount = T("Cannot modify amount in a record other than the last one!")
        else:
            form = modify_form(form, request.args(2))

    elif request.args(0) == 'new':
        form = modify_form(form)


def cassa_update(form):
    form = modify_form(form, request.args(2))
    return


def modify_form(form, rid=0):

    q = None

    if rid == 0:
        q = db.market_cassa.id>0
    elif rid > 0:
        q = db.market_cassa.id<rid

    prev_row = db(q).select(db.market_cassa.id,
                            db.market_cassa.balance_after,
                            orderby=~db.market_cassa.id,
                            limitby=(0,1)).first()

    form.vars.balance_before = 0
    if prev_row:
        form.vars.balance_before = prev_row.balance_after

    form.vars.balance_after = form.vars.movement_amount + form.vars.balance_before


    
    
    return form
