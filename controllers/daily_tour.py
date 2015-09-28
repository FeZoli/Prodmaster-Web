# -*- coding: utf-8 -*-

import daily_tour_importer

def index(): return dict(message="hello from daily_tour.py")


def import_data():
    import shutil
    if request.vars:
        filename = request.vars.upload.filename
        file = request.vars.upload.file
        filename = 'applications/FoodMaster/daily_tour_data/' + filename
        shutil.copyfileobj(file, open(filename, 'wb'))

    return dict(data=daily_tour_importer.show_importable_days(filename))
