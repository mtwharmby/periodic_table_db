from ...shared import (
    ATOMIC_NR, PERIOD, GROUP, BLOCK, E_SHELL_STRUCT, E_SUB_SHELL_STRUCT
)

AZIMUTHAL_QUANTUM_NUMBER = {
    0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h", 6: "i", 7: "j"
    # j is assumed to be the next value... it will never appear as the empty
    # shells get cleaned up
}

NON_NUMERIC_GROUP_NAMES = {
    -1: "Lanthanoids", -2: "Actinoids"
}


# TODO Needs testing
# TODO Write tests for all!


class SubShell:

    MAX_E_ORBITAL = 2

    def __init__(self, pqn: int, aqn: int) -> None:
        """
        A representation of the orbitals making up a sub-shell in an atom.

        The number of sub-shells to create is determined from the azimuthal
        quantum number (l) provided (the magnetic quantum number, m_l of the
        orbitals in the sub-shell varies from -l to l).

        The name of the sub-shell is determined from the principal quantum
        number with the letter code derived from the azimuthal quantum number.

        The number of electrons that can be allocated to each orbital is
        limited by the MAX_E_ORBITAL variable.
        """
        self.orbitals = [0] * len(range(-aqn, aqn + 1))
        self.name = f"{pqn}{AZIMUTHAL_QUANTUM_NUMBER[aqn]}"
        self._pqn = pqn
        self._aqn = aqn

    def populate(
            self, population: dict[str, int | list[tuple[int, int]]]
            ) -> dict[str, int | list[tuple[int, int]]]:
        """
        Fill orbitals with electrons.

        Electrons are provided from a dictionary containing the keyword
        "electrons". Electrons are distributed equally across all orbitals,
        first with one electron per orbital, then with a second.
        Each orbital can only hold two electrons.

        Remaining electrons are returned in the dictionary. The principal and
        azimuthal quantum numbers of the sub-shell are added to the "sequence"
        entry if electrons were added to allow the sub-shell filling sequence
        to be determined.
        """

        while (population["electrons"] and not self.is_full):
            #    and self.electrons < len(self.orbitals) * self.MAX_E_ORBITAL):
            for i in range(len(self.orbitals)):
                if (population["electrons"]
                        and self.orbitals[i] < self.MAX_E_ORBITAL):
                    self.orbitals[i] += 1
                    population["electrons"] -= 1

        if bool(sum(self.orbitals)):
            # Only add to the sequence if some electrons added to the sub-shell
            population["sequence"].append((self._pqn, self._aqn))

        return population

    @property
    def electrons(self):
        """
        Total number of electrons (over all orbitals) in this sub-shell.
        """
        return sum(self.orbitals)

    @property
    def is_full(self):
        """
        True if all the orbitals in this sub-shell are filled.
        """
        return self.electrons == len(self.orbitals) * self.MAX_E_ORBITAL

    def __repr__(self) -> str:
        e_config = ", ".join(map(str, self.orbitals))
        return f"<SubShell: {self.name} ({e_config})>"

    def __str__(self) -> str:
        return f"{self.name}^{{{self.electrons}}}"


