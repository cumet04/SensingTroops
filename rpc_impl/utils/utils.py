import functools
import threading
import traceback
import socket
import sys
import xmlrpc.server as xmlrpc_server


def trace_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print('[ERROR] tracing error...', file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
    return wrapper


def run_rpc(ip, port, obj):
    # webサーバのループとasyncioのループをうまく共存させる方法がわからないため
    # スレッドを立てる方法でなんとかしている。
    # もっとスッキリできるといいのだが...
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.close()
        return False  # 問題無く接続できれば（=ポートが使用中であれば）失敗を返す
    except socket.error:
        pass

    server = xmlrpc_server.SimpleXMLRPCServer(
        (ip, port), allow_none=True, logRequests=False)
    server.register_instance(obj)
    server.register_introspection_functions()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return True
