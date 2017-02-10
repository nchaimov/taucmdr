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
"""Target data model.

:any:`Target` fully describes the hardware and software environment that our
experiments will be performed in.  The hardware architecture, available compilers,
and system libraries are described in the target record.  There will be multiple
target records for any physical computer system since each target record uniquely
describes a specific set of system features.  For example, if both GNU and Intel
compilers are installed then there will target configurations for each compiler family.
"""

import os
import glob
from tau import logger, util
from tau.error import InternalError, ConfigurationError, IncompatibleRecordError
from tau.mvc.model import Model
from tau.model.compiler import Compiler
from tau.cf.platforms import Architecture, OperatingSystem
from tau.cf.platforms import HOST_ARCH, INTEL_KNC, IBM_BGL, IBM_BGP, IBM_BGQ, HOST_OS, DARWIN, CRAY_CNL
from tau.cf.compiler import Knowledgebase, InstalledCompilerSet
from tau.cf.software.tau_installation import TAU_MINIMAL_COMPILERS

LOGGER = logger.get_logger(__name__)


def knc_require_k1om(*_):
    """Compatibility checking callback for use with data models.

    Requires that the Intel k1om tools be installed if the host architecture is KNC.

    Raises:
        ConfigurationError: Invalid compiler family specified in target configuration.
    """
    k1om_ar = util.which('x86_64-k1om-linux-ar')
    if not k1om_ar:
        for path in glob.glob('/usr/linux-k1om-*'):
            k1om_ar = util.which(os.path.join(path, 'bin', 'x86_64-k1om-linux-ar'))
            if k1om_ar:
                break
        else:
            raise ConfigurationError('k1om tools not found', 'Try installing on compute node', 'Install MIC SDK')


