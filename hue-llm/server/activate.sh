if [ "$VIRTUAL_ENV" != "" ]; then
    echo "Error: venv is active"
    exit 1
fi

ver=$(python -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "39" ]; then
    echo "Error: Hue LLM Server requires python 3.9 or higher"
    exit 1
fi

VENV_PATH=".venv"

if [ ! -d $VENV_PATH ]; then
    echo "Setting up $VENV_PATH"
    python -m venv $VENV_PATH
fi

source $VENV_PATH/bin/activate
pip install -r requirements.txt

if [[ "$PYTHONPATH" != *"${PWD}"* ]]; then
  export PYTHONPATH="${PYTHONPATH}:${PWD}"
fi
