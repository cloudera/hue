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

DJANGO_APPS = [ "useradmin" ]
NICE_NAME = "User Admin"
REQUIRES_HADOOP = False
ICON = "useradmin/art/icon_useradmin_48.png"
MENU_INDEX = 60

PERMISSION_ACTIONS = (
  ("access_view:useradmin:edit_user", "Access to profile page on User Admin"),
  ("superuser", "Give superuser access to members of group")
)
