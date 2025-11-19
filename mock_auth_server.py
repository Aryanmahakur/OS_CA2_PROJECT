#!/usr/bin/env python3
"""
mock_auth_server.py
A simple test server implementing a tiny socket protocol:
- Listens on UNIX socket path (same as GUI)
- Reads a password line, compares to TEST_PASSWORD, replies "OK\n" or "FAIL\n"
This is for Phase 1 testing only.
"""

import os
import socket
import sys
import signal

SOCKET_PATH = "/tmp/secure_auth_test.sock"
TEST_PASSWORD = "password123"  # change this to test different behaviors

def cleanup_and_exit(signum, frame):
    try:
        os.unlink(SOCKET_PATH)
    except FileNotFoundError:
        pass
    print("\nServer stopped.")
    sys.exit(0)

def run_server():
    # Clean up any stale socket
    try:
        os.unlink(SOCKET_PATH)
    except FileNotFoundError:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    # Restrict access to your user only (for testing)
    os.chmod(SOCKET_PATH, 0o600)
    server.listen(5)
    print(f"Mock auth server listening on {SOCKET_PATH}")
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    try:
        while True:
            conn, _ = server.accept()
            with conn:
                # read until newline
                data = b""
                while not data.endswith(b"\n"):
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                password = data.decode("utf-8").strip()
                print(f"Received password attempt: {password!r}")
                if password == TEST_PASSWORD:
                    conn.sendall(b"OK\n")
                else:
                    conn.sendall(b"FAIL\n")
    finally:
        cleanup_and_exit(None, None)

if __name__ == "__main__":
    run_server()
