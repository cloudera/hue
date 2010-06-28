#!/bin/bash
find . -name "*.pyc" -print0 | xargs -0 rm -rf
