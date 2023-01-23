// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

import java.util.Arrays;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import net.jpountz.lz4.LZ4Compressor;
import net.jpountz.lz4.LZ4Factory;
import net.jpountz.lz4.LZ4FastDecompressor;

public class CompressionUtil {
  private static final CompressionUtil INSTANCE = new CompressionUtil();
  private final ObjectMapper mapper = new ObjectMapper();
  private final LZ4Factory factory = LZ4Factory.fastestInstance();
  private final byte LZ4_FAST_COMPRESSION = 1;

  public static CompressionUtil getInstance() {
    return INSTANCE;
  }

  private byte[] compress(byte[] input) {
    LZ4Compressor compressor = factory.fastCompressor();
    byte[] buffer = new byte[compressor.maxCompressedLength(input.length) + 5];
    int len = compressor.compress(input, 0, input.length, buffer, 5, buffer.length - 5);
    ByteBuffer bb = ByteBuffer.wrap(buffer);
    bb.order(ByteOrder.BIG_ENDIAN);
    bb.put(LZ4_FAST_COMPRESSION);
    bb.putInt(input.length);
    return Arrays.copyOf(buffer, len + bb.position());
  }

  private byte[] decompress(byte[] input) {
    ByteBuffer bb = ByteBuffer.wrap(input);
    bb.order(ByteOrder.BIG_ENDIAN);
    if (bb.get() != LZ4_FAST_COMPRESSION) {
      throw new RuntimeException("Unsupported compression method.");
    }
    int len = bb.getInt();
    LZ4FastDecompressor decompressor = factory.fastDecompressor();
    return decompressor.decompress(input, bb.position(), len);
  }

  public <T> T getValue(byte[] compressed, Class<T> clazz) {
    if (compressed == null) {
      return null;
    }
    try {
      return mapper.readValue(decompress(compressed), clazz);
    } catch (IOException e) {
      throw new RuntimeException("Unexpected exception while deserializing.", e);
    }
  }

  public <T extends JsonNode> byte[] compressValue(T val) {
    try {
      return compress(mapper.writeValueAsBytes(val));
    } catch (JsonProcessingException e) {
      throw new RuntimeException("Unexpected exception while serializing.", e);
    }
  }
}
