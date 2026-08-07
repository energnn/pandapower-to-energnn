# Copyright (c) 2026, RTE (http://www.rte-france.com)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

import pandas as pd
from energnn.converter import ElementsConverter
from pandapower.auxiliary import pandapowerNet


class NetworkElementsConverter(ElementsConverter):
    """Base class for elements converters that read a single pandapower network table.

    Subclasses only need to set ``_network_table`` to the name of the ``pandapower.auxiliary.pandapowerNet``
    method that returns their table (e.g. ``"net.line"``).

    The ``"id"`` column is the index of pandapower tables, not an attribute: it is stripped from the
    ``attributes`` requested from pandapower.

    :cvar _network_getter: Name of the ``pandapower.auxiliary.pandapowerNet`` method returning the table.
    """

    _net_table: str

    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        columns = [a for a in self.attributes if a != "id"] # relic from pypowsybl-to-energnn, can probably be deleted
        return net[self._net_table][columns]


class BusConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        bus_df = net.bus.copy()
        bus_df['energnn_adress'] = bus_df.index.astype(int)
        return bus_df

class ExtGridConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.ext_grid

class LineConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        line_df = net.line.copy()
        line_df['r_ohm'] = line_df.r_ohm_per_km * line_df.length_km
        line_df['x_ohm'] = line_df.x_ohm_per_km * line_df.length_km
        line_df['c_nf'] = line_df.c_nf_per_km * line_df.length_km
        return line_df

class LoadConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.load

class GenConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.gen

class SgenConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.sgen

class ShuntConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.shunt

class TrafoConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.trafo

class ResBusConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        res_bus_df = net.res_bus.copy()
        res_bus_df['energnn_adress'] = res_bus_df.index.astype(int)
        return res_bus_df

class ResLineConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_line

class ResLoadConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_load

class ResExtGridConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_ext_grid

class ResGenConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_gen

class ResSgenConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_sgen

class ResShuntConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_shunt

class ResTrafoConverter(ElementsConverter):
    def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
        return net.res_trafo
