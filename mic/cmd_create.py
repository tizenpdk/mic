#!/usr/bin/python -tt
# vim: ai ts=4 sts=4 et sw=4
#
# Copyright (c) 2012 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""Implementation of subcmd: create
"""

import os
import os, sys, re
import pwd
import argparse

from mic import msger
from mic.utils import errors, rpmmisc
from mic.conf import configmgr
from mic.plugin import pluginmgr

def main(parser, args, argv):
    """mic create entry point."""
    #args is argparser namespace, argv is the input cmd line
    if args is None:
        raise errors.Usage("Invalid arguments")

    if not os.path.exists(args.ksfile):
        raise errors.CreatorError("Can't find the file: %s" % args.ksfile)

    if os.geteuid() != 0:
        msger.error("Root permission is required, abort")
        
    try:
        w = pwd.getpwuid(os.geteuid())
    except KeyError:
        msger.warning("Might fail in compressing stage for undetermined user")
    
    abspath = lambda pth: os.path.abspath(os.path.expanduser(pth))
    if args.logfile:
        logfile_abs_path = abspath(args.logfile)
        if os.path.isdir(logfile_abs_path):
            raise errors.Usage("logfile's path %s should be file"
                               % args.logfile)
        configmgr.create['logfile'] = logfile_abs_path
        configmgr.set_logfile()

    if args.subcommand == "auto":
        do_auto(parser, args.ksfile, argv)
        return

    if args.interactive:
        msger.enable_interactive()
    else:
        msger.disable_interactive()

    if args.verbose:
        msger.set_loglevel('VERBOSE')

    if args.debug:
        try:
            import rpm
            rpm.setVerbosity(rpm.RPMLOG_NOTICE)
        except ImportError:
            pass

        msger.set_loglevel('DEBUG')

    #check the imager type
    createrClass = None
    for subcmd, klass in pluginmgr.get_plugins('imager').iteritems():
        if subcmd == args.subcommand and hasattr(klass, 'do_create'):
            createrClass = klass

    if createrClass is None:
        raise errors.CreatorError("Can't support subcommand %s" % args.subcommand)

    if args.config:
        configmgr.reset()
        configmgr._siteconf = args.config

    if args.outdir is not None:
        configmgr.create['outdir'] = abspath(args.outdir)
    if args.cachedir is not None:
        configmgr.create['cachedir'] = abspath(args.cachedir)
    os.environ['ZYPP_LOCKFILE_ROOT'] = configmgr.create['cachedir']

    for cdir in ('outdir', 'cachedir'):
        if os.path.exists(configmgr.create[cdir]) \
          and not os.path.isdir(configmgr.create[cdir]):
            raise errors.Usage('Invalid directory specified: %s' \
                               % configmgr.create[cdir])
        if not os.path.exists(configmgr.create[cdir]):
            os.makedirs(configmgr.create[cdir])
            if os.getenv('SUDO_UID', '') and os.getenv('SUDO_GID', ''):
                os.chown(configmgr.create[cdir],
                         int(os.getenv('SUDO_UID')),
                         int(os.getenv('SUDO_GID')))

    if args.local_pkgs_path is not None:
        if not os.path.exists(args.local_pkgs_path):
            raise errors.Usage('Local pkgs directory: \'%s\' not exist' \
                          % args.local_pkgs_path)
        configmgr.create['local_pkgs_path'] = args.local_pkgs_path

    if args.release:
        configmgr.create['release'] = args.release.rstrip('/')

    if args.record_pkgs:
        configmgr.create['record_pkgs'] = []
        for infotype in args.record_pkgs.split(','):
            if infotype not in ('name', 'content', 'license', 'vcs'):
                raise errors.Usage('Invalid pkg recording: %s, valid ones:'
                                   ' "name", "content", "license", "vcs"' \
                                   % infotype)

            configmgr.create['record_pkgs'].append(infotype)

    if args.strict_mode:
      configmgr.create['strict_mode'] = args.strict_mode
    if args.arch is not None:
        supported_arch = sorted(rpmmisc.archPolicies.keys(), reverse=True)
        if args.arch in supported_arch:
            configmgr.create['arch'] = args.arch
        else:
            raise errors.Usage('Invalid architecture: "%s".\n'
                               '  Supported architectures are: \n'
                               '  %s' % (args.arch,
                                           ', '.join(supported_arch)))

    if args.pkgmgr is not None:
        configmgr.create['pkgmgr'] = args.pkgmgr

    if args.runtime:
        configmgr.set_runtime(args.runtime)

    if args.pack_to is not None:
        configmgr.create['pack_to'] = args.pack_to

    if args.copy_kernel:
        configmgr.create['copy_kernel'] = args.copy_kernel

    if args.install_pkgs:
        configmgr.create['install_pkgs'] = []
        for pkgtype in args.install_pkgs.split(','):
            if pkgtype not in ('source', 'debuginfo', 'debugsource'):
                raise errors.Usage('Invalid parameter specified: "%s", '
                                   'valid values: source, debuginfo, '
                                   'debusource' % pkgtype)

            configmgr.create['install_pkgs'].append(pkgtype)

    if args.check_pkgs:
        for pkg in args.check_pkgs.split(','):
            configmgr.create['check_pkgs'].append(pkg)

    if args.enabletmpfs:
        configmgr.create['enabletmpfs'] = args.enabletmpfs

    if args.repourl:
        for item in args.repourl:
            try:
                key, val = item.split('=')
            except:
                continue
            configmgr.create['repourl'][key] = val

    if args.repo:
        for optvalue in args.repo:
            repo = {}
            for item in optvalue.split(';'):
                try:
                    key, val = item.split('=')
                except:
                    continue
                repo[key.strip()] = val.strip()
            if 'name' in repo:
                configmgr.create['extrarepos'][repo['name']] = repo

    if args.ignore_ksrepo:
        configmgr.create['ignore_ksrepo'] = args.ignore_ksrepo
    if args.run_script:
        configmgr.create['run_script'] = args.run_script

    creater = createrClass()
    creater.do_create(args)

def do_auto(parser, ksfile, argv):
        """${cmd_name}: auto detect image type from magic header

        Usage:
            ${name} ${cmd_name} <ksfile>

        ${cmd_option_list}
        """
        def parse_magic_line(re_str, pstr, ptype='mic'):
            ptn = re.compile(re_str)
            m = ptn.match(pstr)
            if not m or not m.groups():
                return None

            inline_argv = m.group(1).strip()
            if ptype == 'mic':
                m2 = re.search('(?P<format>\w+)', inline_argv)
            elif ptype == 'mic2':
                m2 = re.search('(-f|--format(=)?)\s*(?P<format>\w+)',
                               inline_argv)
            else:
                return None

            if m2:
                cmdname = m2.group('format')
                inline_argv = inline_argv.replace(m2.group(0), '')
                return (cmdname, inline_argv)

            return None

        if not os.path.exists(ksfile):
            raise errors.CreatorError("Can't find the file: %s" % ksfile)

        with open(ksfile, 'r') as rf:
            first_line = rf.readline()

        mic_re = '^#\s*-\*-mic-options-\*-\s+(.*)\s+-\*-mic-options-\*-'
        mic2_re = '^#\s*-\*-mic2-options-\*-\s+(.*)\s+-\*-mic2-options-\*-'

        result = parse_magic_line(mic_re, first_line, 'mic') \
                 or parse_magic_line(mic2_re, first_line, 'mic2')
        if not result:
            raise errors.KsError("Invalid magic line in file: %s" % ksfile)
        
        ksargv = ' '.join(result).split()

        argv.remove("auto")
        index = argv.index("create")
        #insert the subcommand
        argv.insert(index+1, ksargv[0])
        options = argv + ksargv[1:]

        args = parser.parse_args(options)

        main(parser, args, options)

