#!/usr/bin/python

# Copyright (c) 2014 Intel, Inc.
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

import os
import sys
import fcntl
import struct
import termios

from mic import msger
from mic.utils import runner
from mic.utils.errors import CreatorError
from mic.utils.safeurl import SafeURL

from urlgrabber import grabber
from urlgrabber import __version__ as grabber_version

def myurlgrab(url, filename, proxies, progress_obj = None):
    g = grabber.URLGrabber()
    if progress_obj is None:
        progress_obj = TextProgress()

    if url.startswith("file:/"):
        filepath = "/%s" % url.replace("file:", "").lstrip('/')
        if not os.path.exists(filepath):
            raise CreatorError("URLGrabber error: can't find file %s" % url)
        if url.endswith('.rpm'):
            return filepath
        else:
            # untouch repometadata in source path
            runner.show(['cp', '-f', filepath, filename])

    else:
        try:
            # cast url to str here, sometimes it can be unicode,
            # but pycurl only accept str
            filename = g.urlgrab(url=str(url),
                                 filename=filename,
                                 ssl_verify_host=False,
                                 ssl_verify_peer=False,
                                 proxies=proxies,
                                 http_headers=(('Pragma', 'no-cache'),),
                                 quote=0,
                                 progress_obj=progress_obj)
        except grabber.URLGrabError, err:
            tmp = SafeURL(url)
            msg = str(err)

            if msg.find(url) < 0:
                msg += ' on %s' % tmp
            else:
                msg = msg.replace(url, tmp)

            raise CreatorError(msg)

    return filename

def terminal_width(fd=1):
    """ Get the real terminal width """
    try:
        buf = 'abcdefgh'
        buf = fcntl.ioctl(fd, termios.TIOCGWINSZ, buf)
        return struct.unpack('hhhh', buf)[1]
    except: # IOError
        return 80

def truncate_url(url, width):
    return os.path.basename(url)[0:width]

class TextProgress(object):
    # make the class as singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TextProgress, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, totalnum = None):
        self.total = totalnum
        self.counter = 1

    def start(self, filename, url, *args, **kwargs):
        self.url = url
        self.termwidth = terminal_width()
        if self.total is None:
            msger.info("Retrieving %s ..." % truncate_url(self.url, self.termwidth - 15))
        else:
            msger.info("Retrieving %s [%d/%d] ..." % (truncate_url(self.url, self.termwidth - 25), self.counter, self.total))

    def update(self, *args):
        pass

    def end(self, *args):
        if self.counter == self.total:
            msger.raw("\n")

        if self.total is not None:
            self.counter += 1

