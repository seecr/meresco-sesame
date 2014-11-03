#!/usr/bin/env python
# -*- coding: utf-8 -*-
## begin license ##
#
# The Meresco Sesame package is an Sesame Triplestore based on meresco-triplestore
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
#
# This file is part of "Meresco Sesame"
#
# "Meresco Sesame" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Sesame" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Sesame"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from glob import glob                               #DO_NOT_DISTRIBUTE
from sys import path as systemPath                  #DO_NOT_DISTRIBUTE
from os.path import abspath, dirname                #DO_NOT_DISTRIBUTE
projectdir = dirname(dirname(abspath(__file__)))    #DO_NOT_DISTRIBUTE
for path in glob('%s/deps.d/*' % projectdir):       #DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE
for path in glob('%s/deps.d/*/client' % projectdir):#DO_NOT_DISTRIBUTE
    systemPath.insert(0, path)                      #DO_NOT_DISTRIBUTE

from sys import argv

from seecr.test.testrunner import TestRunner

from integration.sesameintegrationstate import SesameIntegrationState


if __name__ == '__main__':
    flags = ['--fast']
    fastMode = '--fast' in argv
    for flag in flags:
        if flag in argv:
            argv.remove(flag)

    runner = TestRunner()
    SesameIntegrationState(
        'default',
        tests=[
            'integration.sesametest.SesameTest'
        ],
        fastMode=fastMode).addToTestRunner(runner)

    testnames = argv[1:]
    runner.run(testnames)

