import paramiko
import os

class SFTPClient:
    def __init__(self, hostname, port, username, password, remote_directory, local_directory):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.remote_directory = remote_directory
        self.local_directory = local_directory
        self.sftp = None
        self.transport = None

    def connect(self):
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def list_files(self):
        files = self.sftp.listdir(self.remote_directory)
        return [file for file in files if file.endswith('.txt') or file.endswith('.pdf')]

    def download_files(self, files):
        for file in files:
            remote_path = os.path.join(self.remote_directory, file)
            local_path = os.path.join(self.local_directory, file)
            self.sftp.get(remote_path, local_path)
            print(f'Downloaded: {file}')

    def close(self):
        self.sftp.close()
        self.transport.close()

