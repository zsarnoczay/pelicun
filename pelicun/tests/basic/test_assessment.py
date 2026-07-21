#
# Copyright (c) 2018 Leland Stanford Junior University
# Copyright (c) 2018 The Regents of the University of California
#
# This file is part of pelicun.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# You should have received a copy of the BSD 3-Clause License along with
# pelicun. If not, see <http://www.opensource.org/licenses/>.
#
# Contributors:
# Adam Zsarnóczay
# John Vouvakis Manousakis

"""These are unit and integration tests on the assessment module of pelicun."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pelicun import assessment
from pelicun.base import ensure_value
from pelicun.pelicun_warnings import PelicunWarning


def create_assessment_obj(config: dict | None = None) -> assessment.Assessment:
    return assessment.Assessment(config) if config else assessment.Assessment({})


def test_Assessment_init() -> None:
    asmt = create_assessment_obj()
    # confirm attributes
    for attribute in (
        'asset',
        'calc_unit_scale_factor',
        'damage',
        'demand',
        'get_default_data',
        'get_default_metadata',
        'log',
        'loss',
        'options',
        'scale_factor',
        'stories',
        'unit_conversion_factors',
    ):
        assert hasattr(asmt, attribute)
    # confirm that creating an attribute on the fly is not allowed
    with pytest.raises(AttributeError):
        asmt.my_attribute = 2  # type: ignore


def test_assessment_get_default_metadata() -> None:
    asmt = create_assessment_obj()

    # The legacy names below trigger a PelicunWarning about deprecated
    # `PelicunDefault/` placeholder identifiers.
    deprecated_method_names = (
        'damage_DB_FEMA_P58_2nd',
        'damage_DB_Hazus_EQ_bldg',
        'damage_DB_Hazus_EQ_trnsp',
        'loss_repair_DB_FEMA_P58_2nd',
        'loss_repair_DB_Hazus_EQ_bldg',
        'loss_repair_DB_Hazus_EQ_trnsp',
    )
    current_method_names = (
        'Hazus Earthquake - Buildings',
        'Hazus Earthquake - Stories',
        'Hazus Earthquake - Transportation',
        'Hazus Hurricane Wind - Buildings',
    )

    with pytest.warns(PelicunWarning):
        for method_name in deprecated_method_names:
            # here we just test that we can load the data file, without
            # checking the contents.
            asmt.get_default_data(method_name, None)
            asmt.get_default_metadata(method_name, None)

    for method_name in current_method_names:
        for model_type in ['fragility', 'consequence_repair']:
            asmt.get_default_data(method_name, model_type)
            asmt.get_default_metadata(method_name, model_type)


def test_load_consequence_info_legacy_name() -> None:
    # <backwards compatibility>
    # Legacy consequence-database filenames trigger a deprecation
    # warning and resolve to the corresponding method's dataset.
    asmt = assessment.DLCalculationAssessment({})
    with pytest.warns(PelicunWarning, match='no longer referenced'):
        conseq_df, consequence_db = asmt.load_consequence_info(
            'loss_repair_DB_Hazus_EQ_bldg.csv'
        )

    assert len(consequence_db) == 1
    assert Path(consequence_db[0]).is_file()
    assert Path(consequence_db[0]).name == 'consequence_repair.csv'
    assert not conseq_df.empty

    # the loaded data matches what the modern method-name form provides
    asmt_modern = assessment.DLCalculationAssessment({})
    conseq_df_modern, consequence_db_modern = asmt_modern.load_consequence_info(
        'Hazus Earthquake - Buildings'
    )
    assert consequence_db == consequence_db_modern
    pd.testing.assert_frame_equal(conseq_df, conseq_df_modern)


def test_calculate_damage_collapse_fragility_custom_demand_type() -> None:
    # The collapse-fragility demand lookup in `calculate_damage`
    # resolves demand-type acronyms through the assessment-scoped
    # vocabulary, so it recognizes demand types registered through the
    # `CustomDemandTypes` option.
    sample_size = 3

    def prepare_assessment(
        config: dict | None,
    ) -> assessment.DLCalculationAssessment:
        asmt = assessment.DLCalculationAssessment(config)
        asmt.stories = 1

        # demand sample with the custom `STR` demand type
        demand_sample = pd.DataFrame(
            np.full((sample_size, 1), 0.06),
            columns=pd.MultiIndex.from_tuples(
                [('STR', '0', '1')], names=['type', 'loc', 'dir']
            ),
        )
        units_row = pd.DataFrame(
            'rad', index=['Units'], columns=demand_sample.columns, dtype=object
        )
        asmt.demand.load_sample(pd.concat([demand_sample, units_row]))

        # the global collapse component
        cmp_marginals = pd.DataFrame(
            {
                'Units': ['ea'],
                'Location': ['0'],
                'Direction': ['1'],
                'Theta_0': [1],
            },
            index=['collapse'],
        )
        asmt.asset.load_cmp_model({'marginals': cmp_marginals})
        asmt.asset.generate_cmp_sample(sample_size)
        return asmt

    collapse_fragility = {
        'DemandType': 'STR',
        'CapacityDistribution': None,
        'CapacityMedian': 0.04,
        'Theta_1': None,
    }

    asmt = prepare_assessment({'CustomDemandTypes': {'Story Torsion Ratio': 'STR'}})
    asmt.calculate_damage(
        length_unit='in',
        component_database='None',
        collapse_fragility=collapse_fragility,
    )

    # the custom acronym resolved to the registered demand name
    damage_params = ensure_value(asmt.damage.ds_model.damage_params)
    assert damage_params.loc['collapse', ('Demand', 'Type')] == (
        'Story Torsion Ratio'
    )

    # the 0.06 rad demand exceeds the deterministic 0.04 rad collapse
    # capacity in every realization
    ds_sample = ensure_value(asmt.damage.ds_model.sample)
    assert (ds_sample['collapse'] == 1).all().all()

    # without the custom entry, the acronym is not recognized
    asmt_default = prepare_assessment(None)
    with pytest.raises(
        ValueError, match='valid demand type acronym was not provided'
    ):
        asmt_default.calculate_damage(
            length_unit='in',
            component_database='None',
            collapse_fragility=collapse_fragility,
        )


def test_assessment_calc_unit_scale_factor() -> None:
    # default unit file
    asmt = create_assessment_obj()

    # without specifying a quantity
    assert asmt.calc_unit_scale_factor('m') == 1.00
    assert asmt.calc_unit_scale_factor('in') == 0.0254

    # with quantity
    assert asmt.calc_unit_scale_factor('2.00 m') == 2.00
    assert asmt.calc_unit_scale_factor('2 in') == 2.00 * 0.0254

    # when a custom unit file is specified, changing the base units
    asmt = create_assessment_obj(
        {
            'UnitsFile': (
                'pelicun/tests/basic/data/assessment/'
                'test_assessment_calc_unit_scale_factor/'
                'custom_units.json'
            )
        }
    )

    assert asmt.calc_unit_scale_factor('in') == 1.00
    assert asmt.calc_unit_scale_factor('m') == 39.3701

    # exceptions

    # unrecognized unit
    with pytest.raises(KeyError):
        asmt.calc_unit_scale_factor('smoot')
        # 1 smoot was 67 inches in 1958.


def test_assessment_scale_factor() -> None:
    # default unit file
    asmt = create_assessment_obj()
    assert asmt.scale_factor('m') == 1.00
    assert asmt.scale_factor('in') == 0.0254

    # when a custom unit file is specified, changing the base units
    asmt = create_assessment_obj(
        {
            'UnitsFile': (
                'pelicun/tests/basic/data/assessment/'
                'test_assessment_calc_unit_scale_factor/'
                'custom_units.json'
            )
        }
    )

    assert asmt.scale_factor('in') == 1.00
    assert asmt.scale_factor('m') == 39.3701

    # exceptions
    with pytest.raises(ValueError, match='Unknown unit: helen'):
        asmt.scale_factor('helen')
