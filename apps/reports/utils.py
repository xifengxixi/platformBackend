

def get_file_contents(filename, chunk_size=512):
    with open(filename, encoding='utf-8') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break