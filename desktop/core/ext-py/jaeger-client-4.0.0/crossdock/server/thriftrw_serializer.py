# Copyright (c) 2016 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def trace_response_to_thriftrw(service, tr):
    if tr is None:
        return None
    return service.TraceResponse(span=observed_span_to_thriftrw(service, tr.span),
                                 downstream=trace_response_to_thriftrw(service, tr.downstream),
                                 notImplementedError=tr.notImplementedError or '')


def downstream_to_thriftrw(service, downstream):
    if downstream is None:
        return None
    return service.Downstream(downstream.serviceName,
                              downstream.serverRole,
                              downstream.host,
                              downstream.port,
                              downstream.transport,
                              downstream.downstream)


def join_trace_request_to_thriftrw(service, jtr):
    return service.JoinTraceRequest(jtr.serverRole, downstream_to_thriftrw(service, jtr.downstream))


def observed_span_to_thriftrw(service, observed_span):
    return service.ObservedSpan(traceId=observed_span.traceId,
                                sampled=observed_span.sampled,
                                baggage=observed_span.baggage)
