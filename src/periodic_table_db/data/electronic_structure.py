AZIMUTHAL_QUANTUM_NUMBER = {
    0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h", 6: "i", 7: "j"
    # j is assumed to be the next value... it will never appear as the empty
    # shells get cleaned up
}

NON_NUMERIC_GROUP_NAMES = {
    -1: "Lanthanoids", -2: "Actinoids"
}


class SubShell:

    MAX_E_ORBITAL = 2

    def __init__(self, pqn: int, aqn: int) -> None:
        self.orbitals = [0] * len(range(-aqn, aqn + 1))
        self.name = f"{pqn}{AZIMUTHAL_QUANTUM_NUMBER[aqn]}"
        self._pqn = pqn
        self._aqn = aqn

    def populate(self, population):

        while (population["electrons"] and not self.is_full):
            #    and self.electrons < len(self.orbitals) * self.MAX_E_ORBITAL):
            for i in range(len(self.orbitals)):
                if (population["electrons"]
                        and self.orbitals[i] < self.MAX_E_ORBITAL):
                    self.orbitals[i] += 1
                    population["electrons"] -= 1

            # # Set this sub-shell's AQN as the last AQN to populate the atom
            # population["aqn"] = self._aqn

        if bool(sum(self.orbitals)):
            # Only add to the sequence if some electrons added to the sub-shell
            population["sequence"].append((self._pqn, self._aqn))

        return population

    @property
    def electrons(self):
        return sum(self.orbitals)

    @property
    def is_full(self):
        return self.electrons == len(self.orbitals) * self.MAX_E_ORBITAL

    def __repr__(self) -> str:
        e_config = ", ".join(map(str, self.orbitals))
        return f"<SubShell: {self.name} ({e_config})>"


class Atom:

    def __init__(self, atomic_nr, charge=0) -> None:
        """
        Create a representation of the electronic structure of an atom, using
        its atomic number. If the entity is charged (i.e. it is an ion),
        electronic structure can also be calculated, but block, group and
        period are not.
        """
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

        self._sub_shell_sequence: list[tuple[int, int]] = (
            population["sequence"]
        )

        self._shell_config = {
            pqn: sum([
                sub_shell.electrons
                for _, sub_shell in self.shells[pqn].items()
            ])
            for pqn in self.shells
        }

        self._last_pqn, self._last_aqn = self._sub_shell_sequence[-1]
        if self.is_ion:
            self.block = None
            self.group = None
            self.period = None
        else:
            self.block = AZIMUTHAL_QUANTUM_NUMBER[self._last_aqn]
            self.group = self._calculate_group()
            self.period = self._last_pqn

    def _calculate_group(self):
        # Find the index in the sequence of the beginning of the last period
        period_begin_idx = self._sub_shell_sequence.index((self._last_pqn, 0))

        # Add up number of electrons added in period
        period_electrons = 0
        for pqn, aqn in self._sub_shell_sequence[period_begin_idx:]:
            period_electrons += self.shells[pqn][aqn].electrons

        # Handle all the edge cases for group assignment
        if self._last_aqn == 0:  # s-block
            if self._last_pqn == 1:
                if self.shells[self._last_pqn][self._last_aqn].is_full:
                    # Edge case: Helium
                    return period_electrons + 16

        elif self._last_pqn in [2, 3]:
            if self._last_aqn != 0:
                # Edge case: period 2 & 3 p-block
                return period_electrons + 10
        elif self._last_pqn in [6, 7]:
            if self._last_aqn in [1, 2]:
                # Edge case: p- or d-block, with f-block
                return period_electrons - 14
            elif self._last_aqn == 3:
                if self._last_pqn == 6:
                    # Edge case: lanthanoids
                    return -1
                elif self._last_pqn == 7:
                    # Edge case: actinoids
                    return -2
            elif self._last_aqn > 3:
                raise RuntimeError("Group calculation not implemented: "
                                   f"aqn = {self._last_aqn}")
        elif self._last_pqn > 7:
            raise RuntimeError("Group calculation not implemented: "
                               f"period = {self._last_pqn}")

            # TODO Needs testing
            # TODO Write tests for all!

        return period_electrons

    @property
    def shell_structure(self):
        cfg = [
            f"{self._shell_config[pqn]}"
            for pqn in self._shell_config
        ]
        return ".".join(cfg)

    @property
    def _sub_shell_config(self) -> dict[str, int]:
        """
        A dictionary of all sub-shell names its number of electrons.
        """
        return {
                sub_shell.name: sub_shell.electrons
                for pqn in self.shells
                for _, sub_shell in self.shells[pqn].items()
            }

    @property
    def sub_shell_structure(self) -> str:
        """
        A string of each sub-shell name with its number of electrons as a
        superscript. Uses LaTeX formatting.
        """
        cfg = [
            f"{name}{{^{electrons}}}"
            for name, electrons in self._sub_shell_config.items()
        ]

        return " ".join(cfg)


# if __name__ == "__main__":
#     # el_h = Atom(1)
#     # el_he = Atom(2)
#     # 0


#     # el_zr = Atom(40)  # Should be in group 4
#     # el_in = Atom(49)  # Should be group 13
#     # og = Atom(118)
#     eu = Atom(65)
#     tc = Atom(43)
#     he = Atom(2)
#     0
