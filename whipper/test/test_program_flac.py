# -*- Mode: Python; test-case-name: whipper.test.test_program_flac -*-

import os
import shutil
import tempfile
from unittest import mock

from whipper.program import flac
from whipper.test import common


class EncodeArgumentsTestCase(common.TestCase):
    @mock.patch('whipper.program.flac.check_call')
    def testDefaultLevel(self, check_call):
        flac.encode('in.wav', 'out.flac')
        check_call.assert_called_once_with(
            ['flac', '--silent', '--verify', '-o', 'out.flac', '-f',
             'in.wav'])

    @mock.patch('whipper.program.flac.check_call')
    def testLevel(self, check_call):
        flac.encode('in.wav', 'out.flac', level=8)
        check_call.assert_called_once_with(
            ['flac', '--silent', '--verify', '-8', '-o', 'out.flac', '-f',
             'in.wav'])

    @mock.patch('whipper.program.flac.check_call')
    def testLevelZero(self, check_call):
        flac.encode('in.wav', 'out.flac', level=0)
        self.assertIn('-0', check_call.call_args[0][0])


class EncodeTestCase(common.TestCase):
    """Encode a real file at two levels, if flac is installed."""

    def setUp(self):
        if not shutil.which('flac'):
            raise common.unittest.SkipTest('flac not installed')
        self.tmpdir = tempfile.mkdtemp()
        self.wav = os.path.join(self.tmpdir, 'track.wav')
        # decode the test track to WAV first
        flac.check_call(['flac', '--silent', '-d', '-f', '-o', self.wav,
                         os.path.join(os.path.dirname(__file__),
                                      'track.flac')])

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _encode(self, level):
        out = os.path.join(self.tmpdir, 'level%d.flac' % level)
        open(out, 'wb').close()
        flac.encode(self.wav, out, level=level)
        return out

    def testSmallerAtLevel8(self):
        fast = self._encode(0)
        best = self._encode(8)
        self.assertLess(os.path.getsize(best), os.path.getsize(fast))