def attributes():
    """Construct attributes dictionary for the target model.

    We build the attributes in a function so that classes like ``tau.module.project.Project`` are
    fully initialized and usable in the returned dictionary.

    Returns:
        dict: Attributes dictionary.
    """
    from tau.model.project import Project
    from tau.cli.arguments import ParsePackagePathAction
    from tau.cf.compiler.host import CC, CXX, FC, UPC, INTEL
    from tau.cf.compiler.mpi import MPI_CC, MPI_CXX, MPI_FC, INTEL as INTEL_MPI
    from tau.cf.compiler.shmem import SHMEM_CC, SHMEM_CXX, SHMEM_FC
    from tau.model import require_compiler_family

    knc_intel_only = require_compiler_family(INTEL,
                                             "You must use Intel compilers to target the Xeon Phi",
                                             "Try adding `--compilers=Intel` to the command line")
    knc_intel_mpi_only = require_compiler_family(INTEL_MPI,
                                                 "You must use Intel MPI compilers to target the Xeon Phi",
                                                 "Try adding `--mpi-compilers=Intel` to the command line")

    return {
        'projects': {
            'collection': Project,
            'via': 'targets',
            'description': 'projects using this target'
        },
        'name': {
            'primary_key': True,
            'type': 'string',
            'unique': True,
            'description': 'target configuration name',
            'argparse': {'metavar': '<target_name>'}
        },
        'host_os': {
            'type': 'string',
            'required': True,
            'description': 'host operating system',
            'default': HOST_OS.name,
            'argparse': {'flags': ('--os',),
                         'group': 'host',
                         'metavar': '<os>',
                         'choices': OperatingSystem.keys()},
            'on_change': Target.attribute_changed
        },
        'host_arch': {
            'type': 'string',
            'required': True,
            'description': 'host architecture',
            'default': HOST_ARCH.name,
            'argparse': {'flags': ('--arch',),
                         'group': 'host',
                         'metavar': '<arch>',
                         'choices': Architecture.keys()},
            'compat': {str(INTEL_KNC):
                       (Target.require('host_arch', knc_require_k1om),
                        Target.require(CC.keyword, knc_intel_only),
                        Target.require(CXX.keyword, knc_intel_only),
                        Target.require(FC.keyword, knc_intel_only),
                        Target.require(MPI_CC.keyword, knc_intel_mpi_only),
                        Target.require(MPI_CXX.keyword, knc_intel_mpi_only),
                        Target.require(MPI_FC.keyword, knc_intel_mpi_only))},
            'on_change': Target.attribute_changed
        },
        CC.keyword: {
            'model': Compiler,
            'required': True,
            'description': 'Host C compiler command',
            'argparse': {'flags': ('--cc',),
                         'group': 'host',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        CXX.keyword: {
            'model': Compiler,
            'required': True,
            'description': 'Host C++ compiler command',
            'argparse': {'flags': ('--cxx',),
                         'group': 'host',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        FC.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'Host Fortran compiler command',
            'argparse': {'flags': ('--fc',),
                         'group': 'host',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        UPC.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'Universal Parallel C compiler command',
            'argparse': {'flags': ('--upc',),
                         'group': 'Universal Parallel C',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        MPI_CC.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'MPI C compiler command',
            'argparse': {'flags': ('--mpi-cc',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        MPI_CXX.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'MPI C++ compiler command',
            'argparse': {'flags': ('--mpi-cxx',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        MPI_FC.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'MPI Fortran compiler command',
            'argparse': {'flags': ('--mpi-fc',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        'mpi_include_path': {
            'type': 'array',
            'description': 'paths to search for MPI header files when building MPI applications',
            'argparse': {'flags': ('--mpi-include-path',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<path>',
                         'nargs': '+'},
            'compat': {bool: (Target.require(MPI_CC.keyword),
                              Target.require(MPI_CXX.keyword),
                              Target.require(MPI_FC.keyword))},
            'on_change': Target.attribute_changed
        },
        'mpi_library_path': {
            'type': 'array',
            'description': 'paths to search for MPI library files when building MPI applications',
            'argparse': {'flags': ('--mpi-library-path',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<path>',
                         'nargs': '+'},
            'compat': {bool: (Target.require(MPI_CC.keyword),
                              Target.require(MPI_CXX.keyword),
                              Target.require(MPI_FC.keyword))},
            'on_change': Target.attribute_changed
        },
        'mpi_libraries': {
            'type': 'array',
            'description': 'libraries to link to when building MPI applications',
            'argparse': {'flags': ('--mpi-libraries',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<flag>',
                         'nargs': '+'},
            'compat': {bool: (Target.require(MPI_CC.keyword),
                              Target.require(MPI_CXX.keyword),
                              Target.require(MPI_FC.keyword))},
            'on_change': Target.attribute_changed
        },
        SHMEM_CC.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'SHMEM C compiler command',
            'argparse': {'flags': ('--shmem-cc',),
                         'group': 'Symmetric Hierarchical Memory (SHMEM)',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        SHMEM_CXX.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'SHMEM C++ compiler command',
            'argparse': {'flags': ('--shmem-cxx',),
                         'group': 'Symmetric Hierarchical Memory (SHMEM)',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        SHMEM_FC.keyword: {
            'model': Compiler,
            'required': False,
            'description': 'SHMEM Fortran compiler command',
            'argparse': {'flags': ('--shmem-fc',),
                         'group': 'Symmetric Hierarchical Memory (SHMEM)',
                         'metavar': '<command>'},
            'on_change': Target.attribute_changed
        },
        'shmem_include_path': {
            'type': 'array',
            'description': 'paths to search for SHMEM header files when building SHMEM applications',
            'argparse': {'flags': ('--shmem-include-path',),
                         'group': 'Symmetric Hierarchical Memory (SHMEM)',
                         'metavar': '<path>',
                         'nargs': '+'},
            'on_change': Target.attribute_changed
        },
        'shmem_library_path': {
            'type': 'array',
            'description': 'paths to search for SHMEM library files when building SHMEM applications',
            'argparse': {'flags': ('--shmem-library-path',),
                         'group': 'Symmetric Hierarchical Memory (SHMEM)',
                         'metavar': '<path>',
                         'nargs': '+'},
            'on_change': Target.attribute_changed
        },
        'shmem_libraries': {
            'type': 'array',
            'description': 'libraries to link to when building SHMEM applications',
            'argparse': {'flags': ('--shmem-libraries',),
                         'group': 'Symmetric Hierarchical Memory (SHMEM)',
                         'metavar': '<flag>',
                         'nargs': '+'},
            'on_change': Target.attribute_changed
        },
        'cuda': {
            'type': 'string',
            'description': 'path to NVIDIA CUDA installation (enables OpenCL support)',
            'argparse': {'flags': ('--cuda',),
                         'group': 'software package',
                         'metavar': '<path>',
                         'action': ParsePackagePathAction},
            'on_change': Target.attribute_changed
        },
        'tau_source': {
            'type': 'string',
            'description': 'path or URL to a TAU installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--tau',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|nightly)',
                         'action': ParsePackagePathAction},
            'compat': {True: Target.require('tau_source')},
            'on_change': Target.attribute_changed
        },
        'pdt_source': {
            'type': 'string',
            'description': 'path or URL to a PDT installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--pdt',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction},
            'on_change': Target.attribute_changed
        },
        'binutils_source': {
            'type': 'string',
            'description': 'path or URL to a GNU binutils installation or archive file',
            'default': 'download' if HOST_OS is not DARWIN else None,
            'argparse': {'flags': ('--binutils',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction},
            'compat': {(lambda x: x is not None): Target.discourage('host_os', DARWIN.name)},
            'on_change': Target.attribute_changed
        },
        'libunwind_source': {
            'type': 'string',
            'description': 'path or URL to a libunwind installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--libunwind',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction},
            'on_change': Target.attribute_changed
        },
        'papi_source': {
            'type': 'string',
            'description': 'path or URL to a PAPI installation or archive file',
            'default': 'download' if HOST_OS is not DARWIN else None,
            'argparse': {'flags': ('--papi',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction},
            'compat': {(lambda x: x is not None): Target.discourage('host_os', DARWIN.name)},
            'on_change': Target.attribute_changed
        },
        'scorep_source': {
            'type': 'string',
            'description': 'path or URL to a Score-P installation or archive file',
            'default': 'download' if HOST_OS is not DARWIN else None,
            'argparse': {'flags': ('--scorep',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction},
            'compat': {(lambda x: x is not None): (Target.discourage('host_os', DARWIN.name),
                                                   Target.require(CC.keyword),
                                                   Target.require(CXX.keyword),
                                                   Target.require(FC.keyword))},
            'on_change': Target.attribute_changed
        },
        'forced_makefile': {
            'type': 'string',
            'description': 'Populate target configuration from a TAU Makefile (WARNING: Overrides safety checks)',
            'argparse': {'flags': ('--from-tau-makefile',),
                         'metavar': '<path>'},
            'on_change': Target.attribute_changed
        }
    }


class Target(Model):
    """Target data model."""

    __attributes__ = attributes

    def __init__(self, *args, **kwargs):
        super(Target, self).__init__(*args, **kwargs)
        self._compilers = None

    @classmethod
    def attribute_changed(cls, model, attr, new_value):
        if model.is_selected():
            old_value = model.get(attr, None)
            Target.controller(model.storage).push_to_topic('rebuild_required', {attr: (old_value, new_value)})

    def on_update(self):
        from tau.error import ImmutableRecordError
        from tau.model.experiment import Experiment
        expr_ctrl = Experiment.controller()
        found = expr_ctrl.search({'target': self.eid})
        used_by = [expr['name'] for expr in found if expr.data_size() > 0]
        if used_by:
            raise ImmutableRecordError("Target '%s' cannot be modified because "
                                       "it is used by these experiments: %s" % (self['name'], ', '.join(used_by)))
        for expr in found:
            try:
                expr.verify()
            except IncompatibleRecordError as err:
                raise ConfigurationError("Changing measurement '%s' in this way will create an invalid condition "
                                         "in experiment '%s':\n    %s." % (self['name'], expr['name'], err),
                                         "Delete experiment '%s' and try again." % expr['name'])
    def on_create(self):
        from tau.cf.compiler.host import HOST_COMPILERS
        for role in HOST_COMPILERS.all_roles():
            try:
                record = self.populate(role.keyword)
            except KeyError:
                continue
            path = record['path']
            script_name = 'tau_%s.sh' % os.path.basename(path)
            script_dir=os.path.join(self.storage.prefix, 'bin',)
            script_Fullpath = os.path.join(self.storage.prefix, 'bin',          script_name)
            print script_Fullpath
            #now create a file with script_name that holds
            #'tau <path> $@'
            #and place in script_path
            #1)content
            buff = 'tau ' + path + ' $@ '
            #2)open file and written
            if not os.path.exists(str(self.storage.prefix))
                os.makedirs(str(self.storage.prefix))
            if not os.path.exists(str(script_dir)):
                os.makedirs(str(script_dir))
            wrapFile = open(str(script_Fullpath),"w")
            wrapFile.write(buff)
            wrapFile.close()



    def is_selected(self):
        """Returns True if this target configuration is part of the selected experiment, False otherwise."""
        from tau.model.project import Project, ProjectSelectionError, ExperimentSelectionError
        try:
            selected = Project.controller().selected().experiment()
        except (ProjectSelectionError, ExperimentSelectionError):
            return False
        return selected['target'] == self.eid

    def architecture(self):
        return Architecture.find(self['host_arch'])

    def operating_system(self):
        return OperatingSystem.find(self['host_os'])

    def sources(self):
        """Get paths to all source packages known to this target.

        Returns:
            dict: Software package paths indexed by package name.
        """
        sources = {}
        for attr in self.attributes:
            if attr.endswith('_source'):
                key = attr.replace('_source', '')
                sources[key] = self.get(attr)
        return sources

    def compilers(self):
        """Get information about the compilers used by this target configuration.

        Returns:
            InstalledCompilerSet: Collection of installed compilers used by this target.
        """
        if not self._compilers:
            eids = []
            compilers = {}
            for role in Knowledgebase.all_roles():
                try:
                    compiler_record = self.populate(role.keyword)
                except KeyError:
                    continue
                compilers[role.keyword] = compiler_record.installation()
                LOGGER.debug("compilers[%s] = '%s'", role.keyword, compilers[role.keyword].absolute_path)
                eids.append(compiler_record.eid)
            missing = [role for role in TAU_MINIMAL_COMPILERS if role.keyword not in compilers]
            if missing:
                raise InternalError("Target '%s' is missing required compilers: %s" % (self['name'], missing))
            self._compilers = InstalledCompilerSet('_'.join([str(x) for x in sorted(eids)]), **compilers)
        return self._compilers

    def check_compiler(self, compiler_cmd, compiler_args):
        """Checks a compiler command its arguments for compatibility with this target configuration.

        Checks that the given compiler matches at least one, **but possibly more**, of the compilers
        used in the target. Also performs any special checkes for invalid compiler arguments,
        e.g. -mmic is only for native KNC.

        If the given compiler command and arguments are compatible with this target then information about
        matching compiler installations is returned as a list of n :any:`InstalledCompiler` instances.

        Args:
            compiler_cmd (str): The compiler command as passed by the user.
            compiler_args (list): Compiler command line arguments.

        Returns:
            list: Information about matching installed compilers as :any:`Compiler` instances.

        Raises:
            ConfigurationError: The compiler or command line arguments are incompatible with this target.
        """
        if '-mmic' in compiler_args and self['host_arch'] != str(INTEL_KNC):
            raise ConfigurationError("Host architecture of target '%s' is '%s'"
                                     " but the '-mmic' compiler argument requires '%s'" %
                                     (self['name'], self['host_arch'], INTEL_KNC),
                                     "Select a different target",
                                     "Create a new target with host architecture '%s'" % INTEL_KNC)
        compiler_ctrl = Compiler.controller(self.storage)
        absolute_path = util.which(compiler_cmd)
        compiler_cmd = os.path.basename(compiler_cmd)
        found = []
        known_compilers = [comp for comp in self.compilers().itervalues()]
        for info in Knowledgebase.find_compiler(command=compiler_cmd):
            try:
                compiler_record = self.populate(info.role.keyword)
            except KeyError:
                # Target was not configured with a compiler in this role
                continue
            compiler_path = compiler_record['path']
            if (absolute_path and (compiler_path == absolute_path) or
                    (not absolute_path and (os.path.basename(compiler_path) == compiler_cmd))):
                found.append(compiler_record)
            else:
                # Target was configured with a wrapper compiler so check if that wrapper wraps this compiler
                while 'wrapped' in compiler_record:
                    compiler_record = compiler_ctrl.one(compiler_record['wrapped'])
                    known_compilers.append(compiler_record.installation())
                    compiler_path = compiler_record['path']
                    if (absolute_path and (compiler_path == absolute_path) or
                            (not absolute_path and (os.path.basename(compiler_path) == compiler_cmd))):
                        found.append(compiler_record)
                        break
        if not found:
            parts = ["No compiler in target '%s' matches '%s'." % (self['name'], absolute_path),
                     "The known compiler commands are:"]
            parts.extend('  %s (%s)' % (comp.absolute_path, comp.info.short_descr) for comp in known_compilers)
            hints = ("Try one of the valid compiler commands",
                     "Create and select a new target configuration that uses the '%s' compiler" % absolute_path,
                     "Check loaded modules and the PATH environment variable")
            raise ConfigurationError('\n'.join(parts), *hints)
        return found

    def papi_metrics(self, event_type="PRESET", include_modifiers=False):
        """List PAPI metrics available on this target.

        Returns a list of (name, description) tuples corresponding to the
        requested PAPI event type and possibly the event modifiers.

        Args:
            event_type (str): Either "PRESET" or "NATIVE".
            include_modifiers (bool): If True include event modifiers,
                                      e.g. BR_INST_EXEC:NONTAKEN_COND as well as BR_INST_EXEC.

        Returns:
            list: List of event name/description tuples.
        """
        assert event_type == "PRESET" or event_type == "NATIVE"
        if not self.get('papi_source'):
            return []
        from HTMLParser import HTMLParser
        from tau.cf.software.papi_installation import PapiInstallation
        metrics = []
        html_parser = HTMLParser()
        papi = PapiInstallation(self.sources(), self.architecture(), self.operating_system(), self.compilers())
        def _format(item):
            name = item.attrib['name']
            desc = html_parser.unescape(item.attrib['desc'])
            desc = desc[0].capitalize() + desc[1:] + "."
            return name, desc
        xml_event_info = papi.xml_event_info()
        for eventset in xml_event_info.iter('eventset'):
            if eventset.attrib['type'] == event_type:
                for event in eventset.iter('event'):
                    if include_modifiers:
                        for modifier in event.iter('modifier'):
                            metrics.append(_format(modifier))
                    metrics.append(_format(event))
        return metrics

    def tau_metrics(self):
        """List TAU metrics available on this target.

        Returns a list of (name, description) tuples.

        Returns:
            list: List of event name/description tuples.
        """
        metrics = [("LOGICAL_CLOCK", "Logical clock that increments on each request."),
                   ("USER_CLOCK", ("User-defined clock. Implement "
                                   "'void metric_write_userClock(int tid, double value)'  to set the clock value.")),
                   ("GET_TIME_OF_DAY", "Wall clock that calls gettimeofday."),
                   ("TIME", "Alias for GET_TIME_OF_DAY. Wall clock that calls gettimeofday."),
                   ("CLOCK_GET_TIME", "Wall clock that calls clock_gettime."),
                   ("P_WALL_CLOCK_TIME", "Wall clock that calls PAPI_get_real_usec."),
                   ("PAPI_TIME", "Alias for P_WALL_CLOCK_TIME.  Wall clock that calls PAPI_get_real_usec."),
                   ("P_VIRTUAL_TIME", "PAPI virtual clock that calls PAPI_get_virt_usec."),
                   ("PAPI_VIRTUAL_TIME", ("Alias for P_VIRTUAL_TIME.  "
                                          "PAPI virtual clock that calls PAPI_get_virt_usec.")),
                   ("CPU_TIME", "CPU timer that calls getrusage."),
                   ("LINUX_TIMERS", "Linux high resolution wall clock."),
                   ("TAU_MPI_MESSAGE_SIZE", "Running sum of all MPI messsage sizes."),
                   ("MEMORY_DELTA", "Instantaneous resident set size (RSS)")]
        if self.get('cuda'):
            metrics.append(("TAUGPU_TIME", "Wall clock that uses TAU's GPU timestamps."))
        target_arch = self.architecture()
        target_os = self.operating_system()
        if target_os is CRAY_CNL:
            metrics.extend([("CRAY_TIMERS", "Cray high resolution clock."),
                            ("ENERGY", "Cray Power Monitoring: /sys/cray/pm_counters/energy"),
                            ("ACCEL_ENERGY", "Cray Power Monitoring: /sys/cray/pm_counters/accel_energy")])
        if target_arch is IBM_BGL:
            metrics.append(("BGL_TIMERS", "BlueGene/L high resolution clock."))
        elif target_arch is IBM_BGP:
            metrics.append(("BGP_TIMERS", "BlueGene/P high resolution clock."))
        elif target_arch is IBM_BGQ:
            metrics.append(("BGQ_TIMERS", "BlueGene/Q high resolution clock."))
        return metrics

    def cupti_metrics(self):
        if not self.get('cuda'):
            return []
