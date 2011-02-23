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
<!DOCTYPE html>
<html>
  <head>
    <title>JFrame Gallery Source -- ${name}</title>
    </head>
    <body>
      <div class="jf-src_view view" id="source" data-filters="SizeTo" data-size-to-height="0">
        <div data-filters="Tabs, SizeTo" data-size-to-height="0" data-tabs-selector=".tab" data-sections-selector=".section">
          <div data-filters="SplitView">
            <div class="left_col">
              <ul class="jframe_padded">
                <li class="tab html-tab"><a>HTML/Template</a></li>
                %for js_name in js_data.iterkeys():
                  <li class="tab">
                    <a>${js_name}</a>
                  </li>
                %endfor
              </ul>
            </div>
            <div class="right_col">
              <ul class="jframe-clear jframe_padded">
                ## Template data
                <li class="section">
                  <h3>Source for HTML</h3>
                  <hr/>
                  ${data|n}
                </li>
                ## JS data
                %for js_name, js in js_data.iteritems():
                  <li class="section">
                    <h3>Source for <code>${js_name}</code></h3>
                    <hr/>
                    ${js|n}
                  </li>
                %endfor
              </ul>
            </div>
          </div>
        </div>
      </div>
    </body>
</html>
