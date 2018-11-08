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
import copy
import glob
import json
import os
import re
import types
import struct

from dateutil.parser import parse as dtparse
from itertools import groupby

from libanalyze.utils import Timer

from libanalyze import models
from libanalyze import exprs
from libanalyze import utils

def to_double(metric_value):
    return struct.unpack('d', struct.pack('q', metric_value))[0]

class ProfileContext:
    """This is the main wrapper around the runtime profile tree. Main accessor
    methods are implemented here."""

    def __init__(self, profile):
        self.profile = profile

    def query_duration(self):
        node = self.profile.find_by_name("Summary")
        return (dtparse(node.info_strings["End Time"]) -
                dtparse(node.info_strings["Start Time"])).total_seconds()

    def percentage_of_total(self, compare):
        return compare / self.query_duration()


class SQLOperatorReason:
    def __init__(self, node_name, metric_names,
                 rule, exprs=[], to_json=True, **kwargs):
        self.node_name = node_name
        if isinstance(metric_names, types.StringTypes):
            self.metric_names = [metric_names]
        else:
            self.metric_names = metric_names
        self.exprs = exprs
        self.rule = copy.deepcopy(rule)
        self.kwargs = kwargs
        self.result = None
        self.return_messages = []
        self.to_json = to_json

    def isStorageBound(self, node):
        """
        Return true if the scan node (specified by the surragate id of the scan_node) is IO bound.
        It is considered IO bound if the enclosing fragment's "TotalStorageWaitTime" > 30% of the
        fragment's "TotalTime"
        :param scan_node_id: the surragat node id
        :return:
        """
        storagetime = models.query_fragment_metric_by_node_id(node, 'TotalStorageWaitTime')
        totaltime = models.query_fragment_metric_by_node_id(node, 'TotalTime')
        if (storagetime is None or totaltime is None):
            return False
        return (float(storagetime) / float(totaltime)) > 0.3

    def getNumInputRows(self, node):
        """
        Return the number of input rows for the given plan node id (surrogate node id).
        For scan, return the #rows read.
        For exchange, return the #rows returned == #rows processed.
        For join, return the probe rows.
        For table sink, it's the rows inserted
        For all others, return the rows returned by all its children
        :param plan_node_id:
        :return:
        """
        nodeType = node.name()

        if (nodeType == 'HDFS_SCAN_NODE'):
            return node.find_metric_by_name('RowsRead')[0]['value']
        if (nodeType == 'EXCHANGE_NODE'):
            return node.find_metric_by_name('RowsReturned')[0]['value']
        if (nodeType == 'HASH_JOIN_NODE'):
            return node.find_metric_by_name('ProbeRows')[0]['value']
        if (nodeType == 'HdfsTableSink'):
            return node.find_metric_by_name('RowsInserted')[0]['value']

        metrics = reduce(lambda x,y: x + y.find_metric_by_name('RowsReturned'), node.children, [])
        return reduce(lambda x,y: x + y['value'], metrics, 0)

    def evaluate(self, profile, plan_node_id):
        """
        Evaluate the impact of this cause to the query. The return is a json string with
        this format:
        {
            "impact": the amount of slow down (in ns),
            "message" : the displayed "explanation" string
        }
        :return:
        """
        impact = -1
        if len(self.exprs):
            assert len(self.metric_names) == 1

            # metric_names can have multiple values create a dict for all of
            # them
            db_result = models.query_node_by_id(profile, plan_node_id, self.metric_names[0])
            for k, g in groupby(db_result, lambda x: x.fid):
                grouped = list(g)
                # A list of pairs, with aggregated value and index at value for
                # max / min like exprs
                converted_exprs = self.check_exprs(grouped)
                expr_vars = {
                    "vars": dict(zip(self.exprs, map(lambda x: x[0], converted_exprs))),
                    "idxs": dict(zip(self.exprs, map(lambda x: x[1], converted_exprs))),
                }

                expr_val = exprs.Expr.evaluate(self.rule["expr"], expr_vars)
                if (impact is None or impact < expr_val):
                    impact = expr_val
        else:
            # For each of the metrics get the result
            with Timer() as t:
                # Get the metric values from the db grouped by metric name
                db_result = [models.query_node_by_id(profile, plan_node_id, m) for m in self.metric_names]
                # Assuming that for all metric names the same number of rows have been returned transpose the array
                all_metrics = zip(*db_result)

            for row in all_metrics:
                # Convert to double values if unit is 6(double)
                metric_values = map(lambda x: x.value if x.unit != 6 else to_double(x.value), row)

                surrogate_node = row[0].node
                local_vars = {"vars": dict(zip(self.metric_names, metric_values))}
                local_vars["vars"]["IOBound"] = self.isStorageBound(surrogate_node)
                local_vars["vars"]['InputRows'] = self.getNumInputRows(surrogate_node)
                condition = True
                if ("condition" in self.rule):
                    condition = exprs.Expr.evaluate(self.rule["condition"], local_vars)
                if (condition):
                    expr_val = exprs.Expr.evaluate(self.rule["expr"], local_vars)
                    if (impact is None or impact < expr_val):
                        impact = expr_val

        msg = self.rule["label"] + ": " + self.rule["message"]
        return {
            "impact": impact,
            "message": msg
        }

    def check_exprs(self, group):
        """For each of the specified expressions evaluate the function"""
        result = []
        for e in self.exprs:
            result.append(getattr(exprs, "expr_{0}".format(e))(
                [g.value for g in group]))
        return result

