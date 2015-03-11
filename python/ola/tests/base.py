import unittest
import subprocess
import tempfile
import sys
import os
import socket
import errno
import shutil
import time

from ola.tests.SyncOlaClient import SyncOlaClient

# The tests should be ran while in the root OLA directory.

OLAD_INSTALL_ROOT = '/home/simark/src/gridss/ola/install'
OLAD_PATH = os.path.join(OLAD_INSTALL_ROOT, 'bin/olad')
OLAD_PID_LOCATION = os.path.join(OLAD_INSTALL_ROOT, 'share/ola/pids')
OLAD_RPC_PORT = 9010
OLAD_RPC_ADDRESS = '127.0.0.1'


class BaseTestCase(unittest.TestCase):

  def setUp(self):
    try:
      self._start_olad()
      self._wait_for_olad_ready()
      self._client = SyncOlaClient()
    except Exception as e:
      self.tearDown()
      raise e

  def _wait_for_olad_ready(self):
    """Wait until a connection to olad is possible.

    Note that if there is already an olad process running, we will connect
    to that one return immediately."""

    retry = 0
    retry_delay = .05  # seconds
    timeout = 2  # seconds
    max_retries = int(timeout / retry_delay)

    while retry < max_retries:
      try:
        # Fail if we couldn't connect after 2 seconds.
        sock = socket.create_connection((OLAD_RPC_ADDRESS, OLAD_RPC_PORT))
        sock.close()
        return
      except socket.error as e:
        if e.errno != errno.ECONNREFUSED:
          raise e

        retry += 1
        time.sleep(retry_delay)

    raise Exception('Test timed out waiting for olad.')

  def tearDown(self):
    self._close_olad()

  def _start_olad(self):
    self._olad_config_dir = tempfile.mkdtemp(suffix='-ola-python-test')
    self._olad_stdout = open(
        os.path.join(self._olad_config_dir, 'stdout.txt'), 'w')

    print('Config dir is {}'.format(self._olad_config_dir))

    olad_command = [
        OLAD_PATH,
        '--no-http',
        '--config-dir', self._olad_config_dir,
        '--no-register-with-dns-sd',
        '--pid-location', OLAD_PID_LOCATION,
    ]

    print('Starting olad with: {}'.format(' '.join(olad_command)))

    self._olad_popen = subprocess.Popen(
        olad_command, stdout=self._olad_stdout, stderr=subprocess.STDOUT)

  def _close_olad(self):
    if hasattr(self, '_olad_popen'):
      self._olad_popen.terminate()

    if hasattr(self, '_olad_stdout'):
      self._olad_stdout.close()

    # if hasattr(self, '_olad_config_dir'):
    #    shutil.rmtree(self._olad_config_dir)

  @property
  def client(self):
    return self._client

  def testEmpty(self):
    # Tests that setUp and tearDown work fine.
    pass
