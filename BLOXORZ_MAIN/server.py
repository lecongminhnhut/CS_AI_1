"""Local web interface; Python remains the authority for every game action."""

import argparse
import json
import secrets
import webbrowser
from http.cookies import CookieError, SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit

from bloxorz import Action, Board, Engine
from bloxorz.solver import solve
from bloxorz.levels import load_levels

ROOT = Path(__file__).resolve().parent
PACK = load_levels(ROOT / "levels/levels.json")
LEVELS = {f"stage-{i:02}": (level.name, f"Coolmath · {level.name}" +
                          (f" · Mã màn {level.passcode}" if level.passcode else ""))
          for i, level in enumerate(PACK, 1)}
BOARDS = {f"stage-{i:02}": level.board for i, level in enumerate(PACK, 1)}
LEVELS.update({"courtyard": ("Sân đá · Demo", "Tìm đường qua khu vườn lơ lửng."),
          "basic": ("Bước đầu tiên", "Lăn sang phải hai lần để vào đích."),
          "advanced": ("Những nhịp cầu · Demo", "Công tắc, cầu, ô dễ vỡ và hai khối con.")})
TESTCASE_GROUPS = json.loads((ROOT / "levels/testcases.json").read_text(encoding="utf-8"))["groups"]
TESTCASE_IDS = set()
for group in TESTCASE_GROUPS:
    for case in group["cases"]:
        key = case["id"]
        if not isinstance(key, str) or key in LEVELS:
            raise ValueError("Duplicate or invalid testcase ID")
        BOARDS[key] = Board.from_dict(case["board"])
        LEVELS[key] = (f"Test · {case['name']}", group["description"])
        TESTCASE_IDS.add(key)


class Session:
    def __init__(self):
        self.lock = Lock()
        self.reset("stage-01")

    def reset(self, level):
        if level not in LEVELS:
            raise ValueError("Unknown level")
        self.level = level
        self.engine = Engine(BOARDS[level] if level in BOARDS else Board.load(ROOT / "levels" / f"{level}.json"))
        self.state = self.engine.initial_state()
        self.moves = 0
        self.status = "playing"
        self.message = LEVELS[level][1]
        self.transition = None

    def snapshot(self):
        board, state = self.engine.board, self.state
        return {"level": self.level, "levels": [{"id": key, "name": value[0]} for key, value in LEVELS.items()],
                "description": LEVELS[self.level][1], "transition": self.transition,
                "rows": board.rows, "bridge_cells": board.bridge_cells,
                "state": {"cells": state.cells, "bridges": sorted(state.bridges), "split": state.split,
                          "active": state.active, "orientation": state.orientation},
                "moves": self.moves, "status": self.status, "message": self.message}

    def move(self, action):
        action = Action(action)
        if self.status != "playing":
            return
        if action == Action.SWITCH and not self.state.split:
            self.message = "Đứng trên công tắc tách để tạo hai khối con."
            return
        result, self.transition = self.engine.transition(self.state, action)
        self.moves += 1
        if result is None:
            self.status = "lost"
            self.message = ("Ô mềm đã sập, khối mất điểm tựa và rơi. Chơi lại để chọn đường khác."
                            if self.transition["failure"] == "soft" else
                            "Khối đã rơi. Chơi lại để thử một con đường khác.")
        else:
            self.state = result
            self.status = "won" if self.engine.is_goal(result) else "playing"
            self.message = ("Hoàn thành! Bạn đã đưa khối vào đích." if self.status == "won" else
                            "Space để đổi khối. Hai khối liền cạnh sẽ tự ghép." if result.split else
                            "Đưa khối đứng vào ô đích màu xanh.")


class Handler(SimpleHTTPRequestHandler):
    # Windows may register .mjs as text/plain; browsers require a JS MIME type.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mjs": "application/javascript"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def log_message(self, format, *args):
        pass

    def session(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except CookieError as error:
            raise ValueError("Invalid session cookie") from error
        token = cookies["bloxorz"].value if "bloxorz" in cookies else ""
        with self.server.sessions_lock:
            if token not in self.server.sessions:
                if len(self.server.sessions) >= 100:
                    raise ValueError("Too many game sessions; restart the server")
                token = secrets.token_urlsafe(24)
                self.server.sessions[token] = Session()
            return token, self.server.sessions[token]

    def respond(self, payload, status=200, token=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if token:
            self.send_header("Set-Cookie", f"bloxorz={token}; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/testcases":
            self.respond({"groups": TESTCASE_GROUPS})
        elif path == "/api/game":
            try:
                token, session = self.session()
                with session.lock:
                    self.respond(session.snapshot(), token=token)
            except ValueError as error:
                self.respond({"error": str(error)}, 400)
        else:
            super().do_GET()

    def do_POST(self):
        origin = self.headers.get("Origin")
        expected = f"http://{self.headers.get('Host')}"
        if origin and origin != expected:
            self.respond({"error": "Cross-origin requests are not allowed"}, 403)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 1024:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Expected JSON object")
            token, session = self.session()
            with session.lock:
                path = urlsplit(self.path).path
                if path == "/api/reset":
                    session.reset(data.get("level", session.level))
                elif path == "/api/move":
                    session.move(data.get("action"))
                elif path == "/api/testcase":
                    level = data.get("level")
                    if not isinstance(level, str) or level not in TESTCASE_IDS:
                        raise ValueError("Unknown testcase")
                    engine = Engine(BOARDS[level])
                    result = solve(engine, engine.initial_state(), data.get("algorithm"))
                    self.respond({"result": result}, token=token)
                    return
                elif path == "/api/solve":
                    if session.status == "lost":
                        raise ValueError("Restart before solving")
                    result = solve(session.engine, session.state, data.get("algorithm"))
                    self.respond({"result": result}, token=token)
                    return
                else:
                    self.respond({"error": "Unknown endpoint"}, 404)
                    return
                self.respond(session.snapshot(), token=token)
        except (ValueError, TypeError) as error:
            self.respond({"error": str(error)}, 400)


def create_server(port=8000):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.sessions = {}
    server.sessions_lock = Lock()
    server.daemon_threads = True
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    server = create_server(args.port)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Bloxorz 3D: {url}", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
