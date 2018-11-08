#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re


def pre_order_graph(node, nodes, edges, parent):
    match = re.search("(.*?)\s\(id=(\d+)\)", node.val.name)
    if match:
        node_id = "node_%s" % match.group(2)
        if parent:
            edges.append([node_id, parent])
        nodes[node_id] = {
            "name": match.group(1)
        }
        for c in node.children:
            pre_order_graph(c, nodes, edges, "node_%s" % (match.group(2), ))


def graph_to_json(fragments):
    """Parse the list of fragements to build the graph"""
    # get all nodes of the fragement
    nodes = {}
    edges = []
    for f in fragments:
        parent = None
        for c in f.children:
            dst = re.search("dst_id=(\d+)", c.val.name)
            if dst:
                parent = "node_%s" % (dst.group(1))
            pre_order_graph(c, nodes, edges, parent)

    return {"nodes": nodes, "edges": edges}
