import socket
import threading
import json

clients = []
clients_lock = threading.Lock()

tasks = []
tasks_lock = threading.Lock()

HOST = "localhost"
PORT = 9090

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((HOST, PORT))
server_sock.listen()
print("Сервер запущен")

def broadcast_tasks():
    data = []

    with tasks_lock:
        for i, task in enumerate(tasks):
            data.append({
                "text": task.get("text"),
                "priority": task.get("priority"),
                "completed": task.get("completed"),
                "index": i
            })

    response = json.dumps({"action": "get_tasks", "tasks": data}).encode("utf-8")

    with clients_lock:
        not_working = []
        for client in clients:
            try:
                client.sendall(response)
            except:
                not_working.append(client)

        for con in not_working:
            clients.remove(con)


def handle_client(client_sock, addr):
    print(f"Подключение клиента {addr}")
    broadcast_tasks()

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                print(f"Отключение клиента {addr}")
                break

            msg = json.loads(data.decode("utf-8"))
            action = msg.get("action")

            if action == "add":
                text = msg.get("text")
                priority = msg.get("priority")
                with tasks_lock:
                    tasks.append({
                        "text": text,
                        "priority": priority,
                        "completed": False
                    })
                broadcast_tasks()

            elif action == "delete":
                index = msg.get("index")
                with tasks_lock:
                    del tasks[index]
                broadcast_tasks()


            elif action == "update":
                index = msg.get("index")
                completed = msg.get("completed")
                with tasks_lock:
                        tasks[index]["completed"] = bool(completed)
                broadcast_tasks()

    finally:
        with clients_lock:
            if client_sock in clients:
                clients.remove(client_sock)
        client_sock.close()
        print(f"Закрыто соединение клиента {addr}")


while True:
    client_sock, addr = server_sock.accept()
    with clients_lock:
        clients.append(client_sock)



    potok = threading.Thread(target=handle_client, args=(client_sock, addr))
    potok.start()