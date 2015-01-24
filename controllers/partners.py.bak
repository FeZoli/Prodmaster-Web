# -*- coding: utf-8 -*-
# try something like

from gluon.tools import Crud

@auth.requires_login()
def index():
    
    l = SQLFORM.grid(db.partner, orderby='name')
    
    return dict(partner_list=l)
