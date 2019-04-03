.. developer-docs

Developer docs
==============

The easiest way to start developing ``python-future`` is as follows:

1. Install Anaconda Python distribution

2. Run::

    conda install -n future2 python=2.7 pip
    conda install -n future3 python=3.4 pip

    git clone https://github.com/PythonCharmers/python-future

3. If you are using Anaconda Python distribution, this comes without a ``test``
module on Python 2.x. Copy ``Python-2.7.6/Lib/test`` from the Python source tree
to ``~/anaconda/envs/yourenvname/lib/python2.7/site-packages/`.
