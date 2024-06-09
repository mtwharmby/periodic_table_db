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

#### References
* Periodic table of elements & atomic weights: https://ciaaw.org/atomic-weights.htm
  - Atomic weights are summarised from [Prohaska *et al.*, Pure Appl. Chem., 94 (2022), 573-600](https://www.degruyter.com/document/doi/10.1515/pac-2019-0603/html)
  - For further discussion on the expression of the atomic weights and their uncertainties, see [Possolo *et al.*, Pure Appl. Chem., 90 (2018), 395-424](https://www.degruyter.com/document/doi/10.1515/pac-2016-0402/html), specifically section 1.1.

### Electronic Structure, Groups, Periods
#### Background
Elements are arranged in the periodic table corresponding to their chemical similarity. The chemistry of an element is determined by the number and arrangement of electrons, specifically the outermost electrons.

Electrons are arranged around an atom in *orbitals* (wavefunctions), which are solutions of the *Schr&ouml;dinger Equation*. There are four types of orbital, *s*, *p*, *d* and *f* (described by the *azimuthal quantum number*, $l$), each with their own shapes, and each able to support up to two electrons. As more electrons need to be accommodated around an atom, the orbitals get further away (expressed by the *principal quantum number*, $n$). Through a combination of the shape and distances from the nucleus, there is a  quantisation of the electron energies.

An orbital is specified by its quantum numbers, $n$ and $l$, which adopt the following values:
- $n$: $1 \le n \le \infty$
- $l$: $0, 1, ... (n - 1)$, where the values of $l$ correspond to the orbital shapes:

| $l$ | Orbital | 
|---|---|
| 0 | s |
| 1 | p |
| 2 | d |
| 3 | f |

As larger values of $n$ correspond to a further distance from the nucleus, the electrons in these shells experience a smaller effective nuclear charge, $Z_{eff}$, so it is less energetically favourable to fill these orbitals. Furthermore, the different orbital shapes have differing radial distributions, and their electrons experience different $Z_{eff}$s. This leads to the following (approximately correct - see [Exceptions](#exceptions)) order of filling of orbitals in neutral atoms:
> 1s < 2s < 2p < 3s < 3p < 4s < 3d < 4p < 5s < 4d < 5p < 6s < 5d ~ 4f < 6p < 7s < 6d ~ 5f < 7p

Three principles govern the sequence of orbital filling:
1. The *Aufbau Principle*: The lowest energy orbitals are filled first.
2. *Hund's First Rule*:  In a set of degenerate orbitals, electrons may not be (spin-)paired until each orbital in the set contains one electron.
3. The *Pauli Exclusion Principle*: No two electrons around an atom may have the same set of quantum numbers, $n$, $l$, $m_l$ and $m_s$.

#### Derived Properties
The orbital filling sequence combined with the three principles by which the orbitals are filled, are used in the module `electronic_structure.py` to build a model for the ground state configuration of electrons in an atom, assuming a neutral atom (see ).

From this configuration, the following properties are derived:
- Period
- Group
- Block: the type of the last orbital to be filled.
- Electronic Structure:
  - Shell structure: a dot separated listing of total number of electrons in a shell.
  - Subshell structure: a dot separated listing of the number of electrons within each orbital type, arranged by principal quantum number.

Groups are entered as a number (1-18) with additional European (`label_eu`) and American (`label_us`) labelling schemes. This is based on the discussion on the [Webelements Group Number page](https://www.webelements.com/periodicity/group_number/). Certain groups have also been assigned names (see [The Red Book, 2005](https://iupac.org/wp-content/uploads/2016/07/Red_Book_2005.pdf), section IR-3.5):
| Group | Name | Note |
|---|---|---|
| 1 | Alkali Metals | |
| 2 | Alkaline Earth Metals | |
| 11 | Coinage Metals | Not IUPAC approved |
| 15 | Pnictogens | |
| 16 | Chalcogens | |
| 17 | Halogens | |
| 18 | Noble Gases | |

Based on the assigned group (and period), the following labels are also assigned to specific atoms (see [The Red Book, 2005](https://iupac.org/wp-content/uploads/2016/07/Red_Book_2005.pdf), section IR-3.5):
- Main Group: all elements in groups 1, 2 and 13-18 (excluding hydrogen). These, along with the light transition metals, are the most abundant in on Earth.
- Transition Metal: all elements in groups 3-11, i.e. those whose atoms or cations have partially filled d-subshells.
- Rate Earth Metal: scandium, yttrium and the lanthanoids.

#### Exceptions
The orbital filling sequence given in the [Background](#background) is an approximation. The real groundstate of the following elements is manually altered:
* copper (29), niobium (41), molybdenum (42), ruthenium (44), rhodium (45), palladium (46), silver (47), lanthanum (57), cerium (58), gadolinium (64), platinum (78), actinium (89), thorium (90), protactinium (91), uranium (92) and neptunium (93) - according to Housecroft and Sharp (2001), Table 1.3.
* lawrencium (104) - has unusual groundstate for a d-block element: $7s^2 7p^1$. This has been confirmed as the groundstate by Zou & Fischer ([Phys. Rev. Lett., 88 (2002), 183001](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.88.183001))
* darmstadtium (110) and roentgenium (111) - according to Webelements.

Although the electronic configurations are modified, all block & group memberships are correctly calculated.

**Note 1:** Lanthanum and actinium are considered f-block elements, even though they do not possess any f-electrons in their groundstates. This is consistent with Webelements.

**Note 2:** Lutetium and lawrencium are both considered d-block elements. This is consistent with Webelements.

#### References
* *Inorganic Chemistry*, C. E. Housecroft & A. G. Sharp, Prentice Hall (2001) - specifically, sections 1.5 to 1.9.
* *Nomenclature of Inorganic Chemistry IUPAC Recommendations 2005*, Eds. N.G. Connelly, T. Damhus, R.M. Hartshorn, and A.T. Hutton, IUPAC/RSC Publishing (2005): [The Red Book, 2005](https://iupac.org/wp-content/uploads/2016/07/Red_Book_2005.pdf)
* [Webelements Group Number page](https://www.webelements.com/periodicity/group_number/)
* [Zou & Fischer, Phys. Rev. Lett., 88 (2002), 183001](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.88.183001)