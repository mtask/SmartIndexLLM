TODO: ssh key type detection

## Indexing

There's multiple scripts for different indexing use cases.
Indexing supports PDF or TXT files based on extension `.txt` and `.pdf`.

### File

`x`

### SFTP

Configure SFTP instances where to copy files. One per remote path even if all remote paths are in the same server.

```yaml
sftp:
  - hostname: '127.0.0.1'
    port: 22
    username: user
    # currently only ed25519 key is supported
    private_key: ~/.ssh/id_ed25519
    # Copy TXT of PDF files from here...
    remote_directory: /opt/dokuwiki/config/
    # ...to this directory. Files are then read and indexed from this local path.
    local_directory: data/wikipages
  - hostname: and so on
    ...
```

Then launch indexing.

```bash
python3 sftp_index.py -c path/to/config/file.yaml
```


### Web

Configure web paths

`x

### RSS

`x`

## Searching

```bash
$ python3 search_prompt.py --whoosh_query 'cert*'  --ollama_prompt "How do I renew certificate in my homelab?" --model myllama3.2_3b
```

## Prompt LLM via Ollama and provide context from Whoosh search

```bash
$ python3 search_prompt.py --whoosh_query 'LED' --ollama_prompt 'How can LED lights be used in cyber attack?'
```

## Debugging

You can use the provided test script to query the index.


```bash
$ python3 tests/search.py 'xyz and (foo or bar)'
```

Or you can dump the whole index.

```bash
$ python3 tests/dump_index.py
```
