#!/home/csso_ranade/mypy2.7/bin/python

import base64
import json
import logging
import socket
import sys
import uuid
from datetime import datetime, timedelta

import urllib3
urllib3.disable_warnings()

# import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1
# LOG = logging.getLogger(__name__)
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

import signer_protos_pb2 as raz_signer

import boto3
from boto3.session import Session
from botocore.client import Config
from botocore import UNSIGNED
from botocore.model import ServiceId
from botocore.compat import urlsplit, parse_qs
from botocore.handlers import disable_signing

import requests
import requests_kerberos

logger = logging.getLogger(__name__)

cert_path = "/opt/cloudera/parcels/CDH/lib/hue/build/env/lib/python2.7/site-packages/certifi-2018.1.18-py2.7.egg/certifi/cacert.pem"

class RazToken(object):
    def __init__(self, raz_url, kerberos_auth):
        self.raz_url = raz_url
        self.kerberos_auth = kerberos_auth
        self.init_time = datetime.now()
        self.raz_token = None
        tstamp=(self.init_time + timedelta(minutes=3)).strftime("%Y%m%dT%H%M%SZ")
        o = urlsplit(self.raz_url)
        self.raz_port = o.port
        self.raz_hostname = o.hostname
        self.scheme = o.scheme

    def get_delegation_token(self, user="csso_ranade"):
        ip_address = socket.gethostbyname(self.raz_hostname)
        GET_PARAMS = {"op": "GETDELEGATIONTOKEN", "service": "%s:%s" % (ip_address, self.raz_port), "renewer": user}
        r = requests.get(self.raz_url, GET_PARAMS, auth=self.kerberos_auth, verify=False)
        self.raz_token = json.loads(r.text)['Token']['urlString']
        return self.raz_token

    def renew_delegation_token(self, user="csso_ranade"):
        if self.raz_token==None:
            self.raz_token = self.get_delegation_token(user=user)
        if (self.init_time + timedelta(hours=8)) > datetime.now():
            r = requests.put("%s?op=RENEWDELEGATIONTOKEN&token=%s"%(self.raz_url, self.raz_token), auth=self.kerberos_auth, verify=False)
        return self.raz_token

class RazS3SignerPlugin(object):
    def __init__(self, request, raz_url, raz_token, *args, **kwargs):
        # args <type 'tuple'>: ()
        # kwargs {'event_name': 'request-created.s3.HeadBucket', 'operation_name': u'HeadBucket'}
        logger.debug("Sign request: {%s}, args: {%s}, kwargs: {%s}"%(request, args, kwargs))
        self.request = request
        self.raz_url = raz_url
        self.raz_token = raz_token
        self.args = args
        self.kwargs = kwargs
        self.requestid = str(uuid.uuid4())

    def sign_request(self):
        logger.debug("inside sign")
        o = urlsplit(self.request.url)
        params = parse_qs(o.query)
        allparams = [raz_signer.StringListStringMapProto(key=key, value=val) for key, val in params.items()]
        allparams.extend([raz_signer.StringListStringMapProto(key=key, value=val) for key, val in self.request.params.items()])
        headers = [raz_signer.StringStringMapProto(key=key, value=val) for key, val in self.request.headers.items()]
        endpoint = "%s://%s" % (o.scheme, o.netloc)
        resource_path=o.path.lstrip("/")
        # if len(self.args)>1 and type(self.args[1])==type({}) and self.args[1]["operation_name"]=="ListObjectsV2":
        #     resource_path="%s/"%(resource_path)
        logger.debug("preparing sign request with http_method: {%s}, header: {%s}, parameters: {%s}, endpoint: {%s}, resource_path: {%s}"%(self.request.method, headers, allparams, endpoint, resource_path))
        raz_req = raz_signer.SignRequestProto(endpoint_prefix="s3", service_name="s3",
                                              endpoint=endpoint,
                                              http_method=self.request.method,
                                              headers=headers,
                                              parameters=allparams,
                                              resource_path=resource_path,
                                              time_offset=0)
        raz_req_serialized = raz_req.SerializeToString()
        signed_request = base64.b64encode(raz_req_serialized)

        logger.debug("inside check_access")
        request_data = {"requestId":self.requestid,
                        "serviceType":"s3",
                        "serviceName":"cm_s3",
                        "user":"csso_ranade",  # make change to improve KERBEROS USER NAME
                        "userGroups":[],
                        "accessTime":"",
                        "clientIpAddress":"",
                        "clientType": "",
                        "clusterName":"prakashdb23",
                        "clusterType":"",
                        "sessionId":"",
                        "context":{"S3_SIGN_REQUEST":signed_request}
                        }
        headers = {"Content-Type":"application/json", "Accept-Encoding":"gzip,deflate"}
        # headers.update(self.request.headers)

        logger.debug("sending access check headers: {%s} request_data: {%s}" % (headers, request_data)) 
        rurl = "%s/api/authz/s3/access?delegation=%s"%(self.raz_url, self.raz_token)
        raz_req = requests.post(rurl, headers=headers, json=request_data, verify=False)
        s3_sign_response = None
        signed_response = None
        if raz_req.ok:
            if raz_req.json().get("operResult", False) and raz_req.json()["operResult"]["result"]=="NOT_DETERMINED":
                logger.error("failure %s"%(raz_req.json()))
                sys.exit(1)
            if raz_req.json().get("operResult", False) and raz_req.json()["operResult"]["result"]=="ALLOWED":
                s3_sign_response=raz_req.json()["operResult"]["additionalInfo"]["S3_SIGN_RESPONSE"]
            if s3_sign_response:
                raz_response_proto=raz_signer.SignResponseProto()
                signed_response=raz_response_proto.FromString(base64.b64decode(s3_sign_response))
                logger.debug("Received signed Response %s" % signed_response)
            if signed_response:
                for i in signed_response.signer_generated_headers:
                    self.request.headers[i.key]=i.value
        if not signed_response:
            return False
        return True

