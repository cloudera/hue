#!/bin/bash
#Clean up old history to keep DB from growing too large

SCRIPT_DIR="$( cd -P "$( dirname "$0" )" && pwd )"
${SCRIPT_DIR}/script_runner hue_desktop_document_cleanup --keep-days 30