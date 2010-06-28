// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
package com.cloudera.beeswax;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.Text;
import org.xml.sax.SAXException;

/**
 * Singleton that looks up Hadoop and Hive configuration descriptions.
 */
public class ConfigDescriptions {
  private static Logger LOG = Logger.getLogger(Server.class.getName());

  public static ConfigDescriptions get() {
    return INSTANCE;
  }

  private final static List<String> RESOURCES_TO_LOAD = new ArrayList<String>();
  static {
    // Configuration's "default resources" aren't public, so we
    // just use well-known values.
    RESOURCES_TO_LOAD.add("core-default.xml");
    RESOURCES_TO_LOAD.add("hdfs-default.xml");
    RESOURCES_TO_LOAD.add("mapred-default.xml");
    RESOURCES_TO_LOAD.add("hive-default.xml");
  }

  private static DocumentBuilder DOCUMENT_BUILDER = createDocumentBuilder();

  /** Creates appropriate Java XML document builder. */
  private static DocumentBuilder createDocumentBuilder() {
    DocumentBuilderFactory docBuilderFactory = DocumentBuilderFactory.newInstance();
    docBuilderFactory.setIgnoringComments(true);
    docBuilderFactory.setNamespaceAware(true);
    try {
      docBuilderFactory.setXIncludeAware(true);
    } catch (UnsupportedOperationException e) {
      LOG.error("Failed to set setXIncludeAware(true) for parser "
            + docBuilderFactory
            + ":" + e,
            e);
    }
    try {
      return docBuilderFactory.newDocumentBuilder();
    } catch (ParserConfigurationException e) {
      throw new RuntimeException(e);
    }
  }

  private static final ConfigDescriptions INSTANCE = new ConfigDescriptions();

  private Map<String, String> descriptionMap = new HashMap<String, String>();

  private ConfigDescriptions() {
    for (String resourceName : RESOURCES_TO_LOAD) {
      try {
        InputStream is = Thread.currentThread()
          .getContextClassLoader().getResourceAsStream(resourceName);
        int n = parseSingleStream(is);
        LOG.info("Parsed " + resourceName + " sucessfully.  Learned " + n
            + " descriptions.");
      } catch (Exception e) {
        LOG.warn("Could not parse or find: " + resourceName, e);
      }
    }

  }

  /**
   * This is lovingly and partially plagiarized from Hadooop's Configuration.loadResource().
   *
   * @return Number of descriptions learned.
   */
  private int parseSingleStream(InputStream is) throws SAXException, IOException {
    Document doc = DOCUMENT_BUILDER.parse(is);
    Element root = doc.getDocumentElement();
    if (!"configuration".equals(root.getTagName())) {
      LOG.warn("Failed to parse configuration from: " + is);
      return 0;
    }
    return parseConfigurationElement(root);
  }

  private int parseConfigurationElement(Node root) {
    int cnt = 0;
    NodeList children = root.getChildNodes();
    for (int i = 0; i < children.getLength(); ++i) {
      Node child = children.item(i);
      if (child.getNodeName().equals("configuration")) {
        // Sometimes the XML structure looks
        // recursive here.
        cnt += parseConfigurationElement(child);
        continue;
      }
      NodeList fields = children.item(i).getChildNodes();
      String key = null;
      String description = null;

      for (int j = 0; j < fields.getLength(); ++j) {
        Node fieldNode = fields.item(j);
        if (!(fieldNode instanceof Element))
          continue;
        Element field = (Element) fieldNode;
        if ("name".equals(field.getTagName()) && field.hasChildNodes()) {
          key = ((Text)field.getFirstChild()).getData().trim();
        }
        if ("description".equals(field.getTagName())  && field.hasChildNodes()) {
          description = ((Text)field.getFirstChild()).getData().trim();
        }
      }
      if (key != null && description != null) {
        descriptionMap.put(key, description);
        cnt++;
      }
    }
    return cnt;
  }

  /** Retrieve configuration description for a key. */
  public String lookup(String key) {
    return descriptionMap.get(key);
  }
}
