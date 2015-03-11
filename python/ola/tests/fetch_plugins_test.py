import unittest
from ola.tests import base

class FetchPluginsTest(base.BaseTestCase):

    def testFetch1(self):
        print(self.client.FetchPlugins())