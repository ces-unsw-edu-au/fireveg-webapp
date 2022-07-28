import pickle
import datetime


general_supporters = (
    {'institution':"University of New South Wales",'url':"https://www.unsw.edu.au/"},
    {'institution':"NSW Bushfire Research Hub",'url':"https://www.bushfirehub.org/"},
    {'institution':"NESP Threatened Species Recovery Hub",'url':"https://www.nespthreatenedspecies.edu.au/"},
    {'institution':"NSW Department of Planning & Environment",'url':"https://www.planning.nsw.gov.au/"}
)

general_info = (
    "Fire Ecology Traits for Plants",
    "Version 1.00 (April 2022)",
    "This data export reflects the status of the database on the %s" % datetime.date.today().strftime('%d %b %Y'),
    "Developed by  José R. Ferrer-Paris and David Keith",
    "Centre for Ecosystem Science / University of New South Wales",
    "Please cite this work as:",
    "Ferrer-Paris, J. R. and Keith, D. A. (2022) Fire Ecology Traits for Plants: A database for fire research and management. Version 1.00. Centre for Ecosystem Science, University of New South Wales, Sydney, Australia.",
    "DISCLAIMER:",
    "DATA IS NOT READY FOR FINAL USE OR CRITICAL APPLICATIONS AND YOU SHOULD NOT DISTRIBUTE THIS DATA."
    )

with open('content/common_data.pik', 'wb') as f:
  pickle.dump([general_supporters,general_info], f, -1)

output_wsheets = [
  {
    "title": "About",
    "colWidths":[("A",90),("B",40)],
    "tabColor":"intro",
    "active":True
  },
  {
    "title": "Summary",
    "colWidths":[("A",70),("B",10),(("C","D","E","F","G","H","I","J","K"),30),(("L","M","N",),25)],
    "tabColor":"summary"
  },
  {
    "title": "References",
    "colWidths":[("A",25),("B",80)],
    "tabColor":"addentry"
  },
  {
    "title": "Trait description",
    "colWidths":[("A",12),("B",30),("C",70)],
    "tabColor":"default"
  }
]

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


with open('content/output_summary_data.pik', 'wb') as f:
  pickle.dump([output_wsheets, output_description], f, -1)


input_wsheets = (
{"title": "Instructions", "colWidths":[("B",90),("C",40)], "tabColor":"instructions","active":True},
{"title": "Contributor", "colWidths":[("A",30),("B",60)], "tabColor":"entry"},
{"title": "Data entry", "colWidths":[(("A","B","C","E","G","I","N","O"),25), (("D","F","H","J","K","L","M"),12)], "tabColor":"entry"},
{"title": "References", "colWidths":[("A",30),("B",60)], "tabColor":"addentry"},
{"title": "Species list", "colWidths":[(("A","G","H"),90),(("C","D",),30),(("E","F","I"),25)], "tabColor":"default"},
{"title": "Trait description", "colWidths":[("A",12),("B",30),("C",70)], "tabColor":"default"},
{"title": "Vocabularies", "colWidths":[("A",30),("B",60)], "tabColor":"default"},
{"title": "Vocabularies for methods", "colWidths":[("A",30),("B",60)], "tabColor":"default"}

)

input_instructions = [
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

input_links = [("#Contributor!A1","Go to 'Contributor' table"),
         ("#'Data entry'!A1","Go to 'Data Entry' table"),
         ("#'References'!A1","Go to 'References' table"),
         ("#'Species list'!A1","Go to 'Species list' table"),
         ("#'Trait description'!A1","Go to 'Trait description' table"),
         None,
         ("#'Vocabularies'!A1","Go to 'Vocabularies' table"),
         None,None,None]

with open('content/data_entry_data.pik', 'wb') as f:
  pickle.dump([input_wsheets, input_instructions, input_links], f, -1)


## Define SQL queries


## These are general queries for categorical and numeric traits
qryCategorical= """
SELECT "currentScientificName" as spp, "currentScientificNameCode" as sppcode,
    array_agg(species) as nspp,
    array_agg(norm_value::text) as val,array_agg(weight) as w,
    array_agg(main_source) as refs,
    array_accum(original_sources) as orefs

FROM litrev.{}
LEFT JOIN species.caps
ON species_code="speciesCode_Synonym"
WHERE  "currentScientificName" is not NULL AND weight>0 AND main_source is not NULL
GROUP BY spp,sppcode;
"""
## WHERE species ilike '%euca%' and

qryNumeric= """
SELECT "currentScientificName" as spp, "currentScientificNameCode" as sppcode,
array_agg(species) as nspp,
array_agg(best) as best,array_agg(lower) as lower,array_agg(upper) as upper,array_agg(weight) as w,
array_agg(main_source) as refs,
array_accum(original_sources) as orefs
FROM litrev.{}
LEFT JOIN species.caps
ON species_code="speciesCode_Synonym"
WHERE "currentScientificName" is not NULL AND weight>0
GROUP BY spp,sppcode;
"""

## Other queries:

qryRefs="""
SELECT ref_code,ref_cite
FROM litrev.ref_list
WHERE ref_code IN %s
ORDER BY ref_code;
"""

qryTraits="""
SELECT code,name,description,value_type,life_stage,life_history_process,priority
FROM litrev.trait_info
ORDER BY code;
"""

qryAllRefs="""
SELECT ref_code,ref_cite
FROM litrev.ref_list;
"""

qrySomeTraits="""
SELECT code,name,description,value_type,life_stage,life_history_process,priority
FROM litrev.trait_info
WHERE priority IS NOT NULL
ORDER BY code;
"""

qrySpps="""
SELECT "scientificName", "speciesCode_Synonym", family, genus, "scientificNameID", "currentScientificNameCode", "currentScientificName", "currentVernacularName", "isCurrent"
FROM species.caps order by "sortOrder";
"""

qryVocabs="""
SELECT code, category_vocabulary, pg_catalog.obj_description(t.oid, 'pg_type')::json as vocab
FROM litrev.trait_info i
LEFT JOIN pg_type t
ON t.typname=i.category_vocabulary
WHERE category_vocabulary IS NOT NULL
ORDER BY code;
"""
qryMethodVocabs="""
SELECT code, method_vocabulary, pg_catalog.obj_description(t.oid, 'pg_type')::json as vocab
FROM litrev.trait_info i
LEFT JOIN pg_type t
ON t.typname=i.method_vocabulary
WHERE method_vocabulary IS NOT NULL
ORDER BY code;
"""

with open('content/sql_queries.pik', 'wb') as f:
  pickle.dump([qryCategorical, qryNumeric, qryRefs, qryTraits, qryAllRefs, qrySomeTraits, qrySpps, qryVocabs, qryMethodVocabs], f, -1)
