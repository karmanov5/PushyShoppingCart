from datetime import datetime


class logs:

    @staticmethod
    def d(*args):
        log = f"INFO {datetime.now()}: {' '.join([str(a) for a in args]) }\n"
        print(log)
        with open("logs.txt", "a", encoding='utf-8') as file:
            file.write(log)
    
    @staticmethod
    def error(*args):
        log = f"ERROR {datetime.now()}: {' '.join([str(a) for a in args])}\n"
        print(log)
        with open("logs.txt", "a", encoding='utf-8') as file:
            file.write(log)