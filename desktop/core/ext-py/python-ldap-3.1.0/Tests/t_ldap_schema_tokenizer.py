# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldap.schema.tokenizer

See https://www.python-ldap.org/ for details.
"""

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

import ldap.schema

# basic test cases
TESTCASES_BASIC = (
    (" BLUBBER DI BLUBB ", ["BLUBBER", "DI", "BLUBB"]),
    ("BLUBBER DI BLUBB", ["BLUBBER", "DI", "BLUBB"]),
    ("BL-UB-BER DI BL-UBB", ["BL-UB-BER", "DI", "BL-UBB"]),
    ("BLUBBER  DI   BLUBB  ", ["BLUBBER", "DI", "BLUBB"]),
    ("BLUBBER  DI  'BLUBB'   ", ["BLUBBER", "DI", "BLUBB"]),
    ("BLUBBER ( DI ) 'BLUBB'   ", ["BLUBBER", "(", "DI", ")", "BLUBB"]),
    ("BLUBBER(DI)", ["BLUBBER", "(", "DI", ")"]),
    ("BLUBBER ( DI)", ["BLUBBER", "(", "DI", ")"]),
    ("BLUBBER ''", ["BLUBBER", ""]),
    ("( BLUBBER (DI 'BLUBB'))", ["(", "BLUBBER", "(", "DI", "BLUBB", ")", ")"]),
    ("BLUBB (DA$BLAH)", ['BLUBB', "(", "DA", "BLAH", ")"]),
    ("BLUBB ( DA $  BLAH )", ['BLUBB', "(", "DA", "BLAH", ")"]),
    ("BLUBB (DA$ BLAH)", ['BLUBB', "(", "DA", "BLAH", ")"]),
    ("BLUBB (DA $BLAH)", ['BLUBB', "(", "DA", "BLAH", ")"]),
    ("BLUBB 'DA$BLAH'", ['BLUBB', "DA$BLAH"]),
    ("BLUBB DI 'BLU B B ER' DA 'BLAH' ", ['BLUBB', 'DI', 'BLU B B ER', 'DA', 'BLAH']),
    ("BLUBB DI 'BLU B B ER' DA 'BLAH' LABER", ['BLUBB', 'DI', 'BLU B B ER', 'DA', 'BLAH', 'LABER']),
    ("BLUBB\t'DA\tBLUB'", ['BLUBB', "DA\tBLUB"]),
)

# UTF-8 raw strings
TESTCASES_UTF8 = (
    (" BL\xc3\x9cBBER D\xc3\x84 BL\xc3\x9cBB ", ["BL\xc3\x9cBBER", "D\xc3\x84", "BL\xc3\x9cBB"]),
    ("BL\xc3\x9cBBER D\xc3\x84 BL\xc3\x9cBB", ["BL\xc3\x9cBBER", "D\xc3\x84", "BL\xc3\x9cBB"]),
    ("BL\xc3\x9cBBER  D\xc3\x84   BL\xc3\x9cBB  ", ["BL\xc3\x9cBBER", "D\xc3\x84", "BL\xc3\x9cBB"]),
)

# broken schema of Oracle Internet Directory
TESTCASES_BROKEN_OID = (
    ("BLUBB DI 'BLU B B ER'MUST 'BLAH' ", ['BLUBB', 'DI', 'BLU B B ER', 'MUST', 'BLAH']),
    ("BLUBBER DI 'BLU'BB ER' DA 'BLAH' ", ["BLUBBER", "DI", "BLU'BB ER", "DA", "BLAH"]),
)

# for quoted single quotes inside string values
TESTCASES_ESCAPED_QUOTES = (
    ("BLUBBER '\\''", ["BLUBBER", "'"]),
    ("BLUBBER DI 'BLU\\'BB ER' DA 'BLAH' ", ["BLUBBER", "DI", "BLU'BB ER", "DA", "BLAH"]),
    ("BLUBBER DI 'BLU\\' BB ER' DA 'BLAH' ", ["BLUBBER", "DI", "BLU' BB ER", "DA", "BLAH"]),
)

# test cases which should result in ValueError raised
TESTCASES_BROKEN = (
    "( BLUB",
    "BLUB )",
    "BLUB 'DA",
    "BLUB $ DA",
#    "BLUB 'DA\\'",
#    "( BLUB )) DA (",
)

class TestSplitTokens(unittest.TestCase):
    """
    test function ldap.schema.tokenizer.split_tokens()
    """

    def _run_split_tokens_tests(self, test_cases):
        for test_value, test_result in test_cases:
            token_list = ldap.schema.split_tokens(test_value)
            self.assertEqual(token_list, test_result)

    def _run_failure_tests(self, test_cases):
        should_have_failed = []
        for test_value in test_cases:
            try:
                _ = ldap.schema.split_tokens(test_value)
            except ValueError:
                pass
            else:
                should_have_failed.append(test_value)
        if should_have_failed:
            self.fail(
                '%d value(s) should have raised ValueError: %r' % (
                    len(should_have_failed),
                    should_have_failed,
                )
            )

    def test_basic(self):
        """
        run test cases specified in constant TESTCASES_BASIC
        """
        self._run_split_tokens_tests(TESTCASES_BASIC)

    def test_utf8(self):
        """
        run test cases specified in constant TESTCASES_BASIC
        """
        self._run_split_tokens_tests(TESTCASES_UTF8)

    @unittest.expectedFailure
    def test_broken_oid(self):
        """
        run test cases specified in constant TESTCASES_BROKEN_OID
        """
        self._run_failure_tests(TESTCASES_BROKEN_OID)

    @unittest.expectedFailure
    def test_escaped_quotes(self):
        """
        run test cases specified in constant TESTCASES_ESCAPED_QUOTES
        """
        self._run_split_tokens_tests(TESTCASES_ESCAPED_QUOTES)

    def test_broken(self):
        self._run_failure_tests(TESTCASES_BROKEN)


if __name__ == '__main__':
    unittest.main()
