// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor;

import java.io.Closeable;
import java.io.EOFException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.HiveHookEventProto;
import org.apache.hadoop.yarn.util.SystemClock;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;
import org.apache.tez.dag.history.logging.proto.ProtoMessageReader;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.io.SerializedString;
import com.google.protobuf.ByteString;
import com.google.protobuf.Descriptors.EnumValueDescriptor;
import com.google.protobuf.Descriptors.FieldDescriptor;
import com.google.protobuf.Message;
import com.google.protobuf.MessageOrBuilder;

import io.dropwizard.cli.Command;
import io.dropwizard.setup.Bootstrap;
import net.sourceforge.argparse4j.inf.Namespace;
import net.sourceforge.argparse4j.inf.Subparser;

public class ProtoJsonConvertor extends Command {

  public ProtoJsonConvertor() {
    super("protodump", "Convert proto files to readable json files.");
  }

  @Override
  public void configure(Subparser subparser) {
    subparser.addArgument("--type", "-t").type(String.class).required(true)
        .help("The proto type: <tez|hive>").choices("tez", "hive");

    subparser.addArgument("--src", "-s").required(true).type(String.class)
        .help("The file to convert to json.");

    subparser.addArgument("--dest", "-d").required(true).type(String.class)
        .help("File to save the json output.");
}

  @Override
  public void run(Bootstrap<?> bootstrap, Namespace namespace) throws Exception {
    String type = namespace.getString("type");
    String srcFile = namespace.getString("src");
    String destFile = namespace.getString("dest");
    try (ProtoMessageReader<? extends MessageOrBuilder> reader = getLoggerForType(type, srcFile);
        JsonFormatter formatter = new JsonFormatter(new FileOutputStream(destFile))) {
      for (MessageOrBuilder evt = reader.readEvent(); evt != null; evt = reader.readEvent()) {
        formatter.printMessage(evt);
      }
    } catch (EOFException e) {
      // All good.
    }
  }

  public ProtoMessageReader<? extends MessageOrBuilder> getLoggerForType(String type,
      String filePath) throws IOException {
    Configuration conf = new Configuration();
    SystemClock clock = SystemClock.getInstance();
    DatePartitionedLogger<? extends MessageOrBuilder> logger;
    if ("tez".equalsIgnoreCase(type)) {
      logger = new DatePartitionedLogger<>(HistoryEventProto.PARSER, new Path("/"), conf, clock);
    } else if ("hive".equalsIgnoreCase(type)) {
      logger = new DatePartitionedLogger<>(HiveHookEventProto.PARSER, new Path("/"), conf, clock);
    } else {
      throw new RuntimeException("Unexpected type : " + type);
    }
    return logger.getReader(new Path(filePath));
  }

  private static final class JsonFormatter implements Closeable {
    private static final JsonFactory jsonFactory = new JsonFactory();
    private final JsonGenerator generator;

    private JsonFormatter(OutputStream out) throws IOException {
      generator = jsonFactory.createGenerator(out);
      generator.setRootValueSeparator(new SerializedString("\n"));
    }

    @Override
    public void close() throws IOException {
      generator.close();
    }

    public void printMessage(MessageOrBuilder message) throws IOException {
      generator.writeStartObject();
      for (Map.Entry<FieldDescriptor, Object> field : message.getAllFields().entrySet()) {
        printField(field.getKey(), field.getValue());
      }
      generator.writeEndObject();
      // message.getUnknownFields() ignored, since we cannot do much about it.
    }

    private void printField(FieldDescriptor field, Object value) throws IOException {
      generator.writeFieldName(field.getName());
      if (field.isRepeated()) {
        generator.writeStartArray();
        for (Object element : (List<?>) value) {
          printFieldValue(field, element);
        }
        generator.writeEndArray();
      } else {
        printFieldValue(field, value);
      }
    }

    private void printFieldValue(FieldDescriptor field, Object value) throws IOException {
      switch (field.getJavaType()) {
        case INT:
          generator.writeNumber((Integer) value);
          break;
        case LONG:
          generator.writeNumber((Long) value);
          break;
        case BOOLEAN:
          generator.writeBoolean((Boolean) value);
          break;
        case FLOAT:
          generator.writeNumber((Float) value);
          break;
        case DOUBLE:
          generator.writeNumber((Double) value);
          break;
        case STRING:
          generator.writeString((String) value);
          break;
        case BYTE_STRING:
          ByteString byteString = ((ByteString) value);
          byte[] bytes = new byte[byteString.size()];
          byteString.copyTo(bytes, 0);
          generator.writeBinary(bytes);
          break;
        case ENUM:
          generator.writeString(((EnumValueDescriptor) value).getName());
          break;
        case MESSAGE:
          printMessage((Message) value);
          break;
      }
    }
  }
}
