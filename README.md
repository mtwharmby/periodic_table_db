# Periodic Table Database
Python module for generating a (SQLite) database containing the elements of the periodic table, their relative atomic masses and other properties.

## Creating the Database
A periodic table database, stored in an SQLite database file, can be created using a command-line instruction after installing the python module:
```sh
% pip install periodic_table_sqlite
...
% create-pt-db --db-path <path to an existing directory>
```
Details of the arguments that can be supplied to `create-pt-db` can be found by running:
```sh
% create-pt-db --help
```
Running the create-pt-db script without the `--db-path` argument will briefly create an in-memory database (useful for debugging...!). 

### Use as a Library
The functions in the module are (hopefully) also written in a way that they can be used with [SQLAlchemy](https://www.sqlalchemy.org/) to create the tables for a periodic table database in another database. See the module `generate_database.py` for an example of how this might be done.

## Data
### Atomic Weights
Data are obtained from the IUPAC Comission on Isotopic Abundances and Atomic Weights (CIAAW website). A description of the uncertainties is provided by [Possolo *et al.*, Pure Appl. Chem., 90 (2018), 395-424](https://www.degruyter.com/document/doi/10.1515/pac-2016-0402/html).

The terms "atomic weight" and "relative atomic mass" are considered as interchangeable, with "atomic weight" being used as a shorthand (in the reference publications as well as in the database).

Atomic weights are published in three different formats:
1. Single value with an uncertainty. Elements may show a variation in their isotopic composition in "normal" materials, but this variation is less than the reported uncertainty. The major source of this uncertainty is not the variation, but another factor (e.g. measurement precision).
2. An interval, with a maximum and minimum value. Elements are expected to show a variability in their composition in "normal" materials, and it is this variability which is the major source of the uncertainty. This format was first introduced in 2009.
3. No atomic weight for elements which have no stable isotope, only radioactive isotopes.
  - **Note**: The elements bismuth (Bi), thorium (Th), protactinium (Pa) and uranium (U) also have no stable isotopes, but all have standard atomic weights in the table (single value with an uncertainty) since they have characteristic terrestrial isotopes.

"Normal" materials are defined as:
> a reasonably possible source for this element or its compounds in commerce, for industry or science; the material is not itself studied for
some extraordinary anomaly and its isotopic composition has not been modified significantly in a geologically brief period

[Possolo *et al.*, Pure Appl. Chem., 90 (2018), 395-424](https://www.degruyter.com/document/doi/10.1515/pac-2016-0402/html), and ref 2 therein.

For elements with atomic weight expressed as an interval, the average weight of atoms in a  sample of the element will be influenced by the population of isotopes (see [Possolo *et al.*, Pure Appl. Chem., 90 (2018), 395-424](https://www.degruyter.com/document/doi/10.1515/pac-2016-0402/html)). Furthermore, isotopic compositions may be influenced by other factors (e.g. geological and biological processes); elements subject to these effects are indicated in the table on the [CIAAW website](https://ciaaw.org/atomic-weights.htm), but not marked in the database.

To standardise the data representation in the database:
* for elements with a single valued atomic weight, the minimum and maximum values of the interval defined by the uncertainty have been calculated and are reported as `weight_min` and `weight_max`, respectively, in the database.
* for elements where atomic weight is reported as an interval, the atomic weight has been calculated as the mid-point of the interval, and the uncertainty is calculated as half the difference between the extrema of the interval. The weight and uncertainty are reported as `weight` and `weight_esd`, respectively, in the database.

The `method` field of the `atomic_weight_types` database defines how the atomic weight provided in the database has been obtained.

## Sources
* Periodic table of elements & atomic weights: https://ciaaw.org/atomic-weights.htm
  - Atomic weights are summarised from [Prohaska *et al.*, Pure Appl. Chem., 94 (2022), 573-600](https://www.degruyter.com/document/doi/10.1515/pac-2019-0603/html)
  - For further discussion on the expression of the atomic weights and their uncertainties, see [Possolo *et al.*, Pure Appl. Chem., 90 (2018), 395-424](https://www.degruyter.com/document/doi/10.1515/pac-2016-0402/html), specifically section 1.1.
