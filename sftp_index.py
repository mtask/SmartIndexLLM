from lib.sftp_get import SFTPClient
from lib.engine import Engine
from lib.index import index_text,index_pdf
from pathlib import Path
import os
import yaml


if __name__=="__main__":
    with open('conf/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    for con in config['sftp']:
        sftp_client = SFTPClient(con['hostname'], con['port'], con['username'], con['password'], con['remote_directory'], con['local_directory'])
        Path(sftp_client.local_directory).mkdir(parents=True, exist_ok=True)
        sftp_client.connect()
        file_list = sftp_client.list_files()
        sftp_client.download_files(file_list)
        sftp_client.close()
    e = Engine({"index_dir": config['whoosh_index_dir']})
    for fname in file_list:
        file_to_index = os.path.join(con['local_directory'], fname)
        if fname.lower().endswith('.txt'):
            index_text(e, file_to_index, fname)
        elif fname.lower().endswith('.pdf'):
            index_pdf(e, file_to_index, fname)
