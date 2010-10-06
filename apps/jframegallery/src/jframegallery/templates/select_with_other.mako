## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title>Select With Other</title>
  </head>
  <body>
    <div class="jframe_padded">
      <div data-filters="SelectWithOther">
        <select>
        <option>A</option>
        <option>B</option>
        <option value="__other__">Other</option>
        </select>
        <input name="other" class="ccs-hidden"  data-filters="OverText" alt="Enter a custom value">
      </div>
      <hr/>
      <div data-filters="SelectWithOther" data-other-input=".otherContainer" data-other-options="option[value=null]">
        <select>
        <option>A</option>
        <option>B</option>
        <option value="null">Other</option>
        </select>
        <div class="otherContainer ccs-hidden">
          <input name="other" data-filters="OverText" alt="Enter a custom value">
        <div>
      </div>
    </div>
  </body>
</html>
