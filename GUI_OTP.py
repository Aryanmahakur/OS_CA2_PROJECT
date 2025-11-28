#!/usr/bin/env python3
import socket
import os
import sys

SOCKET_PATH = "/tmp/secure_auth_otp.sock"

def send_to_otp_server(message):
    if not os.path.exists(SOCKET_PATH):
        return "ERROR"

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(message.encode() + b"\n")
    response = client.recv(1024).decode().strip()
    client.close()D
    return response

class OTPWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Secure Login - OTP")
        self.resize(350, 150)

        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Enter the 6-digit OTP")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        self.otp_box = QtWidgets.QLineEdit()
        self.otp_box.setMaxLength(6)
        layout.addWidget(self.otp_box)

        self.status = QtWidgets.QLabel("")
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status)

        verify_btn = QtWidgets.QPushButton("Verify OTP")
        verify_btn.clicked.connect(self.verify_otp)
        layout.addWidget(verify_btn)

        generate_btn = QtWidgets.QPushButton("Resend OTP")
        generate_btn.clicked.connect(self.resend_otp)
        layout.addWidget(generate_btn)

        self.setLayout(layout)

    def verify_otp(self):
        otp = self.otp_box.text()
        resp = send_to_otp_server(f"VERIFY:{otp}")

        if resp == "OK":
            self.status.setText("OTP Correct!")
        elif resp == "FAIL":
            self.status.setText("Wrong OTP!")
        elif resp == "EXPIRED":
            self.status.setText("OTP Expired!")
        else:
            self.status.setText("Server Not Running!")

    def resend_otp(self):
        resp = send_to_otp_server("GET_OTP")
        if resp == "ERROR":
            self.status.setText("Server not running!")
        else:
            self.status.setText(f"New OTP Sent (check server console)")

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = OTPWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
s