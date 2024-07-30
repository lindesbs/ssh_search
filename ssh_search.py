#!/bin/env python
import glob
import subprocess
import sys
import os
import paramiko
import yaml
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLineEdit, QListWidget, QListWidgetItem


def read_ssh_config():
    ssh_config_path = os.path.expanduser("~/.ssh/config")
    ssh_config = paramiko.SSHConfig()

    def parse_config_file(file_path):
        with open(file_path) as f:
            print(file_path)
            ssh_config.parse(f)

        with open(file_path) as f:
            for line in f:
                if line.strip().startswith('Include'):
                    _, included_path = line.split(None, 1)
                    included_path = "~/.ssh/" + included_path.strip()
                    included_path = os.path.expanduser(included_path)

                    for include_file in glob.glob(included_path):
                        parse_config_file(include_file)

    parse_config_file(ssh_config_path)
    return [host for host in ssh_config.get_hostnames() if host != '*']


def read_config():
    config_path = os.path.expanduser("~/.ssh_search.yaml")

    if not os.path.isfile(config_path):
        initial_data = 'terminal: "gnome-terminal -- ssh {host}"'
        print(initial_data, file=open(config_path, 'w'))

    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


class SSHConfigSearch(QWidget):
    def __init__(self):
        super().__init__()

        self.hosts = read_ssh_config()
        self.config = read_config()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('SSH Config Search')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText('Search hosts...')
        self.search_box.textChanged[str].connect(self.search_hosts)
        layout.addWidget(self.search_box)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        self.list_widget.itemDoubleClicked.connect(self.connect_to_host)
        self.list_widget.itemActivated.connect(self.connect_to_host)

        self.setLayout(layout)

        self.update_listbox(self.hosts)

    def search_hosts(self):
        query = self.search_box.text().lower()
        filtered_hosts = [host for host in self.hosts if query in host.lower()]
        self.update_listbox(filtered_hosts)

    def update_listbox(self, host_list):
        self.list_widget.clear()
        for host in host_list:
            QListWidgetItem(host, self.list_widget)

    def connect_to_host(self, item):
        host = item.text()
        terminal_command = self.config['terminal'].format(host=host)
        subprocess.run(terminal_command, shell=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SSHConfigSearch()
    window.show()
    sys.exit(app.exec_())
