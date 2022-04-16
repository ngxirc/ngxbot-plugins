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
import requests

# Base imports
from supybot.commands import wrap, optional
import supybot.callbacks
import supybot.ircdb
import supybot.world

# i18n
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('PbinAdmin')
except ImportError:
    def _(x):
        '''Placeholder function if i18n can't be loaded.'''
        return x


class PbinAdmin(supybot.callbacks.Plugin):
    '''Provide administrative control over wiki to authorized users.'''
    threaded = True

    def __init__(self, irc):
        self.__parent = super(PbinAdmin, self)
        self.__parent.__init__(irc)

    @wrap([optional('channel'), 'somethingWithoutSpaces'])
    def whitelist(self, irc, msg, args, channel, address):
        '''[<channel>] <address>

        Add a registered subnet to whitelist for specified IP address.'''
        return self._cmd_wrapper(irc, msg, args, address, 'wl')

    @wrap([optional('channel'), 'somethingWithoutSpaces'])
    def greylist(self, irc, msg, args, channel, paste_id):
        '''[<channel>] <paste_id>

        Add address for specified paste to grey list.'''
        return self._cmd_wrapper(irc, msg, args, paste_id, 'gl')

    @wrap([optional('channel'), 'somethingWithoutSpaces'])
    def blacklist(self, irc, msg, args, channel, paste_id):
        '''[<channel>] <paste_id>

        Add address for specified paste to black list.'''
        return self._cmd_wrapper(irc, msg, args, paste_id, 'bl')

    @wrap([optional('channel'), 'somethingWithoutSpaces'])
    def delete(self, irc, msg, args, channel, paste_id):
        '''[<channel>] <paste_id>

        Delete a paste with specified ID.'''
        return self._cmd_wrapper(irc, msg, args, paste_id, 'del')

    def _cmd_wrapper(self, irc, msg, args, target, command):
        '''Send request to the API server after performing sanity checks.'''
        # Pre-flight checks
        if not self.registryValue('enabled', msg.args[0]):
            return None

        # Check capability
        if not supybot.ircdb.checkCapability(msg.prefix, 'pbinadmin'):
            if not supybot.world.testing:
                irc.errorNoCapability('pbinadmin', Raise=True)

        # Send API request
        resp = requests.post(
            self.registryValue('api_host', msg.args[0]),
            json={
                'token': self.registryValue('api_token', msg.args[0]),
                'command': command,
                'target': target},
            headers={'Content-type': 'application/json'})
        if not resp:
            irc.error(_('No response data from API request.'), Raise=True)
        if resp.status_code != 200:
            irc.error(_('Unexpected status code received: %s') % (resp.status_code), Raise=True)

        rdata = resp.json()
        if not rdata:
            irc.error(_('No data decoded.'), Raise=True)

        if rdata.get('status', '') == 'error':
            irc.error(rdata.get('message', _('Unexpected server response.')), Raise=True)
        irc.reply(rdata.get('message', _('Missing server response')))


Class = PbinAdmin
