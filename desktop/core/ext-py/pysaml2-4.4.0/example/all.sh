#!/bin/sh

startme() {
    cd sp-wsgi
    if [ ! -f sp_conf.py ] ; then
        cp sp_conf.py.example sp_conf.py
    fi
    if [ ! -f service_conf.py ] ; then
        cp service_conf.py.example service_conf.py
    fi
    ../../tools/make_metadata.py sp_conf > sp.xml

    cd ../idp2
    if [ ! -f idp_conf.py ] ; then
        cp idp_conf.py.example idp_conf.py
    fi
    ../../tools/make_metadata.py idp_conf > idp.xml

    cd ../sp-wsgi
    ./sp.py sp_conf &

    cd ../idp2
    ./idp.py idp_conf &

    cd ..
}

stopme() {
    pkill -f "sp.py"
    pkill -f "idp.py"
}

case "$1" in
    start)   startme ;;
    stop)    stopme ;;
    restart) stopme; startme ;;
    *) echo "usage: $0 start|stop|restart" >&2
       exit 1
       ;;
esac
