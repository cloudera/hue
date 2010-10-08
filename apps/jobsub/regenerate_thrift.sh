#!/bin/bash

cd $(dirname $0)
thrift -r --gen py:new_style -o . src/jobsub/jobsubd.thrift
