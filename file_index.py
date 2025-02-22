import yaml
import argparse
from lib.engine import Engine
from lib.index import index_text,index_pdf


def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Doc Indexer')
    parser.add_argument('--title', help="Title of the document. If empty filename=title with textfile.", required=False)
    parser.add_argument('--path', help="Path to file", required=True)
    return parser.parse_args()

if __name__=="__main__":
    with open('conf/config.yaml', 'r') as file:
         config = yaml.safe_load(file)
    args = parse_args()
    e = Engine({"index_dir": config['whoosh_index_dir']})
    if args.path.endswith('.pdf'):
        index_pdf(e, args.path, args.title)
    else:
        index_text(e, args.path, args.title)
