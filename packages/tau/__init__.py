# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, ParaTools, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# (1) Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
# (2) Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
# (3) Neither the name of ParaTools, Inc. nor the names of its contributors may
#     be used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""TAU Commander package initialization.

The first line of this file is the first thing to be executed whenever TAU Commander
is invoked in any way. This module establishes global constants (as few as possible)
and checks the Python version.  It must be kept as short and simple as possible.
"""

import os
import sys


EXIT_FAILURE = -100
"""int: Process exit code indicating unrecoverable failure."""

EXIT_WARNING = 100
"""int: Process exit code indicating non-optimal condition on exit."""

EXIT_SUCCESS = 0
"""int: Process exit code indicating successful operation."""

HELP_CONTACT = '<support@paratools.com>'
"""str: E-mail address users should contact for help."""

PROJECT_URL = 'http://www.taucommander.com/'
"""str: URL of the TAU Commander project."""

MINIMUM_PYTHON_VERSION = (2, 7)
"""tuple: Minimum required Python version for TAU Comamnder.

A tuple of at least (MAJOR, MINOR) directly comparible to :any:`sys.version_info`
"""

if sys.version_info < MINIMUM_PYTHON_VERSION:
    VERSION = '.'.join([str(x) for x in sys.version_info[0:3]])
    EXPECTED = '.'.join([str(x) for x in MINIMUM_PYTHON_VERSION])
    sys.stderr.write("""%s
%s
%s
Your Python version is %s but Python %s or later is required.
Please update Python or contact %s for support.
""" % (PROJECT_URL, sys.executable, sys.version, VERSION, EXPECTED, HELP_CONTACT))
    sys.exit(EXIT_FAILURE)

TAU_HOME = os.path.realpath(os.path.abspath(os.environ['__TAU_HOME__']))
"""str: Absolute path to the top-level TAU Commander directory.

This directory contains at least `bin`, `docs`, and `packages` directories and is the root
for system-level package installation paths. **Do not** change it once it is set.
"""

TAU_SCRIPT = os.environ['__TAU_SCRIPT__']
"""str: Script that launched TAU Commander.

Mainly used for help messages. **Do not** change it once it is set.
"""

SYSTEM_PREFIX = os.path.join(TAU_HOME, '.system')
"""str: Absolute path to system-level TAU Commander files.

System-level software package installation prefix and home for system-level projects.
Do not** change it once it is set.
"""

USER_PREFIX = os.path.join(os.path.expanduser('~'), '.tau')
"""str: Absolute path to user-level TAU Commander files.

User-level software package installation prefix and home for user-level projects.
**Do not** change it once it is set.
"""