import unittest

from stash.api import app


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        pass
