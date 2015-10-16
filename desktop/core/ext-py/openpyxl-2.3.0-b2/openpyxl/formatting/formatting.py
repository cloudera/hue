from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.compat import iteritems, OrderedDict, deprecated
from openpyxl.styles.differential import DifferentialStyle
from .rule import Rule


def unpack_rules(cfRules):
    for key, rules in iteritems(cfRules):
        for idx,rule in enumerate(rules):
            yield (key, idx, rule.priority)


class ConditionalFormatting(object):
    """Conditional formatting rules."""

    def __init__(self):
        self.cf_rules = OrderedDict()
        self.max_priority = 0

    def add(self, range_string, cfRule):
        """Add a rule such as ColorScaleRule, FormulaRule or CellIsRule

         The priority will be added automatically.
        """
        if not isinstance(cfRule, Rule):
            raise ValueError("Only instances of openpyxl.formatting.rule.Rule may be added")
        rule = cfRule
        self.max_priority += 1
        rule.priority = self.max_priority

        self.cf_rules.setdefault(range_string, []).append(rule)


    def _fix_priorities(self):
        rules = unpack_rules(self.cf_rules)
        rules = sorted(rules, key=lambda x: x[2])
        for idx, (key, rule_no, prio) in enumerate(rules, 1):
            self.cf_rules[key][rule_no].priority = idx
        self.max_priority = len(rules)


    @deprecated("Always use Rule objects")
    def update(self, cfRules):
        pass

    @deprecated("Conditionl Formats are saved automatically")
    def setDxfStyles(self, wb):
        pass
