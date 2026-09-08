# Copyright (c) 2026, RTE (http://www.rte-france.com), University of Kassel Department e2n 
# (https://www.uni-kassel.de/eecs/en/sections/sustainable-electrical-energy-systems/home.html),
# and Fraunhofer IEE (https://www.iee.fraunhofer.de/)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

import pandapower as pp
import pandapower.networks as pn
import pandas as pd
import pytest
from energnn.graph import HyperEdgeSetStructure
from pandapower.auxiliary import pandapowerNet

from pandapower_to_energnn import elements


@pytest.fixture(scope="module")
def net():
    net = pn.case14()
    pp.runpp(net)
    return net


def test_ports_and_features(net):
    converter = elements.LineConverter(["from_bus", "to_bus"], ["r_ohm", "x_ohm"])
    df_port, df_feature = converter(net=net)

    assert list(df_port.columns) == ["from_bus", "to_bus"]
    assert list(df_feature.columns) == ["r_ohm", "x_ohm"]
    assert len(df_port) == len(df_feature)
    assert len(df_port) == len(net.line)


def test_ports_only(net):
    converter = elements.BusConverter(["energnn_adress"], None)
    df_port, df_feature = converter(net=net)

    assert df_feature is None
    assert list(df_port.columns) == ["energnn_adress"]
    assert df_port["energnn_adress"].is_unique
    assert len(df_port) == len(net.bus)


def test_features_only(net):
    converter = elements.LoadConverter(None, ["p_mw", "q_mvar"])
    df_port, df_feature = converter(net=net)

    assert df_port is None
    assert list(df_feature.columns) == ["p_mw", "q_mvar"]
    assert len(df_feature) == len(net.load)


def test_no_ports_nor_features_raises():
    with pytest.raises(ValueError):
        elements.LineConverter(None, None)


def test_empty_table(net):
    # There is no static generator in the IEEE 14 test case: the converter must still return
    # well-formed (empty) tables.
    converter = elements.SgenConverter(["bus"], ["p_mw", "q_mvar"])
    df_port, df_feature = converter(net=net)

    assert len(df_port) == 0
    assert len(df_feature) == 0
    assert list(df_port.columns) == ["bus"]
    assert list(df_feature.columns) == ["p_mw", "q_mvar"]

def test_res_converter_reads_load_flow_results(net):
    # Result converters must read the res_* tables, not the input tables.
    converter = elements.ResBusConverter(None, ["vm_pu", "va_degree"])
    _, df_feature = converter(net=net)

    pd.testing.assert_series_equal(df_feature["vm_pu"], net.res_bus.vm_pu)
    pd.testing.assert_series_equal(df_feature["va_degree"], net.res_bus.va_degree)


def test_bus_addresses_match_pandapower_index(net):
    # Bus addresses must line up with the from_bus / to_bus indices used as ports elsewhere.
    df_port, _ = elements.BusConverter(["energnn_adress"], None)(net=net)
    assert set(df_port["energnn_adress"]) == set(net.bus.index)


def test_get_structure():
    converter = elements.GenConverter(["bus"], ["p_mw", "vm_pu"])
    structure = converter.get_structure()
    assert isinstance(structure, HyperEdgeSetStructure)


# (converter class, pandapower table it reads, port_list, feature_list)
CONVERTER_CASES = [
    (elements.BusConverter, "bus", ["energnn_adress"], None),
    (elements.ExtGridConverter, "ext_grid", ["bus"], ["vm_pu", "va_degree"]),
    (elements.LineConverter, "line", ["from_bus", "to_bus"], ["r_ohm", "x_ohm", "c_nf", "max_i_ka"]),
    (elements.LoadConverter, "load", ["bus"], ["p_mw", "q_mvar"]),
    (elements.GenConverter, "gen", ["bus"], ["p_mw", "vm_pu"]),
    (elements.SgenConverter, "sgen", ["bus"], ["p_mw", "q_mvar"]),
    (elements.ShuntConverter, "shunt", ["bus"], ["p_mw", "q_mvar", "max_step"]),
    (elements.TrafoConverter, "trafo", ["hv_bus", "lv_bus"], ["vk_percent", "vkr_percent", "tap_pos"]),
    (elements.ResBusConverter, "res_bus", ["energnn_adress"], ["vm_pu", "va_degree"]),
    (elements.ResLineConverter, "res_line", None, ["p_from_mw", "q_from_mvar", "i_from_ka"]),
    (elements.ResLoadConverter, "res_load", None, ["p_mw", "q_mvar"]),
    (elements.ResExtGridConverter, "res_ext_grid", None, ["p_mw", "q_mvar"]),
    (elements.ResGenConverter, "res_gen", None, ["p_mw", "q_mvar", "vm_pu"]),
    (elements.ResSgenConverter, "res_sgen", None, ["p_mw", "q_mvar"]),
    (elements.ResShuntConverter, "res_shunt", None, ["p_mw", "q_mvar"]),
    (elements.ResTrafoConverter, "res_trafo", None, ["p_hv_mw", "q_hv_mvar", "i_hv_ka"]),
]


@pytest.mark.parametrize(
    "converter_class, net_table, port_list, feature_list",
    CONVERTER_CASES,
    ids=[case[0].__name__ for case in CONVERTER_CASES],
)
def test_converter_smoke(net, converter_class, net_table, port_list, feature_list):
    # Every converter must expose the columns it advertises, with one row per element of the
    # pandapower table it reads.
    converter = converter_class(port_list, feature_list)
    df_port, df_feature = converter(net=net)

    n_elements = len(net[net_table])

    if port_list is None:
        assert df_port is None
    else:
        assert list(df_port.columns) == port_list
        assert len(df_port) == n_elements

    if feature_list is None:
        assert df_feature is None
    else:
        assert list(df_feature.columns) == feature_list
        assert len(df_feature) == n_elements


def test_network_elements_converter_base(net):
    # NetworkElementsConverter reads a single pandapower table named by _net_table.
    class LengthLineConverter(elements.NetworkElementsConverter):
        _net_table = "line"

    converter = LengthLineConverter(["from_bus", "to_bus"], ["length_km"])
    df_port, df_feature = converter(net=net)

    assert list(df_port.columns) == ["from_bus", "to_bus"]
    assert list(df_feature.columns) == ["length_km"]
    assert len(df_feature) == len(net.line)


def test_custom_elements_converter(net):
    class SquaredVoltageBusConverter(elements.ElementsConverter):
        def _get_table(self, *, net: pandapowerNet, **kwargs) -> pd.DataFrame:
            df = net.res_bus.copy()
            df["energnn_adress"] = df.index.astype(int)
            df["squared_vm_pu"] = df["vm_pu"] ** 2
            return df

    converter = SquaredVoltageBusConverter(["energnn_adress"], ["squared_vm_pu"])
    df_port, df_feature = converter(net=net)

    assert list(df_feature.columns) == ["squared_vm_pu"]
    assert len(df_port) == len(net.bus)
    pd.testing.assert_series_equal(
        df_feature["squared_vm_pu"], net.res_bus.vm_pu**2, check_names=False
    )