# def rizSigner(*args, **kwargs):
#     client_config = kwargs.get("context").get("client_config")
#     print "Hello RazSigner"
#     print "Hello RazSigner"
#
def checkAccess(request, *args, **kwargs):
    credentials = kwargs.get("request_signer")._credentials
    print("Inside Before RazSigner")

def getRazSign(request, *args, **kwargs):
    raz_url="https://prakashdh27-master10.prakashr.xcu2-8y8x.dev.cldr.work:6082"
    kerberos_auth = requests_kerberos.HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)
    raz = RazToken(raz_url, kerberos_auth)
    raz_token = raz.get_delegation_token(user="csso_ranade")
    raz = RazS3SignerPlugin(request, raz_url, raz_token, args, kwargs)
    rs = raz.sign_request()
    if rs == False:
        return False

def list_objects(session, s3service, region_name, config, bucket):
    #client = session.client(s3service, region_name=region_name, endpoint_url="https://s3.%s.amazonaws.com"%(region_name), config=config)
    client = session.client(s3service, region_name=region_name, config=config)
    paginator = client.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket)
    for page in page_iterator:
        print(page)


def main():
    bucket = "prakashmowdev1"
    key = "user/csso_ranade/footravel.csv"
    key2 = "user/csso_ranade/footravel2.csv"

    s3service = ServiceId("s3")
    session = Session(region_name="us-west-2")
    # session.events.unregister('before-parameter-build.s3.ListObjects', set_list_objects_encoding_type_url)
    session.events.register_last('request-created.s3', getRazSign) # RequestSigner.handler

    s3 = boto3.resource(s3service)
    s3.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
    config = Config(signature_version=UNSIGNED)

    # Get Object
    client = session.client(service_name=s3service, config=config)
    r1 = client.head_bucket(Bucket=bucket)
    region = ""
    if r1["ResponseMetadata"]["HTTPStatusCode"] == 200:
        region = r1['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']
    print("Prakash region is %s" % region)
    print(r1)

    # Read object file
    start_byte = 0
    stop_byte = 10000
    r2 = client.get_object(Bucket=bucket, Key=key, Range='bytes={}-{}'.format(start_byte, stop_byte))
    print(r2["Body"].read())
    print(r2)

    # Download file
    r3 = client.download_file(bucket, key, '/tmp/hello.txt')
    print(r3)

    # Upload objects
    f = open("/tmp/hello.txt", "r")
    r4 = client.put_object(Bucket=bucket, Key=key2, Body=f.read())
    print(r4)

    # region = "us-west-2"
    # config = Config(signature_version=UNSIGNED)
    # list_objects(session, s3service, region, config, bucket)

    client = session.client(s3service, region_name="us-west-2", endpoint_url="https://%s.s3.%s.amazonaws.com"%(bucket,"us-west-2"), config=config)
    paginator = client.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=" ", FetchOwner=False, EncodingType="url"):
        for obj in result['Contents']:
            print(obj)
    # r5 = client.list_objects(Bucket=bucket, Delimiter="/")
    # for o in r5.get('CommonPrefixes'):
    #     print(o.get('Prefix'))
    # print(r5)

    # client = session.client(service_name=s3service, region_name=region, endpoint_url="https://s3.%s.amazonaws.com"%(region))
    # r2 = client.get_object(Bucket=bucket, Key=key)
    # print(r2['Body'].read())
    #
    # r2 = client.list_buckets()
    # print(r2)

    # client = session.client(service_name=s3service, region_name=region, endpoint_url="https://s3.%s.amazonaws.com"%(region))
    # r2 = client.get_bucket_acl(Bucket=bucket)
    # print(r2)
    # bucket = s3.Bucket("prakashmowdev1")
    # for f in bucket.objects.all():
    #     print(f.key)

    # credentials = Credentials("", "")
    # session = botocore.session.get_session()
    #
    # # Working
    # config = Config(signature_version=botocore.UNSIGNED)
    # client = session.create_client(s3service, config=config)
    # client.meta.events.register_last('before-sign.s3', botocore.utils.fix_s3_host) # S3EndpointSetter.set_endpoint
    # client.meta.events.register_last('request-created.s3', getRazSign) # RequestSigner.handler
    # r1 = client.head_bucket(Bucket=bucket)
    # if r1["ResponseMetadata"]["HTTPStatusCode"]==200:
    #     print("it works")
    # region = r1['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']
    # print("Prakash region is %s"%region)
    #
    # config = Config(signature_version="s3v4", region_name=region)
    # client = session.create_client(s3service, region_name=region, config=config)
    # r2 = client.get_object(Bucket=bucket, Key=key)
    # print(r2['Body'].read())
    #
    # r2 = client.get_bucket_acl(Bucket=bucket)
    # print(r2)
    #
    # r2 = client.get_bucket_location(Bucket=bucket)
    # print(r2)
    #
    # r3 = client.list_buckets()
    # print(r3)

    print("="*80)

if __name__=="__main__":
    main()
