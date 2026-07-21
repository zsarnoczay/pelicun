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

"""Provides a command-line interface for Pelicun."""

from __future__ import annotations

import argparse

from pelicun.tools.regional_sim import regional_sim

DLML_NOTICE = """\
The Damage and Loss Model Library now installs together with pelicun as the
`simcenter-dlml` Python package, so the default model data is always
available and no separate download is needed. To update the model library,
upgrade that package:

    pip install --upgrade simcenter-dlml

The `pelicun dlml` command no longer performs downloads; it is kept only so
that existing scripts calling it continue to work. It is planned for
removal in pelicun 3.12.\
"""


def main() -> None:
    """
    Provide main command-line interface for Pelicun.

    This function dispatches subcommands.

    """
    # Define comprehensive usage examples
    examples = """
Examples:
  Regional Simulation:
    pelicun regional_sim                          # Use default config file (inputRWHALE.json)
    pelicun regional_sim my_config.json           # Use custom config file
    pelicun regional_sim -n 4                     # Use 4 CPU cores with default config
    pelicun regional_sim my_config.json -n 8      # Use custom config with 8 CPU cores

  DLML Data Management:
    pelicun dlml                                  # Explain how DLML data is managed

  Getting Help:
    pelicun --help                                # Show this help message
    pelicun regional_sim --help                   # Show regional_sim specific help
    pelicun dlml --help                           # Show dlml specific help
"""

    # Main parser
    parser = argparse.ArgumentParser(
        description='Main command-line interface for Pelicun.',
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest='subcommand', required=True, help='Available subcommands'
    )

    # Create the parser for the "regional_sim" subcommand
    parser_regional = subparsers.add_parser(
        'regional_sim', help='Perform a regional-scale disaster impact simulation.'
    )

    # Add the arguments specific to regional_sim
    parser_regional.add_argument(
        'config_file',
        nargs='?',
        default='inputRWHALE.json',
        help='Path to the input configuration JSON file. '
        "Defaults to 'inputRWHALE.json'.",
    )
    parser_regional.add_argument(
        '-n',
        '--num-cores',
        type=int,
        default=None,
        help='Number of CPU cores to use for parallel processing. '
        'Defaults to all available cores minus one.',
    )
    # Associate the regional_sim function with this subparser
    parser_regional.set_defaults(func=regional_sim)

    # Create the parser for the "dlml" subcommand. The Damage and Loss
    # Model Library data now installs with pelicun as the
    # `simcenter-dlml` package, so this subcommand only explains how to
    # manage the data. It accepts (and ignores) the arguments of the
    # retired `pelicun dlml update` interface, so existing scripts that
    # call it keep working. The stub (and its tests in
    # tests/basic/test_cli.py) is scheduled for removal in pelicun 3.12.
    parser_dlml = subparsers.add_parser(
        'dlml',
        help='Explain how DLML (Damage and Loss Model Library) data is managed.',
        description=DLML_NOTICE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_dlml.add_argument(
        'legacy_args',
        nargs=argparse.REMAINDER,
        metavar='...',
        help='Ignored. Arguments of the retired "pelicun dlml update" '
        'interface are accepted for backward compatibility.',
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    # Call the function associated with the chosen subcommand
    if args.subcommand == 'regional_sim':
        args.func(config_file=args.config_file, num_cores=args.num_cores)
    elif args.subcommand == 'dlml':
        print(DLML_NOTICE)  # noqa: T201


if __name__ == '__main__':
    main()
