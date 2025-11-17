import sys
from client import TaskClient
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QApplication, QPushButton,QHBoxLayout, QListWidget, QRadioButton, QListWidgetItem,QCheckBox, QLabel, QMessageBox)

client = TaskClient()


class TaskWidget(QWidget):
    def __init__(self, text, priority, completed=False, index=None):
        super().__init__()
        self.text = text
        self.priority = priority
        self.completed = completed
        self.index = index  

        layout = QHBoxLayout(self)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.update_style)


        if self.completed:
            self.label.setStyleSheet("color: gray; text-decoration: line-through;")
            self.checkbox.setChecked(True)
        else:
            self.apply_priority_style()

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

    def apply_priority_style(self):
        colors = {
            "high": "red",
            "medium": "orange",
            "low": "green"
        }
        color = colors.get(self.priority, "black")
        self.label.setStyleSheet(f"color: {color}; font-weight: bold")

    def update_style(self, state):
        self.completed = state == 2
        if self.completed:
            self.label.setStyleSheet("color: gray; text-decoration: line-through;")
        else:
            self.apply_priority_style()


        if self.index is not None:
            client_request = {
                "action": "update",
                "completed": self.completed,
                "index": self.index
            }
            client.send_command(client_request)


class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")

        layout = QVBoxLayout(self)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите задачу...")

        self.tasks_list = QListWidget()

        buttons_layout = QHBoxLayout()

        add_button = QPushButton("Добавить задачу")
        delete_button = QPushButton("Удалить выбранную задачу")
        clear_completed_task = QPushButton("Удалить все выполненные")

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(clear_completed_task)

        priority_layout = QHBoxLayout()

        self.low_priority = QRadioButton("Низкий")
        self.medium_priority = QRadioButton("Средний")
        self.high_priority = QRadioButton("Высокий")

        self.medium_priority.setChecked(True)

        priority_layout.addWidget(self.low_priority)
        priority_layout.addWidget(self.medium_priority)
        priority_layout.addWidget(self.high_priority)
        priority_layout.addStretch()

        layout.addWidget(self.task_input)
        layout.addLayout(priority_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.tasks_list)

        add_button.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
        delete_button.clicked.connect(self.delete_task)
        clear_completed_task.clicked.connect(self.delete_completed_task)

        self.update_gui_timer = QTimer()
        self.update_gui_timer.timeout.connect(self.update_gui)
        self.update_gui_timer.start(1000)

    def get_priority(self):
        if self.high_priority.isChecked():
            return "high"
        elif self.low_priority.isChecked():
            return "low"
        return "medium"

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            priority = self.get_priority()

            client_request = {
                "action": "add",
                "text": text,
                "priority": priority
            }
            client.send_command(client_request)

            self.task_input.clear()

    def delete_task(self):
        selected_item = self.tasks_list.currentItem()
        if selected_item:
            index = self.tasks_list.row(selected_item)

            client_request = {
                "action": "delete",
                "index": index
            }
            client.send_command(client_request)

    def delete_completed_task(self):
        completed_indices = []

        for i in range(self.tasks_list.count() - 1, -1, -1):
            item = self.tasks_list.item(i)
            widget = self.tasks_list.itemWidget(item)
            if widget and widget.completed:
                completed_indices.append(i)

        for i in completed_indices:
            client_request = {
                "action": "delete",
                "index": i
            }
            client.send_command(client_request)

        count = len(completed_indices)
        msg = "Нет выполненных задач" if count == 0 else f"Удалено {count} задач"
        QMessageBox.information(self, "Информация", msg)

    def update_gui(self):
        self.tasks_list.clear()

        for task in client.tasks:
            text = task["text"]
            priority = task.get("priority", "medium")
            completed = task.get("completed", False)
            index = task.get("index")

            task_widget = TaskWidget(text, priority, completed, index)
            item = QListWidgetItem()
            item.setSizeHint(task_widget.sizeHint())
            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, task_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    app.exec()
