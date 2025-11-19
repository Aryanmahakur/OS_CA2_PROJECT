#!/usr/bin/env python3
import socket
import os
import signal
import sys
import random
import time

SOCKET_PATH = "/tmp/secure_auth_otp.sock"

OTP = None
OTP_EXPIRY = 0

def generate_otp():
    global OTP, OTP_EXPIRY
    OTP = str(random.randint(100000, 999999))
    OTP_EXPIRY = time.time() + 60  # valid for 60 seconds
    print(f"[OTP Server] Generated OTP: {OTP}")
    return OTP

def cleanup(*args):
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    print("\nOTP Server stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
os.chmod(SOCKET_PATH, 0o600)
server.listen(1)

print("OTP server started...")
print(f"Listening at {SOCKET_PATH}")

generate_otp() 

while True:
    conn, _ = server.accept()
    data = conn.recv(1024).decode().strip()

    if data == "GET_OTP":
        otp = generate_otp()
        conn.sendall(otp.encode() + b"\n")

    elif data.startswith("VERIFY:"):
        user_otp = data.split("VERIFY:")[1]

        if time.time() > OTP_EXPIRY:
            conn.sendall(b"EXPIRED\n")
        elif user_otp == OTP:
            conn.sendall(b"OK\n")
        else:
            conn.sendall(b"FAIL\n")

    conn.close()
