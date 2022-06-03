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
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
import pandas as pd

import datetime

# common stuff
cent_align=Alignment(horizontal='center', vertical='center', wrap_text=False)
wrap_align=Alignment(horizontal='left', vertical='top', wrap_text=True)
sheet_colors = {"instructions": "1072BA" , "intro": "1072BA" , "entry": "10BA72", "summary": "5AFF5A", "addentry": "20CA82", "default":"505050"}
fontSmall = Font(size = "9")
table_style={"Instructions":TableStyleInfo(name="TableStyleMedium9", showFirstColumn=True, showLastColumn=False, showRowStripes=True, showColumnStripes=False),
         "Contributor": TableStyleInfo(name="TableStyleMedium18", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
         "Lists": TableStyleInfo(name="TableStyleMedium14", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
         "Info":  TableStyleInfo(name="TableStyleMedium14", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
         "Vocabularies": TableStyleInfo(name="TableStyleMedium14", showFirstColumn=True, showLastColumn=False, showRowStripes=False, showColumnStripes=False),
         "Entry": TableStyleInfo(name="TableStyleMedium18", showFirstColumn=False, showLastColumn=False, showRowStripes=False, showColumnStripes=False)
         }

## Update this content if necessary
output_info = ("Fire Ecology Traits for Plants",
        "Version 1.00 (April 2022)",
        "This data export reflects the status of the database on the %s" % datetime.date.today().strftime('%d %b %Y'),
        "Developed by  José R. Ferrer-Paris and David Keith",
        "Centre for Ecosystem Science / University of New South Wales",
        "Please cite this work as:",
        "Ferrer-Paris, J. R. and Keith, D. A. (2022) Fire Ecology Traits for Plants: A database for fire research and management. Version 1.00. Centre for Ecosystem Science, University of New South Wales, Sydney, Australia.",
        "DISCLAIMER:",
        "DATA IS NOT READY FOR FINAL USE OR CRITICAL APPLICATIONS AND YOU SHOULD NOT DISTRIBUTE THIS DATA."
        )

output_wsheets = (
{"title": "About", "colWidths":[("A",90),("B",40)], "tabColor":"intro","active":True},
{"title": "Summary", "colWidths":[("A",70),("B",10),(("C","D","E","F","G","H","I","J","K"),30),(("L","M","N",),25)], "tabColor":"summary"},
{"title": "References", "colWidths":[("A",25),("B",80)], "tabColor":"addentry"},
{"title": "Trait description", "colWidths":[("A",12),("B",30),("C",70)], "tabColor":"default"}
)

output_supporters = ({'institution':"University of New South Wales",'url':"https://www.unsw.edu.au/"},
              {'institution':"NSW Bushfire Research Hub",'url':"https://www.bushfirehub.org/"},
              {'institution':"NESP Threatened Species Recovery Hub",'url':"https://www.nespthreatenedspecies.edu.au/"},
              {'institution':"NSW Department of Planning & Environment",'url':"https://www.planning.nsw.gov.au/"})


output_description = {"about": (
              "Taxonomic nomenclature following BioNET (data export from February 2022)",
              "Data in the report is summarised based on BioNET fields 'currentScientificName' and 'currentScientificNameCode'",
              "For general description of the traits, please refer to the 'Trait description' sheet",
              "Vocabularies for categorical traits are available in the 'Vocabularies' sheet",
              "For categorical traits the values in the 'Summary' sheet show the different values reported in the literature records separated by slashes.",
               "If more than one category has been reported, the values are ordered from higher to lower 'weight', categories receiving less than 10% weight are in round brackets, categories with less than 5% in square brackets",
              "The default weight is calculated by multiplying the number of times a value is reported (nr. of records) with the weight given to each record (default to 1), and divided by the weight of all records for a given species.",
              "Default weights  overridden by expert advice to the administrator will be marked, with justification given in the Notes column of the output.",
              "An asterisk (*) in a trait cell indicates a potential data entry error or uncertainty in the assignment of a trait category or value.",
              "'Import/Entry sources' refer to references that were imported directly using automated scripts or manual entry. These include: 1) Primary observations of traits from published research or reports; and 2) Compilations of data (e.g. databases, spreadsheets, published reviews) that include two or more sources of primary observations.",
              "'Indirect sources' refer to references that were cited in Import/Entry sources, where the latter are compilations of multiple primary sources (see Import/Entry sources). Information from indirect sources may have been modified when it was incorporated into those compilations. The original source of primary trait observations has not yet been verified prior to import into this database. When the primary source is reviewed and the trait values are verified, these records will be attributed to the primary source as 'Import/Entry sources'.",
              "Some sheets are protected to avoid accidental changes, but they are not password protected. If you need to filter and reorder entries in the table, please unprotect the sheet first.",
              ),
                "traits":("The following table gives a general description of the traits used in the 'Summary' sheet",
                               "This sheet is protected to avoid accidental changes, but it is not password protected. If you need to filter and reorder entries in the table, please unprotect the sheet first.",
                              "Vocabularies for categorical traits are available in the 'Vocabularies' sheet","",""),
                "references":("The following table includes bibliographical information for the sources referenced in the 'Summary' sheet","This sheet is protected to avoid accidental changes, but it is not password protected. If you need to filter and reorder entries in the table, please unprotect the sheet first.", "","")}



def create_output_xl(traitsummary=None, referencelist=None, traitlist=None, info=output_info, wsheets=output_wsheets, description=output_description, supporters=output_supporters):
    wb = Workbook()
    ws = wb.active

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

    ## About
    ws = wb["About"]
    k = 1
    for row in info:
        ws.cell(k,1,value=row)
        ws.cell(k,1).alignment=wrap_align
        k=k+1
    ## check these if info was updated/changed
    ws.cell(1,1).style='Title'
    ws.cell(5,1).hyperlink='https://www.unsw.edu.au/research/ecosystem'
    ws.cell(5,1).style='Hyperlink'
    # Disclaimer, check these if info was updated/changed
    ws.cell(8,1).font=Font(color="FF0000", bold=True,italic=False)
    ws.cell(9,1).font=Font(color="FF0000", italic=True)
    k=k+2
    ws.cell(k-1,1,value="This work has been supported by:")
    for item in supporters:
        cell=ws.cell(k,1)
        cell.value=item['institution']
        cell.hyperlink=item['url']
        cell.style = "Hyperlink"
        k=k+1
    k=k+2
    for row in description['about']:
        ws.cell(k,1,value=row)
        ws.cell(k,1).alignment=wrap_align
        k=k+1
    ws.protection.sheet = True

    ## Trait Description
    ws = wb["Trait description"]
    k=1
    for row in description['traits']:
        ws.cell(k,3,value=row)
        ws.cell(k,3).alignment=wrap_align
        k=k+1
    ws.append(["Trait Code", "Trait Name", "Description", "Type", "Life stage", "Life history process", "Data migration"])
    for row in traitlist:
        ws.append(row)
    #ws.max_row
    for j in range(k,ws.max_row+1):
        ws.cell(j,3).alignment=wrap_align
    tab = Table(displayName="TraitInformation", ref="A{}:G{}".format(k,ws.max_row))
    tab.tableStyleInfo = table_style["Info"]
    ws.add_table(tab)
    ws.protection.sheet = True

    ## Summary
    ws = wb["Summary"]
    ws.append(['Species','Code','surv1','surv4','germ1','germ8','rect2','repr2','repr3','repr3a','disp1','Original Species name(s) used','Import/Entry sources','Indirect sources'])
    rows = dataframe_to_rows(traitsummary[['Species','Code','surv1','surv4','germ1','germ8','rect2','repr2','repr3','repr3a','disp1','orig_species','main_refs','orig_refs']],index=False, header=False)
    #rows = dataframe_to_rows(traitsummary,index=False, header=False)
    for r_idx, row in enumerate(rows, 2):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)
        for k in (12,13,14):
            ws.cell(r_idx,k).alignment=wrap_align
            ws.cell(r_idx,k).font = fontSmall
    tab = Table(displayName="Summary", ref="A1:{}{}".format(get_column_letter(c_idx),r_idx))
    tab.tableStyleInfo = table_style["Lists"]
    ws.add_table(tab)

    ## References
    ws = wb["References"]
    k=1

    for row in description['references']:
        ws.cell(k,2,value=row)
        ws.cell(k,2).alignment=wrap_align
        k=k+1
    ws.append(["Reference code", "Reference information"])
    for row in referencelist:
        ws.append(row)
    #ws.max_row
    for j in range(k+1,ws.max_row+1):
        ws.cell(j,2).alignment=wrap_align
        ws.cell(j,2).font = fontSmall
    tab = Table(displayName="ReferenceInformation", ref="A{}:B{}".format(k,ws.max_row))
    tab.tableStyleInfo = table_style["Lists"]
    ws.add_table(tab)
    ws.protection.sheet = True

    ## Finalise and return
    return wb

def create_input_xl(contactinfo=None, specieslist=None, referencelist=None, traitlist=None, vocabularies=None, methods_vocabularies=None):
    wb = Workbook()
    ws = wb.active

    wsheets = (
    {"title": "Instructions", "colWidths":[("B",90),("C",40)], "tabColor":"instructions","active":True},
    {"title": "Contributor", "colWidths":[("A",30),("B",60)], "tabColor":"entry"},
    {"title": "Data entry", "colWidths":[(("A","B","C","E","G","I","N","O"),25), (("D","F","H","J","K","L","M"),12)], "tabColor":"entry"},
    {"title": "References", "colWidths":[("A",30),("B",60)], "tabColor":"addentry"},
    {"title": "Species list", "colWidths":[(("A","G","H"),90),(("C","D",),30),(("E","F","I"),25)], "tabColor":"default"},
    {"title": "Trait description", "colWidths":[("A",12),("B",30),("C",70)], "tabColor":"default"},
    {"title": "Vocabularies", "colWidths":[("A",30),("B",60)], "tabColor":"default"},
    {"title": "Vocabularies for methods", "colWidths":[("A",30),("B",60)], "tabColor":"default"}

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
Fill in your name, affilation and contact details in the "Contributor" tab, so that we can keep track of your contributions and contact you with any queries.
""",
"""
Go to sheet "Data Entry" and fill one (or more) record(s) for each combination of reference + species + trait.
""",
"""
For each record, select references (main source and original sources columns) from the drop down list. If reference is not found, go to list of reference and add it to the table (use "Insert > Table Rows Above/Below" to add record to the list of references)
""",
"""
For each record, type in species name as given by main source in "original_species_name" column. A XLOOKUP function will look for a match in the species table (SpeciesList) and populate columns species_code and species_name, but this can be overridden with a manual entry if needed.

The data in the Species List is taken from BioNET (export from February 2022). The Species Code used in the data entry worksheet comes from the 'speciesCode_Synonym' column in BioNET.

The 'Species list' worksheet is locked to avoid accidental changes, but it is not password protected, so you should be able to unlock the sheet for filtering and sorting.
""",
"""
Select a trait from the drop down menu. A XLOOKUP function will look at the trait code table and populate columns for trait name and trait type (categorical or numerical). The choice will determine the list of values for the "norm_value" column. The 'Trait description' worksheet is locked to avoid accidental changes, but it is not password protected, so you should be able to unlock the sheet for filtering and sorting.
""",
"""
Add raw value as given by original source, might include values, units and short explanatory text about observation or measurement.
""",
"""
For numeric trait values (e.g. age in years) we use a triplet of integer values (columns best, lower and upper) to describe a fuzzy number. Fill out any needed numbers and leave other columns blank. If in doubt leave all columns blank. Examples a raw value of "5 (3-7)" would be best:5, lower:3 upper:7; a value of ">5" would be lower:5, best:blank, upper:blank; etc. This column is colored red if the selected trait is not numerical.

For categorical variables, use values from drop-down list. The list will update when a categorical trait is selected and will be colored red if the selected trait is not categorical. If raw value does not match any of the options, leave blank. Values not in the dropdown list will not be imported in the database, but you can add a comment in the "notes" column.

The 'Vocabularies' and 'Vocabularies for methods' worksheets are locked to avoid accidental changes, but they are not password protected, so you should be able to unlock the sheet for filtering and sorting.
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
        ws.append(["Scientific Name","Code","Family", "Genus", "Scientific Name ID in BioNET", "current Scientific Name Code", "Current Scientific Name", "Current Vernacular Name", "is Current?"])
        for row in specieslist:
            ws.append(row)
        tab = Table(displayName="SpeciesList", ref="A1:B{}".format(ws.max_row))
        tab.tableStyleInfo = table_style["Lists"]
        ws.add_table(tab)
        ws.protection.sheet = True

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
        ws.protection.sheet = True

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
        ws.protection.sheet = True

    ## methods Vocabularies
    if methods_vocabularies is not None:
        ws = wb["Vocabularies for methods"]
        k=1
        for record in methods_vocabularies:
            ws.cell(row=k,column=1,value="Available methods for trait %s" % record['code'])
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
            tab = Table(displayName="method_%s" % record['code'], ref="A{}:B{}".format(tab_first_row,tab_last_row))
            tab.tableStyleInfo = table_style["Vocabularies"]
            ws.add_table(tab)
            k=k+2
        ws.protection.sheet = True

    ## Data Entry
    ws = wb["Data entry"]
    nrows = 200
    hdr=["Main source", "Original sources", "Original species name", "Species code", "Species name", "Trait code", "Trait name","Trait type","Raw value", "Norm value", "Best", "Lower", "Upper", "Method of estimation","Notes"]
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
    dv_mvalue = DataValidation(type="list",
                    formula1="""=INDIRECT(CONCATENATE("method_",$F2,"[Valid values]"))""")

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
    dv_mvalue.prompt = """Please select a valid method for this trait from the dropdown list. Leave blank if no options available."""
    dv_mvalue.promptTitle = 'Accepted values for method'

    # add validation ranges
    dv_ref.add("A2:A{}".format(nrows+1))
    dv_trait.add("F2:F{}".format(nrows+1))
    dv_fuzzy.add("K2:M{}".format(nrows+1))
    dv_vvalue.add("J2:J{}".format(nrows+1))
    dv_mvalue.add("N2:N{}".format(nrows+1))

    ## add to sheet
    ws.add_data_validation(dv_vvalue)
    ws.add_data_validation(dv_mvalue)
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

    #r3 = Rule(type="expression", dxf=dxf, stopIfTrue=True)
    # which formula allows to test if table exists?
    #r3.formula = ['=ISNUMBER(ROWS(INDIRECT(CONCATENATE("method_",$F2))))'] # formula for counting rows in a table
    #ws.conditional_formatting.add("N2:N{}".format(nrows+1), r2)

    cell=ws.cell(row=nrows+1,column=len(hdr))
    tab = Table(displayName="DataEntry", ref="A1:{}{}".format(cell.column_letter,nrows+1))
    tab.tableStyleInfo = table_style["Entry"]
    ws.add_table(tab)

    return wb
