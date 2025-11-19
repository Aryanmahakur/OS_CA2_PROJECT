#!/usr/bin/env python3
"""
email_otp_server.py
OTP backend that sends OTP to configured email via Gmail SMTP (App Password).
Socket protocol (UNIX socket):
- Client sends "GET_OTP" -> server generates OTP, sends email, replies "SENT\n"
- Client sends "VERIFY:<otp>" -> server replies "OK\n", "FAIL\n" or "EXPIRED\n"
"""

import socket, os, signal, sys, random, time
import smtplib
from email.message import EmailMessage

SOCKET_PATH = "/tmp/secure_auth_otp.sock"
OTP = None
OTP_EXPIRY = 0
OTP_TTL = 60  # seconds
LAST_SENT = 0
RESEND_COOLDOWN = 5  # seconds between generate requests

# load config from ~/.secure-auth/email.conf
def load_config(path=os.path.expanduser("~/.secure-auth/email.conf")):
    cfg = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#"): continue
            if "=" not in line: continue
            k,v = line.split("=",1)
            cfg[k.strip()] = v.strip()
    return cfg

def send_email(smtp_user, smtp_pass, to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{smtp_user}"
    msg["To"] = to_email
    msg.set_content(body)

    # Gmail SMTP over SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

def generate_otp():
    global OTP, OTP_EXPIRY, LAST_SENT
    now = time.time()
    if now - LAST_SENT < RESEND_COOLDOWN:
        # avoid hammering; still generate new OTP but respect cooldown
        pass
    OTP = f"{random.randint(100000, 999999):06d}"
    OTP_EXPIRY = time.time() + OTP_TTL
    LAST_SENT = time.time()
    return OTP

def cleanup(*args):
    try:
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
    except Exception:
        pass
    print("\nOTP Email Server stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# --- start server ---
try:
    cfg = load_config()
    SMTP_USER = cfg["SMTP_USER"]
    SMTP_PASSWORD = cfg["SMTP_PASSWORD"]
    TO_EMAIL = cfg.get("TO_EMAIL", SMTP_USER)
    FROM_NAME = cfg.get("FROM_NAME", SMTP_USER)
except Exception as e:
    print("Failed to load email config:", e)
    print("Create config at ~/.secure-auth/email.conf (see README). Exiting.")
    sys.exit(1)

# remove stale socket
if os.path.exists(SOCKET_PATH):
    try: os.remove(SOCKET_PATH)
    except: pass

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
os.chmod(SOCKET_PATH, 0o600)
server.listen(5)
print("Email OTP server started. Listening on", SOCKET_PATH)

# For debugging: print when OTP is generated (you may remove this in production)
DEBUG_PRINT_OTP = False

while True:
    try:
        conn, _ = server.accept()
    except KeyboardInterrupt:
        break
    with conn:
        try:
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
            msg = data.decode().strip()
            if not msg:
                continue

            if msg == "GET_OTP":
                otp = generate_otp()
                body = f"Your SecureAuth OTP is: {otp}\nThis code is valid for {OTP_TTL} seconds."
                subject = "Your SecureAuth OTP code"
                try:
                    send_email(SMTP_USER, SMTP_PASSWORD, TO_EMAIL, subject, body)
                    # reply to client
                    conn.sendall(b"SENT\n")
                    if DEBUG_PRINT_OTP:
                        print("[DEBUG] Sent OTP:", otp)
                except Exception as e:
                    print("Error sending email:", e)
                    conn.sendall(b"ERROR\n")

            elif msg.startswith("VERIFY:"):
                user_otp = msg.split("VERIFY:",1)[1].strip()
                if OTP is None:
                    conn.sendall(b"FAIL\n")
                elif time.time() > OTP_EXPIRY:
                    conn.sendall(b"EXPIRED\n")
                elif user_otp == OTP:
                    # Invalidate OTP immediately after success
                    OTP = None
                    OTP_EXPIRY = 0
                    conn.sendall(b"OK\n")
                else:
                    conn.sendall(b"FAIL\n")
            else:
                conn.sendall(b"UNKNOWN\n")
        except Exception as e:
            # avoid server crash on malformed client
            print("Server error:", e)
            try:
                conn.sendall(b"ERROR\n")
            except:
                pass

# cleanup on exit
cleanup()
