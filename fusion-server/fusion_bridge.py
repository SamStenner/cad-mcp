import adsk.core
import threading, socket, json, uuid, traceback, os
from typing import Any, Dict
from .cad_tools import CADTools

# --------------------------
# Config
# --------------------------
# Must match the host/port in the MCP server config
HOST, PORT = "127.0.0.1", 8765
EVENT_ID = "mcp_event_bridge"

# --------------------------
# Globals / state
# --------------------------
app: adsk.core.Application = None
ui: adsk.core.UserInterface = None
handlers = []
cad_tools = None

_pending: Dict[str, Dict[str, Any]] = {}
_pending_lock = threading.Lock()

_shutdown = threading.Event()
_server_socket: socket.socket | None = None
_server_thread: threading.Thread | None = None

def _fusion_log(msg: str):
    try:
        adsk.core.Application.get().log(f"[fusion_bridge] {msg}")
    except:
        pass

def _report(what: str, ex: Exception = None):
    if ex is None:
        txt = what
    else:
        txt = f"{what}: {ex}\n{traceback.format_exc()}"
    _fusion_log(txt)

# --------------------------
# Networking
# --------------------------
def _send(conn: socket.socket, obj: Any):
    try:
        data = (json.dumps(obj, default=_json_default) + "\n").encode("utf-8")
        conn.sendall(data)
    except Exception as e:
        _report("send failed", e)

def _socket_loop():
    try:
        global _server_socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(16)
        s.settimeout(0.5)
        _server_socket = s
        _report(f"listening on {HOST}:{PORT}")

        while not _shutdown.is_set():
            try:
                conn, _ = s.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                raw = b""
                conn.settimeout(5.0)
                chunk = conn.recv(1 << 20)  # ~1MB
                if not chunk:
                    conn.close()
                    continue
                raw += chunk

                try:
                    msg = json.loads(raw.decode("utf-8"))
                except Exception as ex:
                    _send(conn, {"ok": False, "error": f"Invalid JSON: {ex}"})
                    conn.close()
                    continue

                req_id = msg.get("id") or str(uuid.uuid4())
                msg["id"] = req_id

                ev = threading.Event()
                with _pending_lock:
                    _pending[req_id] = {"event": ev, "msg": msg, "result": None}

                app.fireCustomEvent(EVENT_ID, json.dumps({"id": req_id}))

                if not ev.wait(timeout=60):
                    with _pending_lock:
                        _pending.pop(req_id, None)
                    _send(conn, {"ok": False, "id": req_id, "error": "Timeout waiting for main thread"})
                    conn.close()
                    continue

                with _pending_lock:
                    res = _pending.pop(req_id, {}).get("result")

                if not res:
                    _send(conn, {"ok": False, "id": req_id, "error": "No result"})
                else:
                    _send(conn, res)

            except Exception as e:
                _report("socket handler failed", e)
                try:
                    _send(conn, {"ok": False, "error": str(e)})
                except:
                    pass
            finally:
                try:
                    conn.close()
                except:
                    pass
    except Exception as e:
        _report("socket loop failed", e)
    finally:
        try:
            if _server_socket:
                _server_socket.close()
        except:
            pass
        _server_socket = None

# --------------------------
# CustomEvent handler
# --------------------------
class _BridgeEvent(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CustomEventArgs):
        try:
            info = json.loads(args.additionalInfo or "{}")
            req_id = info.get("id")
            if not req_id:
                return
            with _pending_lock:
                entry = _pending.get(req_id)
            if not entry:
                return

            msg = entry["msg"]
            try:
                result = _handle_message(msg)
                entry["result"] = {"ok": True, "id": msg["id"], "result": result}
            except Exception as ex:
                entry["result"] = {"ok": False, "id": msg["id"], "error": f"{ex}", "trace": traceback.format_exc()}
            finally:
                entry["event"].set()

        except Exception as e:
            _report("CustomEvent notify failed", e)

# --------------------------
# RPC dispatch
# --------------------------
def _handle_message(msg: Dict[str, Any]) -> Any:
    m = msg.get("method")
    p = msg.get("params") or {}

    if hasattr(cad_tools, m):
        method = getattr(cad_tools, m)
        if callable(method):
            return method(p)
    
    raise ValueError(f"Unknown method: {m}")

# --------------------------
# Utilities
# --------------------------
def _json_default(o: Any):
    try:
        return getattr(o, "entityToken")
    except:
        return repr(o)

# --------------------------
# Add-in entry points
# --------------------------
def run(context):
    global app, ui, cad_tools
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        cad_tools = CADTools(app)

        cust = app.registerCustomEvent(EVENT_ID)
        if not cust:
            try:
                app.unregisterCustomEvent(EVENT_ID)
            except:
                pass
            cust = app.registerCustomEvent(EVENT_ID)
            if not cust:
                raise RuntimeError("registerCustomEvent returned None")

        on_event = _BridgeEvent()
        cust.add(on_event)
        handlers.append(on_event)

        global _server_thread
        _shutdown.clear()
        t = threading.Thread(target=_socket_loop, daemon=True)
        _server_thread = t
        t.start()

        _report("fusion_bridge started")
    except Exception as e:
        _report("run() failed", e)

def stop(context):
    try:
        _shutdown.set()
        try:
            if _server_socket:
                _server_socket.close()
        except:
            pass
        try:
            if _server_thread and _server_thread.is_alive():
                _server_thread.join(timeout=2.0)
        except:
            pass
        _report(f"stopped listening on {HOST}:{PORT}")
        adsk.core.Application.get().unregisterCustomEvent(EVENT_ID)
    except:
        pass
    _report("fusion_bridge stopped")
