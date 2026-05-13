# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
from pandas import DataFrame, Series


class Data(DataFrame):
    _metadata = ['auteur', 'date', 'description', 'reference', 'model']

    @property
    def _constructor(self):
        return Data

    @property
    def _constructor_sliced(self):
        return Datum

    @property
    def résiduel(self):
        pass


class Datum(Series):
    _metadata = ['auteur', 'date', 'description', 'reference', 'model']

    @property
    def _constructor(self):
        return Datum

    @property
    def _constructor_expanddim(self):
        return Data
