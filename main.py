from server import server

def main():
    s = server(4668)
    s.start()


if __name__ == '__main__':
    main()