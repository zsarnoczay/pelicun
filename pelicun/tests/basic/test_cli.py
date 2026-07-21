#
# Copyright (c) 2025 Leland Stanford Junior University
# Copyright (c) 2025 The Regents of the University of California
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

"""These are unit tests for the command-line interface of pelicun."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys
from typing import TYPE_CHECKING

from pelicun.cli import main

if TYPE_CHECKING:
    import pytest


def test_dlml_stub_prints_notice(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A bare `pelicun dlml` prints the informational notice."""
    monkeypatch.setattr(sys, 'argv', ['pelicun', 'dlml'])

    main()

    captured = capsys.readouterr()
    assert 'simcenter-dlml' in captured.out
    assert 'pip install --upgrade simcenter-dlml' in captured.out
    assert 'no longer performs downloads' in captured.out
    assert 'removal in pelicun 3.12' in captured.out


def test_dlml_stub_accepts_legacy_arguments(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Retired `pelicun dlml update ...` invocations still succeed."""
    monkeypatch.setattr(
        sys, 'argv', ['pelicun', 'dlml', 'update', '--no-cache', 'v2.1.0']
    )

    main()

    captured = capsys.readouterr()
    assert 'simcenter-dlml' in captured.out


def test_dlml_stub_exit_code() -> None:
    """`pelicun dlml update` exits with code 0 in a real subprocess."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'pelicun', 'dlml', 'update', 'latest'],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert 'simcenter-dlml' in result.stdout
