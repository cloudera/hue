// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

namespace py RuntimeProfile

include "Metrics.thrift"

// Counter data
struct TCounter {
  1: required string name
  2: required Metrics.TUnit unit
  3: required i64 value
}

// Thrift version of RuntimeProfile::EventSequence - list of (label, timestamp) pairs
// which represent an ordered sequence of events.
struct TEventSequence {
  1: required string name
  2: required list<i64> timestamps
  3: required list<string> labels
}

// Struct to contain data sampled at even time intervals (e.g. ram usage every
// N seconds).
// values[0] represents the value when the counter stated (e.g. fragment started)
// values[1] is the value at period_ms (e.g. 500 ms later)
// values[2] is the value at 2 * period_ms (e.g. 1sec since start)
// This can be used to reconstruct a time line for a particular counter.
struct TTimeSeriesCounter {
  1: required string name
  2: required Metrics.TUnit unit

  // Period of intervals in ms
  3: required i32 period_ms

  // The sampled values.
  4: required list<i64> values
}

// Thrift version of RuntimeProfile::SummaryStatsCounter.
struct TSummaryStatsCounter {
  1: required string name
  2: required Metrics.TUnit unit
  3: required i64 sum
  4: required i64 total_num_values
  5: required i64 min_value
  6: required i64 max_value
}

// A single runtime profile
struct TRuntimeProfileNode {
  1: required string name
  2: required i32 num_children
  3: required list<TCounter> counters
  // TODO: should we make metadata a serializable struct?  We only use it to
  // store the node id right now so this is sufficient.
  4: required i64 metadata

  // indicates whether the child will be printed with extra indentation;
  // corresponds to indent param of RuntimeProfile::AddChild()
  5: required bool indent

  // map of key,value info strings that capture any kind of additional information
  // about the profiled object
  6: required map<string, string> info_strings

  // Auxilliary structure to capture the info strings display order when printed
  7: required list<string> info_strings_display_order

  // map from parent counter name to child counter name
  8: required map<string, set<string>> child_counters_map

  // List of event sequences that capture ordered events in a query's lifetime
  9: optional list<TEventSequence> event_sequences

  // List of time series counters
  10: optional list<TTimeSeriesCounter> time_series_counters

  // List of summary stats counters
  11: optional list<TSummaryStatsCounter> summary_stats_counters
}

// A flattened tree of runtime profiles, obtained by an
// pre-order traversal
struct TRuntimeProfileTree {
  1: required list<TRuntimeProfileNode> nodes
}
