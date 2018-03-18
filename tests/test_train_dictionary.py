import sys
import unittest

import zstandard as zstd

from . common import (
    make_cffi,
)

if sys.version_info[0] >= 3:
    int_type = int
else:
    int_type = long


def generate_samples():
    samples = []
    for i in range(128):
        samples.append(b'foo' * 64)
        samples.append(b'bar' * 64)
        samples.append(b'foobar' * 64)
        samples.append(b'baz' * 64)
        samples.append(b'foobaz' * 64)
        samples.append(b'bazfoo' * 64)
    return samples


@make_cffi
class TestTrainDictionary(unittest.TestCase):
    def test_no_args(self):
        with self.assertRaises(TypeError):
            zstd.train_dictionary()

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            zstd.train_dictionary(8192, u'foo')

        with self.assertRaises(ValueError):
            zstd.train_dictionary(8192, [u'foo'])

    def test_no_params(self):
        samples = []
        for i in range(128):
            samples.append(b'foobarbaz' * 16)
            samples.append(b'blehbleh' * 16)
            samples.append(b'randomtext' * 16)

        d = zstd.train_dictionary(8192, samples)
        self.assertIsInstance(d.dict_id(), int_type)

        data = d.as_bytes()
        self.assertEqual(data[0:8], b'\x37\xa4\x30\xec\xe3\x9f\x99\x7a')

    def test_basic(self):
        samples = []
        for i in range(128):
            samples.append(b'foo' * 64)
            samples.append(b'foobar' * 64)

        d = zstd.train_dictionary(8192, samples, k=64, d=16)
        self.assertIsInstance(d.dict_id(), int_type)

        data = d.as_bytes()
        self.assertEqual(data[0:4], b'\x37\xa4\x30\xec')

        self.assertEqual(d.k, 64)
        self.assertEqual(d.d, 16)

    def test_set_dict_id(self):
        samples = []
        for i in range(128):
            samples.append(b'foo' * 64)
            samples.append(b'foobar' * 64)

        d = zstd.train_dictionary(8192, samples, k=64, d=16, dict_id=42)
        self.assertEqual(d.dict_id(), 42)

    def test_optimize(self):
        samples = []
        for i in range(128):
            samples.append(b'foo' * 64)
            samples.append(b'foobar' * 64)

        d = zstd.train_dictionary(8192, samples, threads=-1, steps=1, d=16)

        self.assertEqual(d.k, 50)
        self.assertEqual(d.d, 16)
