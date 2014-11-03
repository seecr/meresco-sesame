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

from os import system
from os.path import join, dirname, abspath

from seecr.test.integrationtestcase import IntegrationState
from seecr.test.portnumbergenerator import PortNumberGenerator


myDir = dirname(abspath(__file__))
serverBinDir = join(dirname(dirname(myDir)), 'bin')

class SesameIntegrationState(IntegrationState):
    def __init__(self, stateName, tests=None, fastMode=False):
        IntegrationState.__init__(self, stateName=stateName, tests=tests, fastMode=fastMode)

        self.sesameDataDir = join(self.integrationTempdir, 'sesame-data')
        self.sesamePort = PortNumberGenerator.next()
        self.testdataDir = join(dirname(myDir), 'data')
        if not fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents ' + self.sesameDataDir)

    def setUp(self):
        self.startSesameServer()

    def binDir(self):
        return serverBinDir

    def startSesameServer(self):
        self._startServer('sesame', self.binPath('start-sesame'), 'http://localhost:%s/query' % self.sesamePort, port=self.sesamePort, stateDir=self.sesameDataDir, name='sesame')

    def restartSesameServer(self):
        self.stopSesameServer()
        self.startSesameServer()

    def stopSesameServer(self):
        self._stopServer('sesame')

