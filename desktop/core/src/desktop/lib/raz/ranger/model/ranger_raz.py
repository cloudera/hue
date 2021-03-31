#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from apache_ranger.model.ranger_base import *
from apache_ranger.utils import *


class RangerRazRequestBase(RangerBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerBase.__init__(self, attrs)

    self.requestId = attrs.get("requestId")
    self.serviceType = attrs.get("serviceType")
    self.serviceName = attrs.get("serviceName")
    self.user = attrs.get("user")
    self.userGroups = attrs.get("userGroups")
    self.accessTime = attrs.get("accessTime")
    self.clientIpAddress = attrs.get("clientIpAddress")
    self.clientType = attrs.get("clientType")
    self.clusterName = attrs.get("clusterName")
    self.clusterType = attrs.get("clusterType")
    self.sessionId = attrs.get("sessionId")
    self.context = attrs.get("context")

  def type_coerce_attrs(self):
    super(RangerRazRequestBase, self).type_coerce_attrs()


class ResourceAccess(RangerBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerBase.__init__(self, attrs)

    self.resource = attrs.get("resource")
    self.resourceOwner = attrs.get("resourceOwner")
    self.action = attrs.get("action")
    self.accessTypes = attrs.get("accessTypes")

  def type_coerce_attrs(self):
    super(ResourceAccess, self).type_coerce_attrs()


class RangerRazRequest(RangerRazRequestBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerRazRequestBase.__init__(self, attrs)

    self.operation = attrs.get("operation")

  def type_coerce_attrs(self):
    super(RangerRazRequest, self).type_coerce_attrs()

    self.operation = type_coerce(self.operation, ResourceAccess)


class RangerRazMultiOperationRequest(RangerRazRequestBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerRazRequestBase.__init__(self, attrs)

    self.operations = attrs.get("operations")

  def type_coerce_attrs(self):
    super(RangerRazMultiOperationRequest, self).type_coerce_attrs()

    self.operation = type_coerce_list(self.operation, ResourceAccess)


class RangerRazResultBase(RangerBase):
  ALLOWED = 0
  DENIED = 1
  NOT_DETERMINED = 2

  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerBase.__init__(self, attrs)

    self.requestId = attrs.get("requestId")

  def type_coerce_attrs(self):
    super(RangerRazResultBase, self).type_coerce_attrs()


class AuditInfo(RangerBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerBase.__init__(self, attrs)

    self.auditId = attrs.get("auditId")
    self.accessType = attrs.get("accessType")
    self.result = attrs.get("result")
    self.policyId = attrs.get("policyId")
    self.policyVersion = attrs.get("policyVersion")

  def type_coerce_attrs(self):
    super(AuditInfo, self).type_coerce_attrs()


class ResourceAccessResult(RangerBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerBase.__init__(self, attrs)

    self.result = attrs.get("result")
    self.isAudited = attrs.get("isAudited")
    self.auditLogs = attrs.get("auditLogs")
    self.additionalInfo = attrs.get("additionalInfo")

  def type_coerce_attrs(self):
    super(ResourceAccessResult, self).type_coerce_attrs()

    self.auditLogs = type_coerce_list(self.operation, AuditInfo)


class RangerRazResult(RangerRazResultBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerRazResultBase.__init__(self, attrs)

    self.operResult = attrs.get("operResult")

  def type_coerce_attrs(self):
    super(RangerRazResult, self).type_coerce_attrs()

    self.operResult = type_coerce(self.operResult, ResourceAccessResult)


class RangerRazMultiOperationResult(RangerRazResultBase):
  def __init__(self, attrs=None):
    attrs = attrs or {}

    RangerRazRequestBase.__init__(self, attrs)

    self.operResults = attrs.get("operResults")

  def type_coerce_attrs(self):
    super(RangerRazMultiOperationResult, self).type_coerce_attrs()

    self.operResults = type_coerce_list(self.operResults, ResourceAccessResult)
