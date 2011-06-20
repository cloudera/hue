#!/usr/bin/env thrift -r --gen py:new_style
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

namespace py djangothrift_test_gen

struct TestStruct {
  1: string a,
  2: i32 b
}

struct TestNesting {
  1: TestStruct nested_struct,
  2: i32 b,
}

enum TestEnum {
  ENUM_ONE,
  ENUM_TWO,
  ENUM_THREE
}

struct TestManyTypes {
  1: bool a_bool,
  2: byte a_byte,
  3: i16 a_i16,
  4: i32 a_i32,
  5: i64 a_i64,
  6: double a_double,
  7: string a_string,
  8: binary a_binary,
  9: TestEnum a_enum,
  10: TestStruct a_struct,
  11: set<i32> a_set,
  12: list<TestStruct> a_list,
  13: map<i32, TestStruct> a_map,
  14: string a_string_with_default = "the_default",
  15: list<string> a_string_list
}


service TestService {
  // Multiply the input by 2 and return the result
  i32 ping(1:i32 input);
}
