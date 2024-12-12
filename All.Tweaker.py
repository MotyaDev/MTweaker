from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, 
    QCheckBox, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit, 
    QScrollArea, QLabel, QFrame, QGridLayout, QProgressBar)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QFont
import sys
import configparser
import os
import subprocess
import getpass
from datetime import datetime

# Создаем конфигурационный файл
config = configparser.ConfigParser()
config.read('settings.ini')

sys.path.insert(0, './tweaks')

from tabs import tabs

class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal()
    status = Signal(str)

    def __init__(self, checkboxes):
        super().__init__()
        self.checkboxes = checkboxes
        self.is_running = True

    def run(self):
        total_tasks = sum(sum(1 for checkbox in tab_checkboxes.values() if checkbox.isChecked())
                         for tab_checkboxes in self.checkboxes.values())
        completed_tasks = 0

        for tab_name, tab_checkboxes in self.checkboxes.items():
            if not self.is_running:
                break
                
            for checkbox_name, checkbox in tab_checkboxes.items():
                if not self.is_running:
                    break
                    
                if checkbox.isChecked():
                    self.status.emit(f"Выполняется: {checkbox_name}")
                    
                    if checkbox_name.endswith(".bat"):
                        subprocess.call(f'tweaks\\"{tab_name}\\{checkbox_name}"', shell=True)
                    elif checkbox_name.endswith(".ps1"):
                        subprocess.run(['Utils\\launcher.exe', 
                                      f'powershell.exe -ExecutionPolicy Bypass -File tweaks\\"{tab_name}\\{checkbox_name}"'])
                    elif checkbox_name.endswith(".reg"):
                        subprocess.call(f'Utils\\PowerRun.exe tweaks\\"{tab_name}\\{checkbox_name}"', shell=True)
                    else:
                        subprocess.call(f'tweaks\\"{tab_name}\\{checkbox_name}"', shell=True)
                    
                    completed_tasks += 1
                    progress = int((completed_tasks / total_tasks) * 100)
                    self.progress.emit(progress)

        self.finished.emit()

    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Moti Tweaker Beta')
        
        # Основной виджет и layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Кнопка выполнить
        self.execute_button = QPushButton('Выполнить')
        self.execute_button.clicked.connect(self.execute)
        self.main_layout.addWidget(self.execute_button)
        
        # Поле поиска
        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.update_checkboxes)
        self.main_layout.addWidget(self.search_entry)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Создание вкладок
        self.checkboxes = {}
        for tab_name, checkbox_names in tabs.items():
            scroll = QScrollArea()
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setSpacing(2)  # Уменьшаем отступ между элементами
            
            # Добавляем кнопку "Выделить всё"
            select_all_btn = QPushButton('Выделить всё')
            select_all_btn.clicked.connect(lambda checked, t=tab_name: self.select_all_in_tab(t))
            tab_layout.addWidget(select_all_btn)
            
            # Контейнер для чекбоксов
            checkbox_widget = QWidget()
            grid = QGridLayout(checkbox_widget)
            grid.setSpacing(2)  # Уменьшаем отступ между чекбоксами
            
            # Выбор количества колонок
            num_columns = 2
            if tab_name == 'База':
                num_columns = 4
            elif tab_name in ['Обновления', 'Поддержка']:
                num_columns = 1
            elif tab_name == 'Программы':
                num_columns = 3
                
            # Создание чекбоксов
            self.checkboxes[tab_name] = {}  # Словарь для чекбоксов текущей вкладки
            for i, checkbox_name in enumerate(checkbox_names):
                checkbox = QCheckBox(checkbox_name)
                grid.addWidget(checkbox, i // num_columns + 1, i % num_columns)
                self.checkboxes[tab_name][checkbox_name] = checkbox
                
            tab_layout.addWidget(checkbox_widget)
            scroll.setWidget(tab_widget)
            scroll.setWidgetResizable(True)
            self.tab_widget.addTab(scroll, tab_name)
        
        # Добавляем прогресс-бар и статус
        status_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        status_layout.addWidget(self.status_label)
        
        # Кнопка отмены
        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.cancel_execution)
        status_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(status_layout)
        
        self.worker = None

    def execute(self):
        if self.worker and self.worker.isRunning():
            return

        self.execute_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.cancel_button.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = WorkerThread(self.checkboxes)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.on_execution_finished)
        self.worker.start()

    def cancel_execution(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.on_execution_finished()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, text):
        self.status_label.setText(text)

    def on_execution_finished(self):
        self.execute_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.cancel_button.setVisible(False)
        self.status_label.clear()

    def update_checkboxes(self):
        search_text = self.search_entry.text().lower()
        for checkbox_name, checkbox in self.checkboxes.items():
            checkbox.setVisible(search_text in checkbox_name.lower())

    def get_tab_name(self, checkbox_name):
        for tab_name, checkbox_names in tabs.items():
            if checkbox_name in checkbox_names:
                return tab_name
        return None  # return None if the checkbox name is not found in any tab

    def select_all_in_tab(self, tab_name):
        """Выделяет или снимает выделение со всех чекбоксов в указанной вкладке"""
        # Определяем текущее состояние (если хоть один не отмечен - будем отмечать все)
        any_unchecked = any(not checkbox.isChecked() 
                           for checkbox in self.checkboxes[tab_name].values())
        
        # Устанавливаем новое состояние для всех чекбоксов
        for checkbox in self.checkboxes[tab_name].values():
            checkbox.setChecked(any_unchecked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
