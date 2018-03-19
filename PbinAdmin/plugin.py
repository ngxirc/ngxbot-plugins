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
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('PbinAdmin')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class PbinAdmin(callbacks.Plugin):
    """Provide administrative control over wiki to authorized users."""
    threaded = True
    def __init__(self, irc):
        self.__parent = super(PbinAdmin, self)

    def whitelist(self, irc, msg, args, name):
        '''Add a registered subnet to whitelist for specified IP address.'''
        if not capab(msg.prefix, 'pbinadmin'):
            return
        (success, message) =  _run_cmd('wl', addr)

    def greylist(self, irc, msg, args, name):
        '''Add address for specified paste to grey list.'''
        if not capab(msg.prefix, 'pbinadmin'):
            return
        (success, message) =  _run_cmd('gl', paste)

    def blacklist(self, irc, msg, args, name):
        '''Add address for specified paste to black list.'''
        if not capab(msg.prefix, 'pbinadmin'):
            return
        (success, message) =  _run_cmd('bl', paste)

    def delete(self, irc, msg, args, name):
        '''Delete a paste with spefied ID.'''
        if not capab(msg.prefix, 'pbinadmin'):
            return
        (success, message) =  _run_cmd('del', addr)

    def _run_cmd(self, command, target):
        try:
            # TODO: conf.get is an incorrect placeholder
            resp = requests.post(conf.get('api_url'), data = {
                    'token': conf.get('api_token'),
                    'command': command,
                    'target': target})
        except:
            return (False, 'Error during API request.')
        if not resp:
            return (False, 'No response data from API request.')

        rdata = resp.json()
        status = rdata.get('status', '')
        if status == 'success':
            return (True, rdata['message'])
        elif status == 'error':
            return (False, rdata['message'])
        return (False, 'Unexpected response from API server received.')


Class = PbinAdmin
