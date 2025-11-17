import socket
import threading
import json

HOST = "localhost"
PORT = 9090

class TaskClient:
    def __init__(self):
        self.tasks = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        server_listener_thread = threading.Thread(target=self.listen_server)
        server_listener_thread.start()

    def listen_server(self):
        while True:
            try:
                server_response = self.sock.recv(4096).decode("utf-8")
                if not server_response:
                    print("Разорвано соединение с сервером")
                    break

                data = json.loads(server_response)
                action = data["action"]

                if action == "get_tasks":
                    self.tasks = data["tasks"]

            except Exception as e:
                print("Ошибка:", e)
                break

    def send_command(self, command):
        try:
            client_request = json.dumps(command)
            self.sock.send(client_request.encode("utf-8"))
        except (ConnectionResetError, BrokenPipeError):
            print("Разорвано соединение с сервером")
