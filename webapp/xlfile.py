import click
from flask import current_app, g
from flask.cli import with_appcontext

import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Alignment, PatternFill, Border, Font # Side, Alignment, Protection,
from openpyxl.formatting import Rule
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.worksheet.datavalidation import DataValidation



def create_input_xl(contactinfo=None, specieslist=None, referencelist=None, traitlist=None, vocabularies=None):
    cent_align=Alignment(horizontal='center', vertical='center', wrap_text=False)
    wrap_align=Alignment(horizontal='left', vertical='top', wrap_text=True)
    sheet_colors = {"instructions": "1072BA" , "entry": "10BA72", "default":"505050"}
    table_style={"Instructions":TableStyleInfo(name="TableStyleMedium9", showFirstColumn=True, showLastColumn=False, showRowStripes=True, showColumnStripes=False),
             "Contributor": TableStyleInfo(name="TableStyleMedium18", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
             "Lists": TableStyleInfo(name="TableStyleMedium14", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
             "Info":  TableStyleInfo(name="TableStyleMedium14", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
             "Vocabularies": TableStyleInfo(name="TableStyleMedium14", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
             "Entry": TableStyleInfo(name="TableStyleMedium18", showFirstColumn=False, showLastColumn=False, showRowStripes=False, showColumnStripes=False)
             }
    wb = Workbook()
    ws = wb.active

    wsheets = (
    {"title": "Instructions", "colWidths":[("B",90),("C",40)], "tabColor":"instructions","active":True},
    {"title": "Contributor", "colWidths":[("A",30),("B",60)], "tabColor":"entry"},
    {"title": "Data entry", "colWidths":[(("A","B","C","E","G","I","N","O"),25), (("D","F","H","J","K","L","M"),12)], "tabColor":"entry"},
    {"title": "Species list", "colWidths":[(("A",),90),], "tabColor":"default"},
    {"title": "References", "colWidths":[("A",30),("B",60)], "tabColor":"default"},
    {"title": "Trait description", "colWidths":[("A",12),("B",30),("C",70)], "tabColor":"default"},
    {"title": "Vocabularies", "colWidths":[("A",30),("B",60)], "tabColor":"default"}

    )
    for item in wsheets:
        if "active" in item.keys():
            ws = wb.active
            ws.title = item['title']
        else:
            ws = wb.create_sheet(item['title'])
        for k in item['colWidths']:
            for j in k[0]:
                ws.column_dimensions[j].width = k[1]
        ws.sheet_properties.tabColor = sheet_colors[item["tabColor"]]

    ## instructions
    ws = wb["Instructions"]

    instructions = [
"""
Fill in your name and affilation in the "Contributor" tab, so that we can keep track of your contributions. Optionally fill in contact information for queries regarding your contribution.
""",
"""
Go to sheet "Data Entry" and fill one (or more) record(s) for each combination of reference + species + trait. Use "Insert > Table Rows Above/Below" to ensure new records have same format and validation options.
""",
"""
For each record, select references (main source and original sources columns) from the drop down list. If reference is not found, go to list of reference and add it to the table (use "Insert > Table Rows Above/Below" to add record to the list of references)
""",
"""
For each record, type in species name as given by main source in "original_species_name" column. A XLOOKUP function will look for a match in the species code table (list_spcode) and populate columns species_code and species_name, but this can be overridden with a manual entry if needed.
""",
"""
Select a trait from the drop down menu. A XLOOKUP function will look at the trait code table and populate columns for trait name and trait type (categorical or numerical). The choice will determine the list of values for the "norm_value" column.
""",
"""
Add raw value as given by original source, might include values, units and short explanatory text about observation or measurement.
""",
"""
For numeric trait values (e.g. age in years) we use a triplet of integer values (columns best, lower and upper) to describe a fuzzy number. Fill out any needed numbers and leave other columns blank. If in doubt leave all columns blank. Examples a raw value of "5 (3-7)" would be best:5, lower:3 upper:7; a value of ">5" would be lower:5, best:blank, upper:blank; etc. This column is colored red if the selected trait is not numerical.

For categorical variables, use values from drop-down list. The list will update when a categorical trait is selected and will be colored red if the selected trait is not categorical. If raw value does not match any of the options, leave blank. Values not in the dropdown list will not be imported in the database, but you can add a comment in the "notes" column.
""",
"""
Fill method of estimation from drop down list.
""",
"""
Add any notes, observations or comments in column "notes". Please avoid using colors or any other formatting, nor add comment on particular cells, rather write all comments as text in the "notes" column.
"""]

    links = [("#Contributor!A1","Go to 'Contributor' table"),
         ("#'Data entry'!A1","Go to 'Data Entry' table"),
         ("#'References'!A1","Go to 'References' table"),
         ("#'Species list'!A1","Go to 'Species list' table"),
         ("#'Trait description'!A1","Go to 'Trait description' table"),
         None,
         ("#'Vocabularies'!A1","Go to 'Vocabularies' table"),
         None,None,None]

    ws.append(["Step", "Instructions","Links"])
    for k in range(len(instructions)):
        ws.cell(k+2,1).value=k+1
        ws.cell(k+2,1).alignment=cent_align
        ws.cell(k+2,2).value=instructions[k]
        ws.cell(k+2,2).alignment=wrap_align
        if links[k] is not None:
            cell=ws.cell(k+2,3)
            cell.value=links[k][1]
            cell.hyperlink=links[k][0]
            cell.style = "Hyperlink"
    tab = Table(displayName="Instructions", ref="A1:C{}".format(len(instructions)+1))
    tab.tableStyleInfo = table_style["Instructions"]
    ws.add_table(tab)

    ## contributor
    ws = wb['Contributor']
    if contactinfo is None:
        contactinfo = {
            'Name': """ Your name """,
            'Affiliation': """ Your institution """,
            'Contact': """ e-mail or phone """
        }
    ws.append(["Field", "Your response"])
    for key in contactinfo.keys():
        ws.append((key,contactinfo[key]))
    tab = Table(displayName="Contributor", ref="A1:B4")
    tab.tableStyleInfo = table_style["Contributor"]
    ws.add_table(tab)

    ## Species list
    if specieslist is not None:
        ws = wb["Species list"]
        ws.append(["Scientific Name","Code"])
        for row in specieslist:
            ws.append(row)
        tab = Table(displayName="SpeciesList", ref="A1:B{}".format(ws.max_row))
        tab.tableStyleInfo = table_style["Lists"]
        ws.add_table(tab)

    ## Reference list
    if referencelist is not None:
        ws = wb["References"]
        ws.append(["Code", "Full reference"])
        for row in referencelist:
            ws.append(row)
        for k in range(2,ws.max_row+1):
            ws.cell(k,2).alignment=wrap_align
        tab = Table(displayName="References", ref="A1:B{}".format(ws.max_row))
        tab.tableStyleInfo = table_style["Lists"]
        ws.add_table(tab)

    ## Trait description
    if traitlist is not None:
        ws = wb["Trait description"]
        ws.append(["Trait Code", "Trait Name", "Description", "Type", "Life stage", "Life history process", "Priority"])
        for row in traitlist:
            ws.append(row)
        for k in range(2,ws.max_row+1):
            ws.cell(k,3).alignment=wrap_align
        tab = Table(displayName="TraitInformation", ref="A1:G{}".format(ws.max_row))
        tab.tableStyleInfo = table_style["Info"]
        ws.add_table(tab)

    ## Vocabularies
    if vocabularies is not None:
        ws = wb["Vocabularies"]
        k=1
        for record in vocabularies:
            ws.cell(row=k,column=1,value="Lookup table for trait %s" % record['code'])
            k=k+1
            tab_first_row=k
            ws.cell(row=k,column=1,value="Valid values")
            ws.cell(row=k,column=2,value="Description")
            vocab=record['vocab']
            for key in vocab.keys():
                k=k+1
                ws.cell(row=k,column=1,value=key)
                ws.cell(row=k,column=2,value=vocab[key])
                ws.cell(row=k,column=2).alignment=wrap_align
            tab_last_row=k
            tab = Table(displayName="lookup_%s" % record['code'], ref="A{}:B{}".format(tab_first_row,tab_last_row))
            tab.tableStyleInfo = table_style["Vocabularies"]
            ws.add_table(tab)
            k=k+2

    ## Data Entry
    ws = wb["Data entry"]
    nrows = 20
    hdr=["Main source", "Original sources", "Original species name", "Species code", "Species name",
               "Trait code", "Trait name","Trait type","Raw value", "Norm value",
               "Best", "Lower", "Upper", "Method of estimation","Notes"]
    ws.append(hdr)
    dv_ref = DataValidation(type="list",
                        formula1="""=INDIRECT("References[Code]")""",
                        allow_blank=True)

    dv_fuzzy = DataValidation(type="decimal",
                        operator="greaterThanOrEqual",
                        formula1=0)

    dv_trait = DataValidation(type="list",
                        formula1="""=INDIRECT("TraitInformation[Trait Code]")""")

    dv_vvalue = DataValidation(type="list",
                        formula1="""=INDIRECT(CONCATENATE("lookup_",$F2,"[Valid values]"))""")

    # custom error message
    dv_ref.error ='Your entry is not in the list'
    dv_ref.errorTitle = 'Invalid Entry'
    dv_trait.error ='Your entry is not in the list'
    dv_trait.errorTitle = 'Invalid Entry'

    # custom prompt message
    dv_ref.prompt = 'Please select from the list of references'
    dv_ref.promptTitle = 'List Selection'
    dv_vvalue.prompt = """For categorical traits, please select trait first and then select one value from the dropdown list, otherwise leave blank.
    For quantitative traits, leave blank and fill Best/Lower/Upper columns."""
    dv_vvalue.promptTitle = 'Accepted values for trait'

    # add validation ranges
    dv_ref.add("A2:A{}".format(nrows+1))
    dv_trait.add("F2:F{}".format(nrows+1))
    dv_fuzzy.add("K2:M{}".format(nrows+1))
    dv_vvalue.add("J2:J{}".format(nrows+1))

    ## add to sheet
    ws.add_data_validation(dv_vvalue)
    ws.add_data_validation(dv_ref)
    ws.add_data_validation(dv_trait)
    ws.add_data_validation(dv_fuzzy)

    for row in range(2,nrows+2):
        cell=ws.cell(row=row,column=7)
        cell.value="""=VLOOKUP($F{}, INDIRECT("TraitInformation"), 2, FALSE)""".format(cell.row)
        cell=ws.cell(row=row,column=8)
        cell.value="""=VLOOKUP($F{}, INDIRECT("TraitInformation"), 4, FALSE)""".format(cell.row)
        cell=ws.cell(row=row,column=4)
        cell.value="""=VLOOKUP($C{}, INDIRECT("SpeciesList"), 2, FALSE)""".format(cell.row)
        cell=ws.cell(row=row,column=5)
        cell.value="""=VLOOKUP($C{}, INDIRECT("SpeciesList"), 1, FALSE)""".format(cell.row)

    red_fill = PatternFill(bgColor="FFC7CE")
    dxf = DifferentialStyle(fill=red_fill)
    r = Rule(type="expression", dxf=dxf, stopIfTrue=True)
    r.formula = ['$H2="categorical"']
    ws.conditional_formatting.add("K2:M{}".format(nrows+1), r)

    r2 = Rule(type="expression", dxf=dxf, stopIfTrue=True)
    r2.formula = ['$H2="numerical"']
    ws.conditional_formatting.add("J2:J{}".format(nrows+1), r2)

    cell=ws.cell(row=nrows+1,column=len(hdr))
    tab = Table(displayName="DataEntry", ref="A1:{}{}".format(cell.column_letter,nrows+1))
    tab.tableStyleInfo = table_style["Entry"]
    ws.add_table(tab)

    return wb
