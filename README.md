# Fire Ecology Traits for Plants

The ***Fire Ecology Traits for Plants*** project is being developed by  [José R. Ferrer-Paris](https://github.com/jrfep) and David Keith in the Centre for Ecosystem Science, University of New South Wales

Please cite this work as:

> Ferrer-Paris, J. R. and Keith, D. A. (2022) Fire Ecology Traits for Plants: A database for fire research and management. Version 1.00. Centre for Ecosystem Science, University of New South Wales, Sydney, Australia.


This work has been supported by:

- [University of New South Wales](https://www.unsw.edu.au/)
- [NSW Bushfire Research Hub](https://www.bushfirehub.org/)
- [NESP Threatened Species Recovery Hub](https://www.nespthreatenedspecies.edu.au/)
- [NSW Department of Planning & Environment](https://www.planning.nsw.gov.au/)

## Components of the project
This project consists of several linked components:

This project consists of several linked components:

***:fire: Fire Ecology Traits for Plants: A database for fire research and management*** OSF project [osf.io/hu96w](https://osf.io/hu96w/) with following components:
  - :file_cabinet: **SQL structure of the fireveg database** [osf.io/4csyz](https://osf.io/4csyz)
    - :gear: Source code for defining the structure of the tables in a PostgreSQL database is available in this [GitHub repository](https://github.com/ces-unsw-edu-au/fireveg-db)
    - :label: A Database snapshot (SQL dump) is available as a Figshare dataset with DOI:[10.6084/m9.figshare.23361002](https://doi.org/10.6084/m9.figshare.23361002)
    - :label: Database exports (summary tables, CSV/XLSX formats) available as Figshare dataset with DOI:[10.6084/m9.figshare.24125088](https://doi.org/10.6084/m9.figshare.24125088)
  - :computer: **Webapp for browsing the fireveg database** [osf.io/rj68t](https://osf.io/rj68t)
    - :gear: Source code for setting up and running the Flask webapp id available in the [GitHub repository](https://github.com/ces-unsw-edu-au/fireveg-webapp)
    - :computer: Acess to the [Webapp](http://fireecologyplants.net) (Register with a verified email address)
  - :briefcase: **Code for managing the fireveg database**
    - :gear: Source code in [GitHub](https://github.com/ces-unsw-edu-au/fire-veg-aust/)
  - :bar_chart: **Data coverage of Fire Ecology Traits for Plants database**
    - :gear: Source code in [GitHub](https://github.com/ces-unsw-edu-au/fireveg-analysis/)
  - :technologist: **Fire Ecology Traits for Plants: Status of the database** [osf.io/kjevh](https://osf.io/kjevh)
    - :gear: Source code in [BitBucket repository](https://bitbucket.org/fireveg/fireveg-presentations)
    - :speech_balloon: [Presentation slides](https://rpubs.com/jrfep/firevegdb-ESA2023) 


### SQL structure of the database

Code for defining the structure of the tables in a PostgreSQL database is available in the [fireveg-db](https://github.com/jrfep/fireveg-db) repository.


### Database content

Data not available yet.

### WebApp

This repository contains the code for running a Python/Flask webapp.

#### Repository structure

- Folder [webapp/](/webapp/) contains all the code for the flask app.

### Code for managing the database

Code and instruction to perform several tasks in the database is available in the [fire-veg-aust](https://github.com/jrfep/fire-veg-aust) repository.
