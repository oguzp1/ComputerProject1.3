from xmlrpc.client import ServerProxy

if __name__ == '__main__':
    proxy = ServerProxy('http://localhost:8080')
    for name in proxy.get_filenames(1, ''):
        print(name)