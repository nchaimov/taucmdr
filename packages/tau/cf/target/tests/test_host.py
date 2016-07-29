# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, ParaTools, Inc.
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
"""Test functions.

Functions used for unit tests of host.py.
"""

from tau.tests import TestCase

from tau.cf.compiler import CC_ROLE
from tau.cf.target import host

class HostTest(TestCase):
    """Unit tests for tau.cf.target.host"""
    # pylint: disable=invalid-name
    
    def test_architecture_not_empty(self):
        self.assertNotEqual(host.architecture(), '')

    def test_os_not_empty(self):
        self.assertNotEqual(host.operating_system(), '')
    
    def test_tau_arch_not_empty(self):
        self.assertNotEqual(host.tau_arch(), '')
    
    def test_preferred_compilers_not_empty(self):
        self.assertNotEqual(host.preferred_compilers(), '')
    
    def test_preffered_mpi_compilers_not_empty(self):
        self.assertNotEqual(host.preferred_mpi_compilers(), '')
    
    def test_default_compilers_not_empty(self):
        self.assertNotEqual(host.default_compilers(), '')
    
    def test_default_mpi_compilers_not_empty(self):
        self.assertNotEqual(host.default_mpi_compilers(), '')
    
    def test_default_compiler_not_empty(self):
        self.assertNotEqual(host.default_compiler(CC_ROLE), '')