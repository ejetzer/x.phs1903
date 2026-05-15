# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
from pandas import DataFrame, Series, concat
import typing
from queue import Queue
from numbers import Real

from .exceptions import AucunDatumError


class Data(DataFrame):
    @property
    def _constructor(self):
        return Data

    @property
    def _constructor_sliced(self):
        return Datum


class Datum(Series):
    @property
    def _constructor(self):
        return Datum

    @property
    def _constructor_expanddim(self):
        return Data


class FileData(Queue):
    def __init__(self, df: Data | None = None):
        self.df = df if df is not None else Data()
        super().__init__()

    @typing.override
    def put(self, *datum: Series, **datum_dict: Real):
        if len(datum) == 1:
            datum: Datum = Datum(datum)
        elif len(datum_dict.values) > 0:
            datum: Datum = Datum(datum_dict)
        else:
            raise AucunDatumError(datum, datum_dict)

        super().put(datum)

    def get(self, timeout: int | None = None):
        datum_col: Datum = super().get(timeout)
        datum_ligne: Data = datum_col.to_frame().T
        self.df = concat([self.df, datum_ligne])
        return Data(self.df)
