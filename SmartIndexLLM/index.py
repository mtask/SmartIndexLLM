from lib.sftp_get import SFTPClient
from lib.engine import Engine, schema_builder
from lib.index import index_text,index_pdf
from pathlib import Path
from bs4 import BeautifulSoup
import tempfile
import requests
import os
import yaml
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Indexer')
    parser.add_argument('-c', help="Path to yaml config file", required=True, metavar="YAML")
    return parser.parse_args()

def sftp_index(config, e):
    """
    Get txt and pdf files over SFTP and index locally
    """
    print("####### Starting SFTP indexing #######")
    for con in config['sftp']:
        sftp_client = SFTPClient(con['hostname'], con['port'], con['username'], os.path.expanduser(con['private_key']), con['remote_directory'], con['local_directory'])
        Path(sftp_client.local_directory).mkdir(parents=True, exist_ok=True)
        sftp_client.connect()
        file_list = sftp_client.list_files()
        sftp_client.download_files(file_list)
        sftp_client.close()
    for fname in file_list:
        file_to_index = os.path.join(con['local_directory'], fname)
        if fname.lower().endswith('.txt'):
            index_text(e, file_to_index, fname)
        elif fname.lower().endswith('.pdf'):
            index_pdf(e, file_to_index, fname)

def local_file_index(config, e):
    """
    index local files
    """
    print("####### Starting local file indexing #######")
    for i in config['local_file']:
        if i['path'].endswith('.pdf'):
            index_pdf(e, i['path'], i['title'])
    else:
        index_text(e, i['path'], i['title'])

def web_index(config, e):
    """
    Index web content
    """
    print("####### Starting web data indexing #######")

    for con in config['web']:
        content = []
        r = requests.get(con['url'])
        content_lines = BeautifulSoup(r.text, 'html.parser').get_text().strip().split('\n')
        for line in content_lines:
            if line.strip() == '':
                continue
            content.append(line.strip())
        content = '\n'.join(content)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(content.encode('UTF-8'))
        index_text(e, temp_file.name, con['url'])
        os.unlink(temp_file.name)

def rss_index(config, e):
    """
    Index rss content
    """
    print("####### Starting RSS feed indexing #######")


if __name__=="__main__":
    args = parse_args()
    with open(args.c, 'r') as file:
        config = yaml.safe_load(file)
    # Get index settings
    index_schema = schema_builder(config['whoosh_index']['schema'])
    index_dir = config['whoosh_index']['dir']
    e = Engine(index_dir, schema=index_schema)
    # Index data
    if len(config['sftp']) > 0:
        sftp_index(config, e)
    if len(config['local_file']) > 0:
        local_file_index(config, e)
    if len(config['web']) > 0:
        web_index(config, e)
    if len(config['rss']) > 0:
        rss_index(config, e)
