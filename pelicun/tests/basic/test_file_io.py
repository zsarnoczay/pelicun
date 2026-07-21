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

"""These are unit and integration tests on the file_io module of pelicun."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import dlml
import numpy as np
import pandas as pd
import pytest

from pelicun import base, file_io
from pelicun.pelicun_warnings import PelicunWarning

# The tests maintain the order of definitions of the `file_io.py` file.


def test_save_to_csv() -> None:
    # Test saving with orientation 0
    data = pd.DataFrame({'A': [1e-3, 2e-3, 3e-3], 'B': [4e-3, 5e-3, 6e-3]})
    units = pd.Series(['meters', 'meters'], index=['A', 'B'])
    unit_conversion_factors = {'meters': 0.001}

    # Save to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'foo.csv'
        file_io.save_to_csv(
            data, filepath, units, unit_conversion_factors, orientation=0
        )
        assert Path(filepath).is_file()
        # Check that the file contains the expected data
        with Path(filepath).open(encoding='utf-8') as f:
            contents = f.read()
            assert contents == (
                ',A,B\n0,meters,meters\n0,1.0,4.0' '\n1,2.0,5.0\n2,3.0,6.0\n'
            )

    # Test saving with orientation 1
    data = pd.DataFrame({'A': [1e-3, 2e-3, 3e-3], 'B': [4e-3, 5e-3, 6e-3]})
    units = pd.Series(['meters', 'meters'], index=['A', 'B'])
    unit_conversion_factors = {'meters': 0.001}

    # Save to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'bar.csv'
        file_io.save_to_csv(
            data, filepath, units, unit_conversion_factors, orientation=1
        )
        assert Path(filepath).is_file()
        # Check that the file contains the expected data
        with Path(filepath).open(encoding='utf-8') as f:
            contents = f.read()
            assert contents == (
                ',0,A,B\n0,,0.001,0.004\n1,,0.002,' '0.005\n2,,0.003,0.006\n'
            )

    #
    # edge cases
    #

    data = pd.DataFrame({'A': [1e-3, 2e-3, 3e-3], 'B': [4e-3, 5e-3, 6e-3]})
    units = pd.Series(['meters', 'meters'], index=['A', 'B'])

    # units given, without unit conversion factors
    filepath = Path(tmpdir) / 'foo.csv'
    with pytest.raises(
        ValueError,
        match='When `units` is not None, `unit_conversion_factors` must be provided.',
    ), tempfile.TemporaryDirectory() as tmpdir:
        file_io.save_to_csv(
            data, filepath, units, unit_conversion_factors=None, orientation=0
        )

    unit_conversion_factors = {'meters': 0.001}

    # not csv extension
    filepath = Path(tmpdir) / 'foo.xyz'
    with pytest.raises(
        ValueError,
        match=('Please use the `.csv` file extension. Received file name is '),
    ), tempfile.TemporaryDirectory() as tmpdir:
        file_io.save_to_csv(
            data, filepath, units, unit_conversion_factors, orientation=0
        )

    # no data, log a complaint
    mylogger = base.Logger(
        log_file=None, verbose=True, log_show_ms=False, print_log=True
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'foo.csv'
        with pytest.warns(PelicunWarning) as record:
            file_io.save_to_csv(
                None,
                filepath,
                units,
                unit_conversion_factors,
                orientation=0,
                log=mylogger,
            )
    assert 'Data was empty, no file saved.' in str(record.list[0].message)


def test_substitute_default_path() -> None:
    expected_path = str(
        dlml.get_file(
            'seismic/building/component/FEMA P-58 2nd Edition', 'fragility.csv'
        )
    )

    # method alias resolution; non-default paths pass through unchanged
    input_paths = [
        'PelicunDefault/FEMA P-58/fragility.csv',
        '/data/file2.txt',
    ]
    result_paths = file_io.substitute_default_path(input_paths)
    assert result_paths[0] == expected_path
    assert result_paths[1] == '/data/file2.txt'

    # full DLML dataset IDs are also accepted as method names
    result_paths = file_io.substitute_default_path(
        [
            'PelicunDefault/seismic/building/component/'
            'FEMA P-58 2nd Edition/fragility.csv'
        ]
    )
    assert result_paths[0] == expected_path

    # only string paths are accepted; in-memory model data (e.g.,
    # DataFrames) needs to be handled by the caller
    with pytest.raises(TypeError, match='Data paths need to be strings'):
        file_io.substitute_default_path(
            [pd.DataFrame({'A': [1.0]})]  # type: ignore[list-item]
        )

    # files absent from a dataset's folder raise
    with pytest.raises(dlml.DatasetFileNotFoundError, match='pelicun_config.py'):
        file_io.substitute_default_path(
            ['PelicunDefault/FEMA P-58/pelicun_config.py']
        )

    # default paths need to include a filename
    with pytest.raises(KeyError, match='does not include a filename'):
        file_io.substitute_default_path(['PelicunDefault/FEMA P-58/'])

    # unknown method names raise a helpful error
    with pytest.raises(
        KeyError, match='is not a valid method alias or DLML dataset ID'
    ):
        file_io.substitute_default_path(['PelicunDefault/Unknown Method/x.csv'])


def test_substitute_default_path_legacy_names() -> None:
    # every legacy placeholder filename resolves without error, emits a
    # deprecation warning, and points to an existing file in the
    # installed DLML package
    for legacy_name in file_io.legacy_names:
        # a fresh logger for each case: a logger emits each distinct
        # warning message only once
        mylogger = base.Logger(
            log_file=None, verbose=True, log_show_ms=False, print_log=True
        )
        with pytest.warns(PelicunWarning, match='no longer referenced'):
            result_paths = file_io.substitute_default_path(
                [f'PelicunDefault/{legacy_name}.csv'], log=mylogger
            )
        result_path = result_paths[0]
        assert Path(result_path).is_file(), (
            f'Legacy name `{legacy_name}` resolved to `{result_path}`, '
            f'which does not point to an existing file.'
        )

    # unrecognized bare filenames raise
    with pytest.raises(KeyError, match='not recognized'):
        file_io.substitute_default_path(['PelicunDefault/some_file.csv'])


def test_resolve_default_dataset_path() -> None:
    # method aliases resolve to the dataset's folder
    dataset_path = file_io.resolve_default_dataset_path('FEMA P-58')
    assert dataset_path.is_dir()
    assert (dataset_path / 'fragility.csv').is_file()

    # dataset IDs resolve to the same folder as their alias
    assert (
        file_io.resolve_default_dataset_path(
            'seismic/building/component/FEMA P-58 2nd Edition'
        )
        == dataset_path
    )

    # optional files can be probed in the folder without errors
    assert not (dataset_path / 'pelicun_config.py').is_file()

    # unknown method names raise a helpful error
    with pytest.raises(
        KeyError, match='is not a valid method alias or DLML dataset ID'
    ):
        file_io.resolve_default_dataset_path('Unknown Method')


def test_dlml_resource_paths_are_valid_dataset_ids() -> None:
    resource_file_path = (
        Path(base.pelicun_path) / 'resources' / 'dlml_resource_paths.json'
    )
    with resource_file_path.open(encoding='utf-8') as f:
        resource_paths = json.load(f)

    valid_dataset_ids = set(dlml.list_datasets())
    for method_name, dataset_id in resource_paths.items():
        assert dataset_id in valid_dataset_ids, (
            f'The `{method_name}` entry in `dlml_resource_paths.json` '
            f'points to `{dataset_id}`, which is not a valid DLML '
            f'dataset ID.'
        )


def test_load_data() -> None:
    # test loading data with orientation 0

    filepath = 'pelicun/tests/basic/data/file_io/test_load_data/units.csv'
    unit_conversion_factors = {'inps2': 0.0254, 'rad': 1.00}

    data = file_io.load_data(filepath, unit_conversion_factors)
    assert np.array_equal(data.index.values, np.array(range(6)))  # type: ignore
    assert data.shape == (6, 19)  # type: ignore
    assert isinstance(data.columns, pd.core.indexes.multi.MultiIndex)  # type: ignore
    assert data.columns.nlevels == 4  # type: ignore

    _, units = file_io.load_data(
        filepath, unit_conversion_factors, return_units=True
    )

    for item in unit_conversion_factors:
        assert item in units.unique()  # type: ignore

    filepath = 'pelicun/tests/basic/data/file_io/test_load_data/no_units.csv'
    data_nounits = file_io.load_data(filepath, {})
    assert isinstance(data_nounits, pd.DataFrame)

    # test loading data with orientation 1
    filepath = 'pelicun/tests/basic/data/file_io/test_load_data/orient_1.csv'
    data = file_io.load_data(
        filepath, unit_conversion_factors, orientation=1, reindex=False
    )
    assert isinstance(data.index, pd.core.indexes.multi.MultiIndex)
    assert data.shape == (10, 2)
    assert data.index.nlevels == 4

    # with convert=None
    filepath = 'pelicun/tests/basic/data/file_io/test_load_data/orient_1_units.csv'
    unit_conversion_factors = {'g': 1.00, 'rad': 1.00}
    data = file_io.load_data(
        filepath, unit_conversion_factors, orientation=1, reindex=False
    )
    assert isinstance(data.index, pd.core.indexes.multi.MultiIndex)
    assert data.shape == (10, 3)
    assert data.index.nlevels == 4

    # try with reindexing
    data = file_io.load_data(
        filepath, unit_conversion_factors, orientation=1, reindex=True
    )
    assert np.array_equal(data.index.values, np.array(range(10)))  # type: ignore

    #
    # edge cases
    #

    # exception: not an existing file
    with pytest.raises(FileNotFoundError):
        file_io.load_from_file('/')
    # exception: not a .csv file
    with pytest.raises(
        ValueError,
        match='Unexpected file type received when trying to load from csv',
    ):
        file_io.load_from_file('pelicun/base.py')


if __name__ == '__main__':
    pass
