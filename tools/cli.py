#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A tool for creating Android sparse image files (.simg) from a block mapped file (.bmap)
"""

import argparse
import sys
import os
import stat
import time
import logging
import tempfile
import traceback
import shutil
import io

from tools import BmapParser
from tools import SimgWriter

VERSION = "0.1"

log = logging.getLogger()

def parse_arguments():
    """A helper function which parses the input arguments."""
    text = sys.modules[__name__].__doc__
    parser = argparse.ArgumentParser(description=text)

    # The --version option
    parser.add_argument("--version", action="version",
                        version="%(prog)s " + "%s" % VERSION)

    # The --quiet option
    text = "be quiet"
    parser.add_argument("-q", "--quiet", action="store_true", help=text)

    # The --debug option
    text = "print debugging information"
    parser.add_argument("-d", "--debug", action="store_true", help=text)

    # Mandatory command-line argument - image file
    text = "the block mapped image to generate Android sparse image from (e.g. .wic, .img, .ext4, ..)"
    parser.add_argument("image", help=text)

    # Mandatory command-line argument - bmap file
    text = "the block map file (.bmap) for the image. Generated from bmaptools"
    parser.add_argument("bmap", help=text)

    # Mandatory command-line argument - output file
    text = "the output file for the generated Android sparse image file (.simg)"
    parser.add_argument("output", help=text)

    return parser.parse_args()


def setup_logger(loglevel):
    """
    A helper function which configures the root logger. The log level is
    initialized to 'loglevel'.
    """

    # Esc-sequences for coloured output
    esc_red = '\033[91m'     # pylint: disable=W1401
    esc_yellow = '\033[93m'  # pylint: disable=W1401
    esc_green = '\033[92m'   # pylint: disable=W1401
    esc_end = '\033[0m'      # pylint: disable=W1401

    class MyFormatter(logging.Formatter):
        """
        A custom formatter for logging messages. The reason we have it is to
        have different format for different log levels.
        """

        def __init__(self, fmt=None, datefmt=None):
            """The constructor."""
            logging.Formatter.__init__(self, fmt, datefmt)

            self._orig_fmt = self._fmt
            # Prefix with green-colored time-stamp, as well as with module name
            # and line number
            self._dbg_fmt = "[" + esc_green + "%(asctime)s" + esc_end + \
                            "] [%(module)s,%(lineno)d] " + self._fmt

        def format(self, record):
            """
            The formatter which which simply prefixes all debugging messages
            with a time-stamp.
            """

            if record.levelno == logging.DEBUG:
                self._fmt = self._dbg_fmt

            result = logging.Formatter.format(self, record)
            self._fmt = self._orig_fmt
            return result

    # Change log level names to something nicer than the default all-capital
    # 'INFO' etc.
    logging.addLevelName(logging.ERROR, esc_red + "ERROR" + esc_end)
    logging.addLevelName(logging.WARNING, esc_yellow + "WARNING" + esc_end)
    logging.addLevelName(logging.DEBUG, "debug")
    logging.addLevelName(logging.INFO, "info")

    log.setLevel(loglevel)
    formatter = MyFormatter("bmap2simg: %(levelname)s: %(message)s", "%H:%M:%S")
    where = logging.StreamHandler(sys.stderr)
    where.setFormatter(formatter)
    log.addHandler(where)

def main():
    """Script entry point."""
    args = parse_arguments()

    if args.quiet:
        loglevel = logging.WARNING
    elif args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    setup_logger(loglevel)
    parser = BmapParser.BmapParser(args.bmap)
    block_size = parser.get_block_size()
    img_writer = SimgWriter.SimgWriter(args.image, args.output)
    
    old_last = 0
    for (first, last, chksum) in parser.get_block_ranges():
        log.debug("Range. start=%d, end=%d, checksum=%s" % (first, last, chksum))

        if old_last < first:
            diff_b = (first - old_last -1) * block_size
            img_writer.add_dont_care_chunk(diff_b)

        old_last = last

        iterator = parser.get_batches(first, last)
        for (start, end, length) in iterator:
            log.debug("Batch. start=%d, end=%d, length=%d" % (start, end, length))
            offset_b = start*block_size
            length_b = length*block_size
            img_writer.add_data_chunk(offset_b, length_b)
    
    img_writer.finalize()

if __name__ == "__main__":
    sys.exit(main())