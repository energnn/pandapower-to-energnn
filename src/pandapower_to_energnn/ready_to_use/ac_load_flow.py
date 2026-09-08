# Copyright (c) 2026, RTE (http://www.rte-france.com), University of Kassel Department e2n 
# (https://www.uni-kassel.de/eecs/en/sections/sustainable-electrical-energy-systems/home.html),
# and Fraunhofer IEE (https://www.iee.fraunhofer.de/)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

from energnn.converter import Converter

from pandapower_to_energnn.elements import (
    BusConverter,
    LineConverter,
    LoadConverter,
    ExtGridConverter,
    GenConverter,
    SgenConverter,
    ShuntConverter,
    TrafoConverter,
    ResBusConverter,
    ResLineConverter,
    ResLoadConverter,
    ResExtGridConverter,
    ResGenConverter,
    ResSgenConverter,
    ResShuntConverter,
    ResTrafoConverter,
)


class ACLoadFlowInputConverter(Converter):

    elements_converter_dict = {
        "buses": BusConverter(["energnn_adress"], None),
        "lines": LineConverter(["from_bus", "to_bus"], ["r_ohm", "x_ohm", "c_nf", "max_i_ka"]),
        "loads": LoadConverter(["bus"], ["p_mw", "q_mvar", "in_service"]),
        "ext_grids": ExtGridConverter(["bus"], ["vm_pu", "va_degree", "in_service"]),
        "gens": GenConverter(["bus"], ["vm_pu", "p_mw", "in_service"]),
        "sgens": SgenConverter(["bus"], ["p_mw", "q_mvar", "in_service"]),
        "shunts": ShuntConverter(["bus"], ["p_mw", "q_mvar", "in_service", "step"]),
        "trafos": TrafoConverter(["hv_bus", "lv_bus"], ["vk_percent", "vkr_percent", "tap_pos"]),
    }


class ACLoadFlowOutputConverter(Converter):

    elements_converter_dict = {
        "buses": ResBusConverter(None, ["vm_pu"]),  # Phase angle is not permutation equivariant
        "lines": ResLineConverter(None, ["p_from_mw", "q_from_mvar", "i_from_ka", "p_to_mw", "q_to_mvar", "i_to_ka"]),
        "loads": ResLoadConverter(None, ["p_mw", "q_mvar"]),
        "ext_grids": ResExtGridConverter(None, ["p_mw", "q_mvar"]),
        "gens": ResGenConverter(None, ["q_mvar", "va_degree"]),
        "sgens": ResSgenConverter(None, ["p_mw", "q_mvar"]),
        "shunts": ResShuntConverter(None, ["p_mw", "q_mvar"]),
        "trafos": ResTrafoConverter(None, ["p_hv_mw", "q_hv_mvar", "i_hv_ka", "p_lv_mw", "q_lv_mvar", "i_lv_ka"]),
    }
