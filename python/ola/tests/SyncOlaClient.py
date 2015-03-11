from ola import OlaClient
from ola import ClientWrapper
from threading import Semaphore
from ola.OlaClient import Plugin, RequestStatus


class OlaCallError(Exception):

    def __init__(self, status):
        super(OlaCallError, self).__init__(status.message)


class SyncOlaClient:
    """Wraps an OlaClient to be able to make synchronous calls."""

    def __init__(self):
        self._wrapper = ClientWrapper.ClientWrapper()
        self._sem = Semaphore()
        self._retval = None

    def _cb(self, *args):
        self._retval = args
        self._wrapper.Stop()

    def _wait_for_answer(self):
        self._wrapper.Run()

        requeststatus = self._retval[0]
        self._retval = self._retval[1:]

        if requeststatus.state != RequestStatus.SUCCESS:
            raise OlaCallError(requeststatus)

        if len(self._retval) == 0:
            self._retval = None
        if len(self._retval) == 1:
            self._retval = self._retval[0]

    def PatchPort(self, device_alias, port, is_output, action, universe):
        self._wrapper.Client().PatchPort(
            device_alias, port, is_output, action, universe, self._cb)
        self._wait_for_answer()
        return self._retval

    def FetchUniverses(self):
        self._wrapper.Client().FetchUniverses(self._cb)
        self._wait_for_answer()
        return self._retval

    def FetchDevices(self, plugin_filter=Plugin.OLA_PLUGIN_ALL):
        self._wrapper.Client().FetchDevices(self._cb, plugin_filter)
        self._wait_for_answer()
        return self._retval

    def PluginDescription(self, plugin_id):
        self._wrapper.Client().PluginDescription(self._cb, plugin_id)
        self._wait_for_answer()
        return self._retval

    def FetchPlugins(self):
        self._wrapper.Client().FetchPlugins(self._cb)
        self._wait_for_answer()
        return self._retval

if __name__ == '__main__':
    # Sample usage
    c = SyncOlaClient()
    ret = c.FetchDevices()
    for dev in ret:
        print(dev.name)
