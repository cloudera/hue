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
		<title>FitText (table)</title>
	</head>
	<body>
	<h1 class="ccs-hidden">FitText (table)</h1>
	
	<table cellpadding="0" cellspacing="0">
		<thead>
			<tr>
				<th>
							ID
				</th>
				<th>
							TimeZone
				</th>
				<th>
							Name
				</th>
				<th>
							GEO Latitude
				</th>
				<th>
							GEO Longitude
				</th>
			</tr>
		</thead>
		<tbody>
			% for i in range(10000):
				<tr>
					<td>
						${i}
					</td>
					<td>
						New York City
					</td>
					<td>
						America/New_York
						America/New_York
						America/New_York
						America/New_York
					</td>
					<td>
						40.7255
					</td>
					<td>
						-73.9983
					</td>
				</tr>
			% endfor
		</tbody>
	</table>
	
	</body>
</html>
