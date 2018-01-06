import eventlet.websocket
import gunicorn
import os
import random
import sys


@eventlet.websocket.WebSocketWSGI
def wsapp(ws):
    ws.send(b'test pass')
    ws.close()


def app(environ, start_response):
    body = b'''<!doctype html>
<h1 id=status>loading...</h1>
<script>
  (function(D) {
    ws = new WebSocket('ws://127.0.0.1:5001/');
    ws.onmessage = function(msg) {
      var fr = new FileReader();
      fr.onload = function(ev) {
        D.getElementById('status').innerHTML = ev.target.result;
      }
      fr.readAsText(msg.data);
    };
    ws.onerror = function() {
      D.getElementById('status').innerHTML = 'test fail';
    }
  })(document);
</script>
'''
    if environ.get('HTTP_UPGRADE') == 'websocket':
        return wsapp(environ, start_response)

    start_response(
        '200 OK', (
            ('Content-type', 'text/html'),
            ('Content-Length', str(len(body))),
            ('X-Gunicorn-Version', gunicorn.__version__),
        ),
    )
    return [body]

if __name__ == '__main__':
    cmd = 'gunicorn websocket-gunicorn:app -b 127.0.0.1:5001 -k eventlet -w 1'
    sys.stderr.write('exec ' + cmd + '\n')
    os.system(cmd)
