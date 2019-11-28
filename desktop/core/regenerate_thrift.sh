#!/bin/bash

cd $(dirname $0)/src/desktop/lib
thrift -r --gen py:new_style *thrift
