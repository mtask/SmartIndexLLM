import string
import re
import os
import subprocess
import sys
import argparse
import yaml
from lib.engine import Engine

def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Doc Indexer')
    parser.add_argument('-c', help="Path to yaml config file", required=True)
    parser.add_argument('--model', default="llama3.2:3b", help="LLM to use (default 'llama3.2:3b')", required=False)
    parser.add_argument('--whoosh_query', help="Whoosh query to search context for prompt", required=True)
    parser.add_argument('--ollama_prompt', help="Ollama prompt that is combined with context", required=True)
    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    with open('conf/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    e = Engine({"index_dir": config['whoosh_index_dir']})

    engine = Engine({"index_dir": "whoosh_doc_index"}, model=args.model)
    response = engine.generate_response(query=args.whoosh_query, prompt=args.ollama_prompt)
    print(response)
