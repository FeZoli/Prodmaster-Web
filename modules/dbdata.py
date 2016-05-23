#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import DAL

def get_db():
    return DAL('mysql://minux:nemerdekel@localhost/foodmaster', migrate=True)
