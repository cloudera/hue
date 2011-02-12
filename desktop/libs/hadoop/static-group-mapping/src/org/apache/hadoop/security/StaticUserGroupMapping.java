/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.hadoop.security;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Map.Entry;
import java.util.concurrent.ConcurrentHashMap;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.util.StringUtils;

/**
 * Implements getGroups() of the GroupMappingServiceProvider interface by
 * parsing a static, .properties-style file of the form:
 *
 * <code>username = comma,separated,list,of,groups</code>
 */
public class StaticUserGroupMapping implements GroupMappingServiceProvider {

  private static final String GROUP_MAPPING_CONF_KEY = "hadoop.security.static.group.mapping.file";
  private static Map<String, List<String>> userGroupMapping = new ConcurrentHashMap<String, List<String>>();

  static {
    Properties properties = new Properties();
    try {
      String groupMappingFile = new Configuration().get(GROUP_MAPPING_CONF_KEY);
      if (groupMappingFile == null) {
        throw new RuntimeException("StaticUserGroupMapping class specified, but no static group " + 
          "mapping file given. Set " + GROUP_MAPPING_CONF_KEY);
      }
      properties.load(new FileInputStream(groupMappingFile));
      for (Entry<Object, Object> user : properties.entrySet()) {
        userGroupMapping.put((String) user.getKey(), Arrays.asList(((String) user.getValue()).split(",")));
      }
    } catch (FileNotFoundException e) {
      throw new RuntimeException(e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public List<String> getGroups(String user) throws IOException {
    return userGroupMapping.get(user);
  }

  @Override
  public void cacheGroupsRefresh() throws IOException {
    // does nothing in this provider of user to groups mapping
  }

  @Override
  public void cacheGroupsAdd(List<String> groups) throws IOException {
    // does nothing in this provider of user to groups mapping
  }

  public static void main(String[] args) {
    for (Entry<String, List<String>> ugi : userGroupMapping.entrySet()) {
      System.out.println(ugi.getKey() + " : " + ugi.getValue().size() + " : "
          + StringUtils.join(StringUtils.COMMA_STR, ugi.getValue()));
    }
  }

}
