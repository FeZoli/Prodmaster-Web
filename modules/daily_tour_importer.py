#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *


sheetdata = {}
sheetdata['tour_location'] = 'B1'
sheetdata['tour_date']     = 'G1'

sheetdata['ostya_ledig_1'] = 'C4'
sheetdata['ostya_ledig_2'] = 'D4'
sheetdata['ostya_ledig_3'] = 'F4'
sheetdata['ostya_ledig_4'] = 'H4'

sheetdata['ostya_200_1']   = 'C6'
sheetdata['ostya_200_2']   = 'D6'
sheetdata['ostya_200_3']   = 'F6'
sheetdata['ostya_200_4']   = 'H6'

sheetdata['ostya_500_1']   = 'C7'
sheetdata['ostya_500_2']   = 'D7'
sheetdata['ostya_500_3']   = 'F7'
sheetdata['ostya_500_4']   = 'H7'

sheetdata['parany_300_1']  = 'C8'
sheetdata['parany_300_2']  = 'D8'
sheetdata['parany_300_3']  = 'F8'
sheetdata['parany_300_4']  = 'H8'

sheetdata['mandula_200_1'] = 'C9'
sheetdata['mandula_200_2'] = 'D9'
sheetdata['mandula_200_3'] = 'F9'
sheetdata['mandula_200_4'] = 'H9'

sheetdata['mezes_250_1']   = 'C10'
sheetdata['mezes_250_2']   = 'D10'
sheetdata['mezes_250_3']   = 'F10'
sheetdata['mezes_250_4']   = 'H10'

sheetdata['fagyi_30_1']    = 'C11'
sheetdata['fagyi_30_2']    = 'D11'
sheetdata['fagyi_30_3']    = 'F11'
sheetdata['fagyi_30_4']    = 'H11'

sheetdata['dietas_150_1']  = 'C12'
sheetdata['dietas_150_2']  = 'D12'
sheetdata['dietas_150_3']  = 'F12'
sheetdata['dietas_150_4']  = 'H12'

sheetdata['parany_ledig_1']= 'C13'
sheetdata['parany_ledig_2']= 'D13'
sheetdata['parany_ledig_3']= 'F13'
sheetdata['parany_ledig_4']= 'H13'

sheetdata['ostya_400_1']   = 'C14'
sheetdata['ostya_400_2']   = 'D14'
sheetdata['ostya_400_3']   = 'F14'
sheetdata['ostya_400_4']   = 'H14'

sheetdata['tortalap_160_1']= 'C16'
sheetdata['tortalap_160_2']= 'D16'
sheetdata['tortalap_160_3']= 'F16'
sheetdata['tortalap_160_4']= 'H16'

sheetdata['linzer_200_1']  = 'C18'
sheetdata['linzer_200_2']  = 'D18'
sheetdata['linzer_200_3']  = 'F18'
sheetdata['linzer_200_4']  = 'H18'

sheetdata['isler_200_1']   = 'C19'
sheetdata['isler_200_2']   = 'D19'
sheetdata['isler_200_3']   = 'F19'
sheetdata['isler_200_4']   = 'H19'

sheetdata['kgolyo_300_1']  = 'C20'
sheetdata['kgolyo_300_2']  = 'D20'
sheetdata['kgolyo_300_3']  = 'F20'
sheetdata['kgolyo_300_4']  = 'H20'

sheetdata['mandula_ledig_1']= 'C21'
sheetdata['mandula_ledig_2']= 'D21'
sheetdata['mandula_ledig_3']= 'F21'
sheetdata['mandula_ledig_4']= 'H21'

sheetdata['mezes_ledig_1']  = 'C23'
sheetdata['mezes_ledig_2']  = 'D23'
sheetdata['mezes_ledig_3']  = 'F23'
sheetdata['mezes_ledig_4']  = 'H23'

sheetdata['linzer_ledig_1'] = 'C24'
sheetdata['linzer_ledig_2'] = 'D24'
sheetdata['linzer_ledig_3'] = 'F24'
sheetdata['linzer_ledig_4'] = 'H24'

sheetdata['tour_deposit']   = 'C30'
sheetdata['tour_cash_1']    = 'D31'
sheetdata['tour_rabbat']    = 'C32'
sheetdata['tour_cash_2']    = 'D32'
sheetdata['tour_delayed_m'] = 'F32'
sheetdata['tour_delayed_w'] = 'F33'
sheetdata['tour_returned']  = 'C34'
sheetdata['tour_delayed_o'] = 'F34'

sheetdata['tour_brutto']     = 'C36'
sheetdata['tour_base']       = 'C37'


def get_raw_data(filename, import_day="1"):
    from openpyxl import load_workbook
    from openpyxl.shared.exc import CellCoordinatesException

    doc = load_workbook(filename=filename)
    sheet = doc.get_sheet_by_name(import_day)

    return sheet.rows # returns data on the given sheet


def import_ods_data(filename):
    import sys
    from odf.opendocument import load, Text
    from odf.table import Table, TableRow, TableCell, Body
    from odf.text import P, Date

    doc = load(filename)
    sheet = 0

    for tablesheet in doc.getElementsByType(Table):
        daily_data = {}
        row = 0
        outstr = ""
        for tablerow in tablesheet.getElementsByType(TableRow):
            column = 0
            for tablecell in tablerow.getElementsByType(TableCell):
                content = '#'
                for key, value in sheetdata.iteritems():
                    if value[0] == row and value[1] == column:
                        for txtObjs in tablecell.getElementsByType(P):
                            content = txtObjs.firstChild.__unicode__().encode('utf-8', 'ignore')
                            if content == None or content == "": content = "#"
                            break
                        daily_data[key] = (content,) # debug, row, column)
                        break
                column += 1
            row += 1

        if daily_data['tour_location'][0] != '#':
            monthly_data.append(daily_data)

        if sheet == 30: break
        sheet += 1

    return monthly_data
