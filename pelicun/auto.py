#
# Copyright (c) 2023 Leland Stanford Junior University
# Copyright (c) 2023 The Regents of the University of California
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


"""Classes and methods that auto-populate DL models."""

from __future__ import annotations

import copy
import importlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pelicun import file_io

if TYPE_CHECKING:
    import pandas as pd


def auto_populate(
    config: dict,
    auto_script_path: Path,
    unique_id: int = 1,
    **kwargs,  # noqa: ANN003, ARG001
) -> tuple[dict, pd.DataFrame]:
    """
    Auto populate the DL configuration with predefined rules.

    Automatically populates the Damage and Loss (DL) configuration for
    a Pelicun calculation using predefined rules.  This function
    modifies the provided configuration dictionary based on an
    external Python script that defines auto-population rules. It
    supports using built-in scripts or custom scripts specified by the
    user.

    Parameters
    ----------
    config: dict
        A configuration dictionary with a 'GeneralInformation' key
        that holds another dictionary with attributes of the asset of
        interest. This dictionary is modified in-place with
        auto-populated values.
    auto_script_path: str
        The path pointing to a Python script with the auto-population
        rules. Built-in scripts can be referenced using the
        'PelicunDefault/method_name/pelicun_config.py' format where
        'method_name' identifies the methodology through one of the
        method aliases in the
        `{base.pelicun_path}/resources/dlml_resource_paths.json` file
        or directly through a DLML dataset ID (e.g.,
        'seismic/building/portfolio/Hazus v6.1'). Such references are
        resolved to the corresponding script in the installed Damage
        and Loss Model Library (the `dlml` package).
    unique_id: int
        This id is required when multiple auto population scripts are
        run in sequence. It helps keep the imported module names unique.
    kwargs
        Keyword arguments.

    Returns
    -------
    tuple
        A tuple containing two items:
        1. Updated configuration dictionary including new 'DL' key
        with damage and loss information.
        2. A dictionary of component quantities (CMP) derived from the
        auto-population process.

    Raises
    ------
    ValueError
        If the configuration dictionary does not contain necessary
        asset information under 'GeneralInformation'.

    """
    # create a copy of config to avoid editing the original
    config_autopopulated = copy.deepcopy(config)

    # try to get the AIM attributes
    aim = config_autopopulated.get('GeneralInformation')
    if aim is None:
        msg = 'No Asset Information provided for the auto-population routine.'
        raise ValueError(msg)

    # Resolve a 'PelicunDefault/' placeholder in the script path
    # through the installed Damage and Loss Model Library. Paths
    # without the placeholder pass through unchanged.
    auto_script_path = Path(
        file_io.substitute_default_path([str(auto_script_path)])[0]
    )

    # load the auto population module
    asp = auto_script_path.resolve()
    module_name = f'auto_script_{unique_id}'
    module = sys.modules.get(module_name)
    if module is None or getattr(module, '__file__', None) != str(asp):
        # Let the script import helper modules from its own folder.
        script_dir = str(asp.parent)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        spec = importlib.util.spec_from_file_location(module_name, asp)
        module = importlib.util.module_from_spec(spec)
        # Register the module so that a subsequent request for the same
        # script with the same unique id reuses it instead of executing
        # the script again.
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[module_name]
            raise
    auto_populate_ext = module.auto_populate

    # generate the DL input data
    aim_ap, dl_ap, comp = auto_populate_ext(aim=config_autopopulated)

    # assemble the extended config
    config_autopopulated['GeneralInformation'].update(aim_ap)
    config_autopopulated.update({'DL': dl_ap})

    # return the extended config data and the component quantities
    return config_autopopulated, comp
