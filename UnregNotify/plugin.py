###
# Copyright (c) 2018, Michael Lustfield
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

# Module imports
import time

# Base imports
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircdb as ircdb
import supybot.world as world
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('UnregNotify')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class UnregNotify(callbacks.Plugin):
    '''Provide administrative control over wiki to authorized users.'''
    threaded = True
    def __init__(self, irc):
        self.__parent = super(UnregNotify, self)
        self.__parent.__init__(irc)

    def doJoin(self, irc, msg):
        nick = ircutils.toLower(msg.nick)
        if len(msg.args) < 2:
            # extended-join is not supported
            return
        channel = msg.args[0].split(',')[0]
        account = msg.args[1]
        if ircutils.strEqual(irc.nick, msg.nick):
            # message from self
            return
        if 'batch' in msg.server_tags and \
                msg.server_tags['batch'] in irc.state.batches and \
                irc.state.batches[msg.server_tags['batch']].type == 'netjoin':
            # ignore netjoin
            return
        if not ircutils.isChannel(channel) or channel not in irc.state.channels:
            return
        if not self.registryValue('enabled', channel):
            return

        if account == '*':
            irc.queueMsg(ircmsgs.notice(nick,
                    'You joined {}, but you are not identified to services and cannot speak.'
                    ' For help with identification, type "/msg nickserv help register"'.format(channel)))


Class = UnregNotify