class Atom:

    def __init__(self, atomic_nr, charge=0) -> None:
        """
        Create a representation of the electronic structure of an atom, using
        its atomic number. If the entity is charged (i.e. it is an ion),
        electronic structure can also be calculated, but block, group and
        period etc., are not.
        """
        self.atomic_nr = atomic_nr
        population = {"electrons": atomic_nr + charge, "sequence": []}
        self.shells: dict[int, dict[int, SubShell]] = {}
        self.is_ion = bool(charge)

        pqn = 1
        while population["electrons"]:
            self.shells[pqn] = {}

            for aqn in range(0, pqn):
                self.shells[pqn][aqn] = SubShell(pqn, aqn)

                if aqn == 0:
                    self.shells[pqn][aqn].populate(population)
                    if pqn > 5:
                        # Populate f-orbitals
                        self.shells[pqn - 2][3].populate(population)
                    if pqn > 3:
                        # Populate d-orbitals
                        self.shells[pqn - 1][2].populate(population)
                elif aqn > 1:
                    # Don't populate f- or d-orbitals in this shell yet
                    continue
                else:
                    self.shells[pqn][aqn].populate(population)

            # Shell complete, next shell
            pqn += 1

        # Clean up empty sub-shells
        for pqn in self.shells:
            self.shells[pqn] = {
                aqn: sub_shell
                for aqn, sub_shell in self.shells[pqn].items()
                if sub_shell.electrons
            }

        # List of tuples containing the principal quantum and azimuthal
        # quantum numbers of each occupied sub-shell in the sequence they
        # were filled.
        self._sub_shell_sequence_qns: list[tuple[int, int]] = (
            population["sequence"]
        )

        # Dictionary of principal quantum numbers of each occupied shell with
        # the total number of electrons in that shell.
        self._shell_electrons = {
            pqn: sum([
                sub_shell.electrons
                for _, sub_shell in self.shells[pqn].items()
            ])
            for pqn in self.shells
        }

        self._last_pqn, self._last_aqn = self._sub_shell_sequence_qns[-1]
        if self.is_ion:
            self.block = None
            self.group = None
            self.period = None
        else:
            self.block = AZIMUTHAL_QUANTUM_NUMBER[self._last_aqn]
            self.period, self.group = self._calculate_period_group()

    def _calculate_period_group(self):
        # Find the index in the sequence of the beginning of the last period
        aqn_seq = [qns[1] for qns in self._sub_shell_sequence_qns]
        # Find last occurrence of 0: https://stackoverflow.com/a/6890255
        period_begin_idx = next(
            i for i in reversed(range(len(aqn_seq))) if aqn_seq[i] == 0
        )
        period = self._sub_shell_sequence_qns[period_begin_idx][0]

        # Add up number of electrons added in period
        period_electrons = 0
        for pqn, aqn in self._sub_shell_sequence_qns[period_begin_idx:]:
            period_electrons += self.shells[pqn][aqn].electrons

        # Handle all the edge cases for group assignment
        if self._last_aqn == 0:  # s-block
            if period == 1:
                if self.shells[self._last_pqn][self._last_aqn].is_full:
                    # Edge case: Helium
                    return period_electrons + 16

        elif period in [2, 3]:
            if self._last_aqn != 0:
                # Edge case: period 2 & 3 p-block
                return period_electrons + 10
        elif period in [6, 7]:
            if self._last_aqn in [1, 2]:
                # Edge case: p- or d-block, with f-block
                return period_electrons - 14
            elif self._last_aqn == 3:
                if period == 6:
                    # Edge case: lanthanoids
                    return period, -1
                elif period == 7:
                    # Edge case: actinoids
                    return period, -2
            elif self._last_aqn > 3:
                raise RuntimeError("Group calculation not implemented: "
                                   f"aqn = {self._last_aqn}")
        elif period > 7:
            raise RuntimeError("Group calculation not implemented: "
                               f"period = {period}")

        return period, period_electrons

    @property
    def shell_structure(self):
        """
        A string reporting the total number of electrons in each shell,
        separated by dots.
        """
        cfg = [
            f"{self._shell_electrons[pqn]}"
            for pqn in self._shell_electrons
        ]
        return ".".join(cfg)

    @property
    def sub_shell_structure(self) -> str:
        """
        A string containing the sub-shell name with the associated number of
        electrons (as a superscript, in LaTeX format) for all occupied
        sub-shells. Sub-shells listed in filling order.
        """
        # List of all occupied sub-shells in the order they were filled
        sub_shells_seq = [
            self.shells[pqn][aqn]
            for pqn, aqn in self._sub_shell_sequence_qns
        ]
        cfg = [
            str(sub_shell)
            for sub_shell in sub_shells_seq
        ]
        return " ".join(cfg)

    @property
    def electrons(self) -> int:
        """
        Returns the total number of electrons in this Atom.
        """
        electrons_per_shell = [
            v for v in self._shell_electrons.values()
        ]
        return sum(electrons_per_shell)

    @property
    def charge(self) -> int:
        """
        Returns the charge of the Atom (ion).
        """
        return self.atomic_nr - self.electrons

    def dict(self) -> dict[str, int | float | str]:
        atom_dict = {
            ATOMIC_NR: self.atomic_nr,
            PERIOD: self.period,
            GROUP: self.group,
            BLOCK: self.block,
            E_SHELL_STRUCT: self.shell_structure,
            E_SUB_SHELL_STRUCT: self.sub_shell_structure,
        }

        return atom_dict
