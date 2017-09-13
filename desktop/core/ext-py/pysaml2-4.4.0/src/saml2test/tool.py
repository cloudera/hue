import cookielib
import sys
import traceback
import logging
from urlparse import parse_qs
import six

from saml2test.opfunc import Operation
from saml2test import CheckError, FatalError
from saml2test.check import ExpectedError, ERROR
from saml2test.interaction import Interaction
from saml2test.interaction import Action
from saml2test.interaction import InteractionNeeded
from saml2test.status import STATUSCODE
from saml2test.status import INTERACTION
from saml2test import OperationError

__author__ = 'rolandh'

logger = logging.getLogger(__name__)


class Conversation(object):
    """
    :ivar response: The received HTTP messages
    :ivar protocol_response: List of the received protocol messages
    """

    def __init__(self, client, config, interaction,
                 check_factory=None, msg_factory=None,
                 features=None, verbose=False, expect_exception=None):
        self.client = client
        self.client_config = config
        self.test_output = []
        self.features = features
        self.verbose = verbose
        self.check_factory = check_factory
        self.msg_factory = msg_factory
        self.expect_exception = expect_exception

        self.cjar = {"browser": cookielib.CookieJar(),
                     "rp": cookielib.CookieJar(),
                     "service": cookielib.CookieJar()}

        self.protocol_response = []
        self.last_response = None
        self.last_content = None
        self.response = None
        self.interaction = Interaction(self.client, interaction)
        self.exception = None

    def check_severity(self, stat):
        if stat["status"] >= 4:
            logger.error("WHERE: %s", stat["id"])
            logger.error("STATUS:%s", STATUSCODE[stat["status"]])
            try:
                logger.error("HTTP STATUS: %s", stat["http_status"])
            except KeyError:
                pass
            try:
                logger.error("INFO: %s", stat["message"])
            except KeyError:
                pass

            raise CheckError

    def do_check(self, test, **kwargs):
        if isinstance(test, six.string_types):
            chk = self.check_factory(test)(**kwargs)
        else:
            chk = test(**kwargs)
        stat = chk(self, self.test_output)
        self.check_severity(stat)

    def err_check(self, test, err=None, bryt=True):
        if err:
            self.exception = err
        chk = self.check_factory(test)()
        chk(self, self.test_output)
        if bryt:
            e = FatalError("%s" % err)
            e.trace = "".join(traceback.format_exception(*sys.exc_info()))
            raise e

    def test_sequence(self, sequence):
        for test in sequence:
            if isinstance(test, tuple):
                test, kwargs = test
            else:
                kwargs = {}
            self.do_check(test, **kwargs)
            if test == ExpectedError:
                return False
        return True

    def my_endpoints(self):
        pass

    def intermit(self):
        _response = self.last_response
        _last_action = None
        _same_actions = 0
        if _response.status_code >= 400:
            done = True
        else:
            done = False

        url = _response.url
        content = _response.text
        while not done:
            rdseq = []
            while _response.status_code in [302, 301, 303]:
                url = _response.headers["location"]
                if url in rdseq:
                    raise FatalError("Loop detected in redirects")
                else:
                    rdseq.append(url)
                    if len(rdseq) > 8:
                        raise FatalError(
                            "Too long sequence of redirects: %s" % rdseq)

                logger.info("HTTP %d Location: %s", _response.status_code, url)
                # If back to me
                for_me = False
                for redirect_uri in self.my_endpoints():
                    if url.startswith(redirect_uri):
                        # Back at the RP
                        self.client.cookiejar = self.cjar["rp"]
                        for_me = True
                        try:
                            base, query = url.split("?")
                        except ValueError:
                            pass
                        else:
                            _response = parse_qs(query)
                            self.last_response = _response
                            self.last_content = _response
                            return _response

                if for_me:
                    done = True
                    break
                else:
                    try:
                        logger.info("GET %s", url)
                        _response = self.client.send(url, "GET")
                    except Exception as err:
                        raise FatalError("%s" % err)

                    content = _response.text
                    logger.info("<-- CONTENT: %s", content)
                    self.position = url
                    self.last_content = content
                    self.response = _response

                    if _response.status_code >= 400:
                        done = True
                        break

            if done or url is None:
                break

            _base = url.split("?")[0]

            try:
                _spec = self.interaction.pick_interaction(_base, content)
            except InteractionNeeded:
                self.position = url
                cnt = content.replace("\n", '').replace("\t", '').replace("\r",
                                                                          '')
                logger.error("URL: %s", url)
                logger.error("Page Content: %s", cnt)
                raise
            except KeyError:
                self.position = url
                cnt = content.replace("\n", '').replace("\t", '').replace("\r",
                                                                          '')
                logger.error("URL: %s", url)
                logger.error("Page Content: %s", cnt)
                self.err_check("interaction-needed")

            if _spec == _last_action:
                _same_actions += 1
                if _same_actions >= 3:
                    self.test_output.append(
                        {"status": ERROR,
                         "message": "Interaction loop detection",
                         #"id": "exception",
                         #"name": "interaction needed",
                         "url": self.position})
                    raise OperationError()
            else:
                _last_action = _spec

            if len(_spec) > 2:
                logger.info(">> %s <<", _spec["page-type"])
                if _spec["page-type"] == "login":
                    self.login_page = content

            _op = Action(_spec["control"])

            try:
                _response = _op(self.client, self, url, _response, content,
                                self.features)
                if isinstance(_response, dict):
                    self.last_response = _response
                    self.last_content = _response
                    return _response
                content = _response.text
                self.position = url
                self.last_content = content
                self.response = _response

                if _response.status_code >= 400:
                    txt = "Got status code '%s', error: %s"
                    logger.error(txt, _response.status_code, content)
                    self.test_output.append(
                        {"status": ERROR,
                         "message": txt % (_response.status_code, content),
                         #"id": "exception",
                         #"name": "interaction needed",
                         "url": self.position})
                    raise OperationError()
            except (FatalError, InteractionNeeded, OperationError):
                raise
            except Exception as err:
                self.err_check("exception", err, False)

        self.last_response = _response
        try:
            self.last_content = _response.text
        except AttributeError:
            self.last_content = None

    def init(self, phase):
        self.creq, self.cresp = phase

    def setup_request(self):
        self.request_spec = req = self.creq(conv=self)

        if isinstance(req, Operation):
            for intact in self.interaction.interactions:
                try:
                    if req.__class__.__name__ == intact["matches"]["class"]:
                        req.args = intact["args"]
                        break
                except KeyError:
                    pass
        else:
            try:
                self.request_args = req.request_args
            except KeyError:
                pass
            try:
                self.args = req.kw_args
            except KeyError:
                pass

        # The authorization dance is all done through the browser
        if req.request == "AuthorizationRequest":
            self.client.cookiejar = self.cjar["browser"]
        # everything else by someone else, assuming the RP
        else:
            self.client.cookiejar = self.cjar["rp"]

        self.req = req

    def send(self):
        pass

    def handle_result(self):
        pass

    def do_query(self):
        self.setup_request()
        self.send()
        if not self.handle_result():
            self.intermit()
            self.handle_result()

    def do_sequence(self, oper):
        try:
            self.test_sequence(oper["tests"]["pre"])
        except KeyError:
            pass

        for phase in oper["sequence"]:
            self.init(phase)
            try:
                self.do_query()
            except InteractionNeeded:
                cnt = self.last_content.replace("\n", '').replace(
                    "\t", '').replace("\r", '')
                self.test_output.append({"status": INTERACTION,
                                         "message": cnt,
                                         "id": "exception",
                                         "name": "interaction needed",
                                         "url": self.position})
                break
            except (FatalError, OperationError):
                raise
            except Exception as err:
                #self.err_check("exception", err)
                raise

        try:
            self.test_sequence(oper["tests"]["post"])
        except KeyError:
            pass
