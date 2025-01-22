How sp_test works internally
============================

:Release: |release|
:Date: |today|

Here are a few hints on how sp_test works internally. It helps to extend it with
new test classes

When you want to test a SAML2 entity with this tool, you need the following things:

#. The Test Driver Configuration, an example can be found in tests/idp_test/config.py
#. Attribute Maps mapping URNs, OIDs and friendly names
#. Key files for the test tool
#. A metadata file representing the tool
#. The Test Target Configuration file describes how to interact with the entity to be tested.  The metadata for the entity is part of this file. An example can be found in tests/idp_test/test_target_config.py.

These files should be stored outside the saml2test package to have a clean separation between the package and a particular test configuration. To create a directory for the configuration files, copy the saml2test/tests including its contents.


(1) Class and Object Structure
::::::::::::::::::::::::::::::

Client (sp_test/__init__.py)
............................
Its life cycle is responsible for following activities:
 - read config files and command line arguments (the test driver's config is "json_config")
 - initialize the test driver IDP
 - initialize a Conversation
 - start the Conversion with .do_sequence_and_tests()
 - post-process log messages

Conversation (sp_test/base.py)
..............................

Operation (oper)
................
  - Comprises an id, name, sequence and tests
  - Example: 'sp-00': {"name": 'Basic Login test', "sequence": [(Login, AuthnRequest, AuthnResponse, None)], "tests": {"pre": [], "post": []}

OPERATIONS
..........
  - set of operations provided in sp_test
  - can be listed with the -l command line option

Sequence
........
  - A list of flows
  - Example: see "sequence" item in operation dict

Test (in the context of an operation)
.....................................
  - class to be executed as part of an operation, either before ("pre") or after ("post") the sequence or in between a SAML request and response ("mid").
    There are standard tests with the Request class (VerifyAuthnRequest) and operation-specific tests.
  - Example for an operation-specific "mid" test: VerifyIfRequestIsSigned
  - A test may be specified together with an argument as a tuple.

Flow
....
  * A tuple of classes that together implement a SAML request-response pair between IDP and SP (and possibly other actors, such as a discovery service or IDP-proxy). A class can be derived from Request, Response (or other), Check or Operation.
  * A flow for a solicited authentication consists of 4 classes:

    * flow[0]: Operation (Handling a login flow such as discovery or WAYF - not implemented yet)
    * flow[1]: Request (process the authentication request)
    * flow[2]: Response (send the authentication response)
    * flow[3]: Check (optional - can be None. E.g. check the response if a correct error status was raised when sending a broken response)

Check (and subclasses)
......................
  - An optional class that is executed on receiving the SP's HTTP response(s) after the SAML response. If there are redirects, it will be called for each response.
  - Writes a structured test report to conv.test_output
  - It can check for expected errors, which do not cause an exception but in contrary are reported as a success

Interaction
...........
  - An interaction automates a human interaction. It searches a response from a test target for some constants, and if
    there is a match, it will create a response suitable response.

(2) Simplified Flow
:::::::::::::::::::

The following pseudo code is an extract showing an overview of what is executed
for test sp-00::

    do_sequence_and_test(self, oper, test):
        self.test_sequence(tests["pre"])  # currently no tests defined for sp_test
        for flow in oper:
            self.do_flow(flow)

    do_flow(flow):
        if len(flow) >= 3:
            self.wb_send_GET_startpage()  # send start page GET request
            self.intermit(flow[0]._interaction)  # automate human user interface
            self.parse_saml_message()    # read relay state and saml message
        self.send_idp_response(flow[1], flow[2])  # construct, sign & send a nice Response from config, metadata and request
        if len(flow) == 4:
            self.handle_result(flow[3])  # pass optional check class
        else:
            self.handle_result()

    send_idp_response(req_flow, resp_flow):
        self.test_sequence(req_flow.tests["mid"])   # execute "mid"-tests (request has "VerifyContent"-test built in; others from config)
        # this line stands for a part that is a bit more involved .. see source

        args.update(resp._response_args)    # set userid, identity

    test_sequence(sequence):
        # execute tests in sequence (first invocation usually with check.VerifyContent)
        for test in sequence:
            self.do_check(test, **kwargs)

    do_check(test, **kwargs):
        # executes the test class using the __call__ construct

    handle_result(response=None):
        if response:
            if isinstance(response(), VerifyEchopageContents):
                if 300 < self.last_response.status_code <= 303:
                    self._redirect(self.last_response)
                self.do_check(response)
            elif isinstance(response(), Check):
                self.do_check(response)
            else:
                # A HTTP redirect or HTTP Post (not sure this is ever executed)
                ...
        else:
            if 300 < self.last_response.status_code <= 303:
                self._redirect(self.last_response)

            _txt = self.last_response.content
            if self.last_response.status_code >= 400:
                raise FatalError("Did not expected error")

(3) Status Reporting
::::::::::::::::::::
The proper reporting of results is at the core of saml2test. Several conditions
must be considered:

#. An operation that was successful because the test target reports OK (e.g. HTTP 200)
#. An operation that was successful because the test target reports NOK as expected, e.g. because of an invalid signature - HTTP 500 could be the correct response
#. An error in SAML2Test
#. An error in the configuration of SAML2Test

Status values are defined in saml2test.check like this:
INFORMATION = 0, OK = 1, WARNING = 2, ERROR = 3, CRITICAL = 4, INTERACTION = 5


There are two targets to write output to:
* Test_output is written to conv.test_output during the execution of the flows.
