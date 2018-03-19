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


def capab(prefix):
    if world.testing:
        # we're running a testcase, always return True
        return True
    # Check capability #
    try:
        user = ircdb.users.getUser(prefix)
    except KeyError:
        return False
    if 'pbinadmin' in list(user.capabilities):
        return True
    elif 'admin' in list(user.capabilities):
        return True
    return False


class PbinAdmin(callbacks.Plugin):
    '''Provide administrative control over wiki to authorized users.'''
    threaded = True
    def __init__(self, irc):
        self.__parent = super(PbinAdmin, self)
        self.__parent.__init__(irc)

    def whitelist(self, irc, msg, args, channel, address):
        '''[<channel>] <address>

        Add a registered subnet to whitelist for specified IP address.'''
        return self._cmd_wrapper(irc, msg, args, address, 'wl')

    def greylist(self, irc, msg, args, channel, paste_id):
        '''[<channel>] <paste_id>

        Add address for specified paste to grey list.'''
        return self._cmd_wrapper(irc, msg, args, paste_id, 'gl')

    def blacklist(self, irc, msg, args, channel, paste_id):
        '''[<channel>] <paste_id>

        Add address for specified paste to black list.'''
        return self._cmd_wrapper(irc, msg, args, paste_id, 'bl')

    def delete(self, irc, msg, args, channel, paste_id):
        '''[<channel>] <paste_id>

        Delete a paste with specified ID.'''
        return self._cmd_wrapper(irc, msg, args, paste_id, 'del')

    def _cmd_wrapper(self, irc, msg, args, tgt, cmd):
        '''A simple wrapper to eliminate repetition.'''
        if not self.registryValue('enabled', msg.args[0]):
            return
        if not capab(msg.prefix):
            return
        if ' ' in tgt:
            return
        (success, message) =  self._run_cmd(msg, cmd, tgt)
        irc.reply(message)

    def _run_cmd(self, msg, command, target):
        try:
            resp = requests.post(
                self.registryValue('api_host', msg.args[0]),
                json = {
                    'token': self.registryValue('api_token', msg.args[0]),
                    'command': command,
                    'target': target},
                headers = {'Content-type': 'application/json'})
        except:
            return (False, 'Error during API request.')
        if not resp:
            return (False, 'No response data from API request.')
        if resp.status_code != 200:
            return (False, 'Unexpected status code received: {}'.format(resp.status_code))

        rdata = resp.json()
        if not rdata:
            return (False, 'No data decoded.')
        status = rdata.get('status', '')

        if status == 'success':
            return (True, rdata['message'])
        elif status == 'error':
            return (False, rdata['message'])
        return (False, 'Unexpected status in server response.')

    whitelist = wrap(whitelist, [optional('channel'), 'text'])
    greylist = wrap(greylist, [optional('channel'), 'text'])
    blacklist = wrap(blacklist, [optional('channel'), 'text'])
    delete = wrap(delete, [optional('channel'), 'text'])


Class = PbinAdmin
