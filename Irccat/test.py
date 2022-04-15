###
# Copyright (c) 2013, Alec Leamas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

# Unused wildcard imports:
# pylint: disable=W0614,W0401
# Missing docstrings:
# pylint: disable=C0111
# supybot's typenames are irregular
# Too many public methods:
# pylint: disable=R0904


import os
import os.path
import socket
import subprocess

from supybot.test import *

from . import config
from . import plugin as irccat

CLIENT = os.path.join(os.path.dirname(__file__), 'irccat')

def clear_sections(testcase):
    if os.path.exists('test-sections.pickle'):
        os.unlink('test-sections.pickle')
    config.global_option('sectionspath').setValue('test-sections.pickle')
    config.global_option('port').setValue(23456)

def communicate(msg, sendonly):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', 23456))
        s.sendall(msg)

        if not sendonly:
            data = []
            try:
                data.append([s.recv(1024)])
                while data[-1]:
                    data.append(s.recv(1024))
            except socket.timeout:
                pass
            return b''.join(data)
    finally:
        s.close()


class IrccatTestList(PluginTestCase):
    plugins = ('Irccat', 'User')

    def setUp(self, nick='test'):      # pylint: disable=W0221
        clear_sections(self)
        PluginTestCase.setUp(self)
        self.assertNotError('reload Irccat')
        self.assertNotError('register suptest suptest')
        self.assertNotError('sectiondata ivar ivar #al-bot-test')

    def testList(self):
        self.assertResponse('sectionlist', 'ivar')


class IrccatTestCopy(ChannelPluginTestCase):
    plugins = ('Irccat', 'User')
    channel = '#test'

    def setUp(self, nick='test'):      # pylint: disable=W0221
        clear_sections(self)
        ChannelPluginTestCase.setUp(self)
        self.assertNotError('reload Irccat', private = True)
        self.assertNotError('register suptest suptest', private = True)
        self.assertNotError('sectiondata ivar ivarpw #test', private = True)

    def testCopy(self):
        communicate(b'ivar;ivarpw;ivar data\n', sendonly=True)
        result = self.getMsg(' ')
        self.assertIsNot(result, None)
        self.assertEqual(result.args[1], 'ivar data')

    def testBadFormat(self):
        communicate(b'ivar;ivarpw data\n', sendonly=True)
        self.assertRegexp(' ', 'Illegal format.*')

    def testBadPw(self):
        communicate(b'ivar;ivarpw22;ivar data\n', sendonly=True)
        self.assertRegexp(' ', 'Bad password.*')

    def testBadSection(self):
        communicate(b'ivaru22;ivarpw22;ivar data\n', sendonly=True)
        self.assertRegexp(' ', 'No such section.*')


class IrccatTestIrccat(ChannelPluginTestCase):
    plugins = ('Irccat', 'User')
    channel = '#test'
    cmd_tmpl = "echo '%s' | nc --send-only localhost 23456"

    def setUp(self, nick='test'):      # pylint: disable=W0221
        clear_sections(self)
        ChannelPluginTestCase.setUp(self)
        self.assertNotError('reload Irccat', private = True)
        self.assertNotError('register suptest suptest', private = True)
        self.assertNotError('sectiondata ivar ivarpw #test', private = True)

    def testIrccatEnvPw(self):
        cmd = 'IRCCAT_PASSWORD=ivarpw %s' \
              ' localhost 23456 ivar ivar data'
        subprocess.check_call(cmd % CLIENT, shell = True)
        self.assertResponse(' ', 'ivar data')

    def testIrccatStdinPw(self):
        cmd = '%s -s  localhost 23456 ivar ivar data'
        p = subprocess.Popen(cmd % CLIENT, shell = True, stdin = subprocess.PIPE)
        p.communicate(b'ivarpw\n')
        self.assertResponse(' ', 'ivar data')

    def testIrccatBadCmdline(self):
        cmd = 'IRCCAT_PASSWORD=ivarpw %s' \
              ' localhost 23456'
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_output(cmd % CLIENT, shell = True)

    def testIrccatBadPort(self):
        cmd = 'IRCCAT_PASSWORD=ivarpw %s' \
              ' localhost 23456xx ivar ivar data'
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_output(cmd % CLIENT, shell = True)


class IrccatTestData(PluginTestCase):
    plugins = ('Irccat', 'User')

    def setUp(self, nick='test'):      # pylint: disable=W0221
        clear_sections(self)
        PluginTestCase.setUp(self)
        self.assertNotError('reload Irccat')
        self.assertNotError('sectiondata ivar ivar #al-bot-test')
        self.assertNotError('sectiondata yngve yngve #al-bot-test')

    def testList(self):
        m = self._feedMsg('sectionlist')
        self.assertIn(m.args[1], ('yngve ivar', 'ivar yngve'))

    def testReload(self):
        self.assertResponse('reload Irccat', 'The operation succeeded.')

    def testShow(self):
        self.assertRegexp('sectionshow yngve', '.*#al-bot-test$')

    def testKill(self):
        self.assertNotError('sectionkill yngve')
        self.assertResponse('sectionlist', 'ivar')

    def testKillBadSection(self):
        self.assertResponse('sectionkill tore', 'Error: no such section')


class BlacklistTest(SupyTestCase):

    def setUp(self):
        SupyTestCase.setUp(self)
        self.blacklist = None

    def testBlock(self):
        self.blacklist = irccat._Blacklist()    # pylint: disable=W0212
        self.blacklist.FailMax = 5
        self.blacklist.BlockTime = 0.2

        host = '132.132.132.132'
        self.assertFalse(self.blacklist.onList(host))
        for i in [1, 2, 3, 4]:                 # pylint: disable=W0612
            self.blacklist.register(host, False)
        self.assertFalse(self.blacklist.onList(host))
        self.blacklist.register(host, False)
        self.assertTrue(self.blacklist.onList(host))
        time.sleep(0.25)
        self.assertFalse(self.blacklist.onList(host))
        for i in [1, 2, 3, 4, 5]:
            self.blacklist.register(host, False)
        self.assertTrue(self.blacklist.onList(host))

#
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
