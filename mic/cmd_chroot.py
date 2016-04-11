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

"""Implementation of subcmd: chroot
"""

import os
import os, sys, re
import pwd
import argparse

from mic import msger
from mic.utils import misc, errors
from mic.conf import configmgr
from mic.plugin import pluginmgr

def _root_confirm():
    """Make sure command is called by root
    There are a lot of commands needed to be run during creating images,
    some of them must be run with root privilege like mount, kpartx"""
    if os.geteuid() != 0:
        msger.error('Root permission is required to continue, abort')
            
def main(parser, args, argv):
    """mic choot entry point."""

    #args is argparser namespace, argv is the input cmd line
    if args is None:
        raise errors.Usage("Invalid arguments")

    targetimage = args.imagefile
    if not os.path.exists(targetimage):
        raise errors.CreatorError("Cannot find the image: %s"
                                  % targetimage)

    _root_confirm()

    configmgr.chroot['saveto'] = args.saveto

    imagetype = misc.get_image_type(targetimage)
    if imagetype in ("ext3fsimg", "ext4fsimg", "btrfsimg"):
        imagetype = "loop"

    chrootclass = None
    for pname, pcls in pluginmgr.get_plugins('imager').iteritems():
        if pname == imagetype and hasattr(pcls, "do_chroot"):
            chrootclass = pcls
            break

    if not chrootclass:
        raise errors.CreatorError("Cannot support image type: %s" \
                                  % imagetype)

    chrootclass.do_chroot(targetimage, args.cmd)
        
    