class JoinOrderStrategyCheck(SQLOperatorReason):
    def __init__(self): pass

    def evaluate(self, profile, plan_node_id):
        """
        Determine if the join order/strategy is correct and evaluate the impact of this cause
        to the query. The return is a json string with
        this format:
        {
            "impact": the amount of slow down (in ns),
            "message" : the displayed "explanation" string
        }
        :return:
        """
        self.metric_names = ["Hosts", "Broadcast", "BuildRows", "ProbeRows"]

        hosts = models.query_node_by_id(profile, plan_node_id, "Hosts", True)[0][0]
        isBroadcast = models.query_node_by_id(profile, plan_node_id, "Broadcast", True)[0][0]
        buildRows = models.query_node_by_id(profile, plan_node_id, "BuildRows", True)[0][0]
        probeRows = models.query_node_by_id(profile, plan_node_id, "ProbeRows", True)[0][0]

        rhsRows = 0
        lhsRows = 0
        networkcost = 0
        if (isBroadcast == 1):
            networkcost = buildRows * hosts
            rhsRows = buildRows
            lhsRows = probeRows * hosts
        else:
            networkcost = (buildRows + probeRows) * hosts
            rhsRows = buildRows * hosts
            lhsRows = probeRows * hosts

        impact = (rhsRows - lhsRows * 1.5) / hosts / 0.01
        if (impact > 0):
            return {
                "impact": impact,
                "message": "Wrong join order - RHS %d; LHS %d" % (rhsRows, lhsRows)
            }

        bcost = rhsRows * hosts
        scost = lhsRows + rhsRows
        impact = (networkcost - min(bcost, scost) - 1) / hosts / 0.01
        return {
            "impact": impact,
            "message": "Wrong join strategy - RHS %d; LHS %d" % (rhsRows, lhsRows)
        }

class ExplodingJoinCheck(SQLOperatorReason):
    def __init__(self): pass

    def evaluate(self, profile, plan_node_id):
        """
        Determine if the join exploded the number of rows
        this format:
        {
            "impact": the amount of slow down (in ns),
            "message" : the displayed "explanation" string
        }
        :return:
        """
        self.metric_names = ["Hosts", "Broadcast", "BuildRows", "ProbeRows"]

        hosts = models.query_node_by_id(profile, plan_node_id, "Hosts", True)[0][0]
        probeRows = models.query_node_by_id(profile, plan_node_id, "ProbeRows", True)[0][0]
        probeTime = models.query_node_by_id(profile, plan_node_id, "ProbeTime", True)[0][0]
        rowsReturned = models.query_node_by_id(profile, plan_node_id, "RowsReturned", True)[0][0]

        impact = 0
        if (rowsReturned > 0):
            impact = probeTime * (rowsReturned - probeRows) / rowsReturned
        return {
            "impact": impact,
            "message": "Exploding join: %d input rows are exploded to %d output rows" % (probeRows, rowsReturned)
        }

