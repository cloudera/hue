#!/bin/sh


sp_testdrv.py -H -d -Y -J tt_config.json -c td_config $1 2> log/$1.log
