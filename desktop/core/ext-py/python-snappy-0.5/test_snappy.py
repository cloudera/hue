#!/usr/bin/env python
#
# Copyright (c) 2011, Andres Moreira <andres@andresmoreira.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the authors nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ANDRES MOREIRA BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys
import random
import snappy
import struct
from unittest import TestCase


class SnappyCompressionTest(TestCase):

    def test_simple_compress(self):
        text = "hello world!".encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.uncompress(compressed))

    def test_moredata_compress(self):
        text = "snappy +" * 1000 + " " + "by " * 1000 + " google"
        text = text.encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.uncompress(compressed))

    def test_randombytes_compress(self):
        _bytes = repr(os.urandom(1000)).encode('utf-8')
        compressed = snappy.compress(_bytes)
        self.assertEqual(_bytes, snappy.uncompress(compressed))

    def test_randombytes2_compress(self):
        _bytes = bytes(os.urandom(10000))
        compressed = snappy.compress(_bytes)
        self.assertEqual(_bytes, snappy.uncompress(compressed))

    def test_uncompress_error(self):
        self.assertRaises(snappy.UncompressError, snappy.uncompress,
                          "hoa".encode('utf-8'))

    if sys.version_info[0] == 2:
        def test_unicode_compress(self):
            text = "hello unicode world!".decode('utf-8')
            compressed = snappy.compress(text)
            self.assertEqual(text, snappy.uncompress(compressed))

    def test_decompress(self):
        # decompress == uncompress, just to support compatibility with zlib
        text = "hello world!".encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.decompress(compressed))

    def test_big_string(self):
        text = ('a'*10000000).encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.decompress(compressed))


class SnappyValidBufferTest(TestCase):

    def test_valid_compressed_buffer(self):
        text = "hello world!".encode('utf-8')
        compressed = snappy.compress(text)
        uncompressed = snappy.uncompress(compressed)
        self.assertEqual(text == uncompressed,
                         snappy.isValidCompressed(compressed))

    def test_invalid_compressed_buffer(self):
        self.assertFalse(snappy.isValidCompressed(
                "not compressed".encode('utf-8')))


class SnappyStreaming(TestCase):

    def test_random(self):
        for _ in range(100):
            compressor = snappy.StreamCompressor()
            decompressor = snappy.StreamDecompressor()
            data = b""
            compressed = b""
            for _ in range(random.randint(0, 3)):
                chunk = os.urandom(random.randint(0, snappy._CHUNK_MAX * 2))
                data += chunk
                compressed += compressor.add_chunk(
                        chunk, compress=random.choice([True, False, None]))

            upper_bound = random.choice([256, snappy._CHUNK_MAX * 2])
            while compressed:
                size = random.randint(0, upper_bound)
                chunk, compressed = compressed[:size], compressed[size:]
                chunk = decompressor.decompress(chunk)
                self.assertEqual(data[:len(chunk)], chunk)
                data = data[len(chunk):]

            decompressor.flush()
            self.assertEqual(len(data), 0)

    def test_compression(self):
        # test that we can add compressed chunks
        compressor = snappy.StreamCompressor()
        data = b"\0" * 50
        compressed_data = snappy.compress(data)
        crc = struct.pack("<L", snappy._masked_crc32c(data))
        self.assertEqual(crc, b"\x8f)H\xbd")
        self.assertEqual(len(compressed_data), 6)
        self.assertEqual(compressor.add_chunk(data, compress=True),
                         b"\xff\x06\x00\x00sNaPpY"
                         b"\x00\x0a\x00\x00" + crc + compressed_data)

        # test that we can add uncompressed chunks
        data = b"\x01" * 50
        crc = struct.pack("<L", snappy._masked_crc32c(data))
        self.assertEqual(crc, b"\xb2\x14)\x8a")
        self.assertEqual(compressor.add_chunk(data, compress=False),
                         b"\x01\x36\x00\x00" + crc + data)

        # test that we can add more data than will fit in one chunk
        data = b"\x01" * (snappy._CHUNK_MAX * 2 - 5)
        crc1 = struct.pack("<L",
                snappy._masked_crc32c(data[:snappy._CHUNK_MAX]))
        self.assertEqual(crc1, b"h#6\x8e")
        crc2 = struct.pack("<L",
                snappy._masked_crc32c(data[snappy._CHUNK_MAX:]))
        self.assertEqual(crc2, b"q\x8foE")
        self.assertEqual(compressor.add_chunk(data, compress=False),
                b"\x01\x04\x00\x01" + crc1 + data[:snappy._CHUNK_MAX] +
                b"\x01\xff\xff\x00" + crc2 + data[snappy._CHUNK_MAX:])

    def test_decompression(self):
        # test that we check for the initial stream identifier
        data = b"\x01" * 50
        self.assertRaises(snappy.UncompressError,
                snappy.StreamDecompressor().decompress,
                    b"\x01\x36\x00\00" +
                    struct.pack("<L", snappy._masked_crc32c(data)) + data)
        self.assertEqual(
                snappy.StreamDecompressor().decompress(
                    b"\xff\x06\x00\x00sNaPpY"
                    b"\x01\x36\x00\x00" +
                    struct.pack("<L", snappy._masked_crc32c(data)) + data),
                data)
        decompressor = snappy.StreamDecompressor()
        decompressor.decompress(b"\xff\x06\x00\x00sNaPpY")
        self.assertEqual(
                decompressor.copy().decompress(
                    b"\x01\x36\x00\x00" +
                    struct.pack("<L", snappy._masked_crc32c(data)) + data),
                data)

        # test that we throw errors for unknown unskippable chunks
        self.assertRaises(snappy.UncompressError,
                decompressor.copy().decompress, b"\x03\x01\x00\x00")

        # test that we skip unknown skippable chunks
        self.assertEqual(b"",
                         decompressor.copy().decompress(b"\xfe\x01\x00\x00"))

        # test that we check CRCs
        compressed_data = snappy.compress(data)
        real_crc = struct.pack("<L", snappy._masked_crc32c(data))
        fake_crc = os.urandom(4)
        self.assertRaises(snappy.UncompressError,
                decompressor.copy().decompress,
                    b"\x00\x0a\x00\x00" + fake_crc + compressed_data)
        self.assertEqual(
                decompressor.copy().decompress(
                    b"\x00\x0a\x00\x00" + real_crc + compressed_data),
                data)

        # test that we buffer when we don't have enough
        uncompressed_data = os.urandom(100)
        compressor = snappy.StreamCompressor()
        compressed_data = (compressor.compress(uncompressed_data[:50]) +
                           compressor.compress(uncompressed_data[50:]))
        for split1 in range(len(compressed_data) - 1):
            for split2 in range(split1, len(compressed_data)):
                decompressor = snappy.StreamDecompressor()
                self.assertEqual(
                    (decompressor.decompress(compressed_data[:split1]) +
                     decompressor.decompress(compressed_data[split1:split2]) +
                     decompressor.decompress(compressed_data[split2:])),
                    uncompressed_data)

    def test_concatenation(self):
        data1 = os.urandom(snappy._CHUNK_MAX * 2)
        data2 = os.urandom(4096)
        decompressor = snappy.StreamDecompressor()
        self.assertEqual(
                decompressor.decompress(
                    snappy.StreamCompressor().compress(data1) +
                    snappy.StreamCompressor().compress(data2)),
                data1 + data2)


if __name__ == "__main__":
    import unittest
    unittest.main()
