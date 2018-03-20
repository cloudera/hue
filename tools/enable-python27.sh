#!/bin/bash

python27_exists=0
python_vers=("/usr/bin" "/usr/local/python27/bin" "/opt/rh/python27/root/usr/bin")

function run_python() {
  $1 --version >/dev/null 2>&1
  if [ ! $? -eq 0 ]; then
    echo 0
  else
    echo 1
  fi
}

for binpath in ${python_vers[@]}; do
  pybin="$binpath/python2.7"
  if [ ! -e $pybin ]; then
    continue
  fi
  if [[ $binpath == "/opt/rh/python27"* ]]; then
    if [ -f "/opt/rh/python27/enable" ]; then
      . /opt/rh/python27/enable
    fi
  fi
  out=$(run_python $pybin)
  if [ $out -eq 1 ]; then
    export PATH=$binpath:$PATH
    python27_exists=1
    break
  fi
done

if [ $python27_exists -eq 0 ]; then
  echo "ERROR: Unable to find python 2.7 installation"
fi
