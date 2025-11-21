

 SecureAuth – Multi-Factor Authentication System for Ubuntu

A custom-built MFA system that adds an additional layer of security after Ubuntu login.

---

 **Overview**

SecureAuth is a custom-built **Multi-Factor Authentication (MFA)** system for Ubuntu.
It adds an additional security layer *after the normal Ubuntu login* by requiring:

* **Password Authentication (PyQt5 GUI)**
* **Email OTP Verification (Gmail SMTP)**

Until both steps are verified, the user **cannot access the Ubuntu desktop**.

The system automatically launches at login using **GNOME Autostart** and the backend runs using **systemd user services**.

---

 **Features**

* ✔ Full-screen password authentication GUI
* ✔ Email-based One-Time Password (OTP)
* ✔ Python backend servers using UNIX sockets
* ✔ Automatic launch at Ubuntu login
* ✔ Secure Gmail App Password configuration
* ✔ OTP valid for 60 seconds
* ✔ OTP server with logging and retries
* ✔ Works on Wayland + GNOME
* ✔ Modular architecture (easy to extend)

---

**Project Structure**

```
secure-auth/
│
├── gui/
│   ├── auth_gui.py            # Password GUI
│   └── otp_gui.py             # OTP GUI
│
├── server/
│   ├── mock_server.py         # Password backend
│   └── email_otp_server.py    # OTP backend
│
├── config/
│   └── email.conf (stored in ~/.secure-auth/)
│
└── autostart/
    └── secure-auth-gui.desktop
```

---

 **Steps to Start the Servers**

**1️⃣ Start Password Server**

```bash
systemctl --user start secure-auth-backend.service
```

**Start OTP Server**

```bash
systemctl --user start secure-auth-otp.service
```

---

  **How It Works**

1. User logs into Ubuntu normally.
2. GNOME Autostart launches **auth_gui.py** (Password GUI).
3. Password is sent to backend through:

   ```
   /tmp/secure_auth.sock
   ```
4. If password is correct → OTP GUI opens.
5. OTP GUI requests a new OTP via:

   ```
   /tmp/secure_auth_otp.sock
   ```
6. Backend emails OTP using Gmail SMTP.
7. User enters OTP → If valid → Desktop unlocks.

---

**Future Scope**

* PAM Integration (real Ubuntu password validation)
* TOTP apps (Google Authenticator / Authy)
* Biometric authentication (Fingerprint, Face ID)
* Hardware Security Keys (YubiKey, FIDO2)
* Push notification–based MFA
* Admin web dashboard

---


