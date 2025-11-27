

import sys
import socket
import os
from PyQt5 import QtWidgets, QtCore

SOCKET_PATH = "/tmp/secure_auth_test.sock"  # test socket (change for production)

class PasswordWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setWindowTitle("Secure Sign-In — Password")
        self.setFixedSize(420, 180)

    def init_ui(self):F
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Enter your system password")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.returnPressed.connect(self.on_submit)
        layout.addWidget(self.password_edit)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label)

        btn_layout = QtWidgets.QHBoxLayout()
        self.submit_btn = QtWidgets.QPushButton("Sign In")
        self.submit_btn.clicked.connect(self.on_submit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def on_submit(self):
        pw = self.password_edit.text()
        self.set_ui_enabled(False)
        self.status_label.setText("Verifying…")
        QtCore.QCoreApplication.processEvents()

        try:
            resp = send_password_over_socket(pw)
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            self.set_ui_enabled(True)
            return

        if resp == "OK":
            self.status_label.setText("Password correct — proceeding to OTP stage (mock).")
            QtCore.QTimer.singleShot(1000, self.close)  # close after 1s (simulate proceed)
        else:
            self.status_label.setText("Incorrect password. Try again.")
            self.password_edit.clear()
            self.set_ui_enabled(True)

    def set_ui_enabled(self, enabled: bool):
        self.submit_btn.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)

def send_password_over_socket(password: str, timeout=5.0) -> str:
   
    if not os.path.exists(SOCKET_PATH):
        raise FileNotFoundError(f"Socket not present: {SOCKET_PATH}")

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(SOCKET_PATH)
        # Ensure we send bytes. We add newline delimiter.
        client.sendall((password + "\n").encode("utf-8"))
        # read response (single line)
        data = b""
        while not data.endswith(b"\n"):
            chunk = client.recv(1024)
            if not chunk:
                break
            data += chunk
        resp = data.decode("utf-8").strip()
        return resp
    finally:
        client.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = PasswordWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