class NNRpcCheck(SQLOperatorReason):
    def __init__(self): pass

    def evaluate(self, profile, plan_node_id):
        """
        Determine the impact of NN RPC latency
        this format:
        {
            "impact": the amount of slow down (in ns),
            "message" : the displayed "explanation" string
        }
        :return:
        """
        totalStorageTime = models.query_avg_fragment_metric_by_node_nid(profile, plan_node_id, "TotalStorageWaitTime")
        hdfsRawReadTime = models.query_node_by_id(profile, plan_node_id, "TotalRawHdfsReadTime(*)", True)[0][0]
        avgReadThreads = models.query_node_by_id(profile, plan_node_id, "AverageHdfsReadThreadConcurrency", True)[0][0]
        avgReadThreads = max(1, to_double(avgReadThreads))
        impact = max(0, (totalStorageTime - hdfsRawReadTime) / avgReadThreads)
        return {
            "impact": impact,
            "message": "This is the time waiting for HDFS NN RPC."
        }

class TopDownAnalysis:

    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), "../..", "reasons")

        # sqlOperatorReasons maps from node name (such as HDFS_SCAN_NODE) to the list
        # of reasons that are applicable to this operator.
        self.sqlOperatorReasons = {}
        for r in glob.glob("{0}/*.json".format(self.base_dir)):
            with open(r, "r") as fid:
                json_object = json.load(fid)
                type = json_object["type"]
                node_names = json_object["node_name"]
                nodes = node_names
                if not isinstance(node_names, types.ListType):
                    nodes = [node_names]
                for node in nodes:
                    self.sqlOperatorReasons.setdefault(node,[])\
                        .append(SQLOperatorReason(**json_object))

        # Manually append specially coded reaason
        self.sqlOperatorReasons["HASH_JOIN_NODE"].append(JoinOrderStrategyCheck())
        self.sqlOperatorReasons["HASH_JOIN_NODE"].append(ExplodingJoinCheck())
        self.sqlOperatorReasons["HDFS_SCAN_NODE"].append(NNRpcCheck())

    def getTopContributor(self, limit=5, profile=None):
        """ Return the top N wall clock time contributor. Contributor can be planning time,
        admission control wait time, query fragment distribution time, SQL operator, DML
        update time, client fetch wait time.
        For SQL operator, the "max" time used.
        This function will return a list of map:
        {
            "type": (planning time, admission control time, SQL operator...etc),
            "wall_clock_time :
            "plan_node_id" : (only if SQL operator)
            "plan_node_name" : (only if SQL operator)
        }
        """
        execTime = sorted(profile, key=lambda x: x.wall_clock_time, reverse=True)
        execTime = execTime[:limit]

        # Sort execTime based on wall_clock_time and cut it off at limit
        return execTime

    def getTopReasons(self, contributor):
        """
        For the given contributor id, return the top reasons why it's slow.
        The result will be in the form of
        [
            {
                "impact" : 7000000,
                "message" : "Predicates might be expensive (expectes speed 40m rows per sec)"
            },
            {
                "impact" : 4000000,
                "message" : "too many columns",
            }
        ]
        """
        return sorted(contributor.reason, key=lambda x: x.impact, reverse=True) if contributor.reason else contributor.reason


    def createContributors(self, profile):
        """ Return the models.Contributor objects. Contributor can be planning time,
        admission control wait time, query fragment distribution time, SQL operator, DML
        update time, client fetch wait time.
        For SQL operator, the "max" time used.
        This function will return a list of models.Controbutor objects and these objects are
        persisted in the database.
        """
        execution_profile = profile.find_by_name('Execution Profile')
        #summary = _profile.find_by_name("Summary")
        counter_map = profile.find_by_name('Summary').counter_map()
        counter_map.update(profile.find_by_name("ImpalaServer").counter_map())
        #counter_map = summary.counter_map()

        # list of non-SQL operator contributor
        # TODO: add admission control, DML Metastore update; profile does not have it yet.
        nonExecMetrics = ['PlanningTime', 'RemoteFragmentsStarted',
                          'RowMaterializationTimer', 'ClientFetchWaitTimer']

        contributors = []
        for metric in nonExecMetrics:
            contributor = models.Contributor(type=metric,
                                             wall_clock_time=counter_map[metric].value,
                                             plan_node_id=-1, plan_node_name="N/A")
            #models.db.session.add(contributor)
            contributors += [contributor]

        if self.isDebugBuilt(profile):
            contributor = models.Contributor(type="Debug Built",
                                             wall_clock_time=9999999999999999,
                                             plan_node_id=-1, plan_node_name="N/A")
            #models.db.session.add(contributor)
            contributors += [contributor]

        # Get the top N contributor from query execution

        # Get the plan node execution time
        # Note: ignore DataStreamSender because its metrics is useless
        nodes = execution_profile.find_all_non_fragment_nodes()
        nodes = filter(lambda x: x.fragment and x.fragment.is_averaged() == False, nodes)
        nodes = filter(lambda x: x.name() != 'DataStreamSender', nodes)
        metrics = reduce(lambda x,y: x + y.find_metric_by_name('LocalTime'), nodes, [])
        metrics = sorted(metrics, key=lambda x: (x['node'].id(), x['node'].name()))
        for k, g in groupby(metrics, lambda x: (x['node'].id(), x['node'].name())):
            grouped = list(g)
            metric_values = map(lambda x: x['value'], grouped)
            metric = max(metric_values)
            contributor = models.Contributor(type="SQLOperator",
                                 wall_clock_time=metric,
                                 plan_node_id=grouped[0]['node'].id(), plan_node_name=grouped[0]['node'].name())
            contributors += [contributor]


        # Sort execTime based on wall_clock_time and cut it off at limit
        contributors = sorted(contributors, key=lambda x: x.wall_clock_time, reverse=True)
        return contributors

    def createExecNodeReason(self, contributor, profile):
        """
        For the given contributor, return the top reasons why it's slow. A list of models.Reason
        object will be created, persisted to the database and returned.
        The result will be in the form of
        """
        reasons = []
        self.sqlOperatorReasons.setdefault(contributor.plan_node_name,[])
        for cause in self.sqlOperatorReasons[contributor.plan_node_name] + self.sqlOperatorReasons["ANY"]:
            evaluation = cause.evaluate(profile, contributor.plan_node_id)
            impact = evaluation["impact"]
            if isinstance(impact, float) and (impact).is_integer():
              evaluation["impact"] = int(impact)
            if (evaluation["impact"] > 0):
                reason = models.Reason(message=evaluation['message'], impact=evaluation['impact'])
                reasons.append(reason)
        return sorted(reasons, key=lambda x: x.impact, reverse=True)

    def isDebugBuilt(self, profile):
        summary = profile.find_by_name('Summary')
        versionStr = summary.val.info_strings['Impala Version']
        if "debug" in versionStr.lower():
            return True
        return False

    def process(self, profile):
        contributors = self.createContributors(profile)
        for contributor in contributors:
            if (contributor.type == "SQLOperator"):
                reasons = self.createExecNodeReason(contributor, profile)
            else:
                reasons = []
            contributor.reason = reasons
        return contributors

    def pre_process(self, profile):
        summary = profile.find_by_name("Summary")
        exec_summary_json = utils.parse_exec_summary(summary.val.info_strings['ExecSummary'])

        # Setup Event Sequence
        if summary:
          for s in summary.val.event_sequences:
              sequence_name = s.name
              if sequence_name == "Query Timeline":
                duration = 0
                for i in range(len(s.labels)):
                    event_name = s.labels[i]
                    event_duration = s.timestamps[i] - duration
                    event_value = s.timestamps[i]
                    if event_name == "Planning finished":
                      summary.val.counters.append(models.TCounter(name='PlanningTime', value=event_duration, unit=5))

                    elif re.search('remote fragments started', event_name, re.IGNORECASE) is not None or re.search('fragment instances started', event_name, re.IGNORECASE) is not None or re.search(r'execution backends.*started', event_name, re.IGNORECASE)  is not None:
                      summary.val.counters.append(models.TCounter(name='RemoteFragmentsStarted', value=event_duration, unit=5))

                    duration = s.timestamps[i]

        def add_host(node, exec_summary_json=exec_summary_json):
          is_plan_node = node.is_plan_node()
          node_id = node.id()
           # Setup Hosts & Broadcast
          if node_id and node.is_regular() and int(node_id) in exec_summary_json:

            node.val.counters.append(models.TCounter(name='Hosts', value=exec_summary_json[int(node_id)]["hosts"], unit=0))
            broadcast = 0
            if exec_summary_json[int(node_id)]["broadcast"]:
                broadcast = 1
            node.val.counters.append(models.TCounter(name='Broadcast', value=broadcast, unit=0))

          # Setup LocalTime & ChildTime
          if node_id:
            child_time = 0
            for c in node.children:
                if c.is_plan_node():
                    child_time += c.counter_map()['TotalTime'].value

            counter_map = node.counter_map()

            # Load the metric data as if the object would be loaded from the DB
            local_time = counter_map['TotalTime'].value - child_time

            # Make sure to substract the wait time for the exchange node
            if is_plan_node and re.search(r'EXCHANGE_NODE', node.val.name) is not None:
                async_time = counter_map.get('AsyncTotalTime', models.TCounter(value=0)).value
                local_time = counter_map['TotalTime'].value - counter_map['InactiveTotalTime'].value - async_time

            # For Hash Join, if the "LocalTime" metrics
            if is_plan_node and re.search(r'HASH_JOIN_NODE', node.val.name) is not None:
                if ("LocalTime" in counter_map):
                    local_time = counter_map["LocalTime"].value
                else:
                    local_time = counter_map["ProbeTime"].value +\
                        counter_map["BuildTime"].value

            # Add two virtual metrics for local_time and child_time
            node.val.counters.append(models.TCounter(name='LocalTime', value=local_time, unit=5))
            node.val.counters.append(models.TCounter(name='ChildTime', value=child_time, unit=5))

        profile.foreach_lambda(add_host)

    def run(self, profile):
        self.pre_process(profile)
        contributors = self.process(profile)
        topContributors = self.getTopContributor(100, contributors)

        topContributions = []
        result_id = 1

        if self.isDebugBuilt(profile):
            topContributions += [{
                "result_id" : result_id,
                "contribution_factor_str" : "Using Debug Built",
                "wall_clock_time" : 9999,
                "reason" : []
            }]

        for contributor in topContributors:
            reasons = self.getTopReasons(contributor)
            topContributions += [{
                    "result_id" : contributor.plan_node_id if contributor.plan_node_id != -1 else '-1',
                    "contribution_factor_str" : contributor.type + " " +
                                                str(contributor.plan_node_id).zfill(2) +
                                                ":" + contributor.plan_node_name,
                    "wall_clock_time" : contributor.wall_clock_time,
                    "reason" : [reason.__dict__ for reason in reasons]
                }]

        result = []
        result += [{
                "rule": {
                    "message": "Top contributing factors and its reasons",
                    "label": "Top Down Analysis",
                    "prio": 1
                },
                "result": topContributions,
                "template": "alan-tpl"
            }]
        return result