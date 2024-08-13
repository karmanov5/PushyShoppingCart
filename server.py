import socket, time
from client import client
from threading import Thread
from logs import logs
import json, os
from pushy import PushyAPI
from product import product, productEncoder

class server:

    __products = []
    __clients = []
    __categories = []


    def __init__(self, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.socket.bind((self.address, self.port))
        self.__working = True
        self.__load_products()
        self.__load_categories()

    def start(self):
        t = Thread(target=self.__process_server, args=())
        t.start()
        self.__working = True    

    def __load_products(self):
        self.__products = []
        if os.path.exists('products.json'):
            with open("products.json", 'r', encoding='utf-8') as file:
                self.__products = json.load(file, object_hook=lambda obj: product(id=obj['Id'],
                                                                                    name=obj['Name'],
                                                                                    price=obj['Price'],
                                                                                    count=obj['Count'],
                                                                                    isWeight=obj['IsWeight'],
                                                                                    completed=obj['Completed'],
                                                                                    category=obj['Category']))
    def __save_products(self):
        with open('products.json', 'w', encoding='utf-8') as file:
            json.dump(self.__products, file, cls=productEncoder, indent=4)

    def __load_categories(self):
        self.__categories = ['Стандартные', 'Завершенные']
        if os.path.exists("categories.json"):
            with open("categories.json", 'r', encoding='utf-8') as file:
                self.__categories = json.load(file)
                self.__categories.append('Завершенные')

    def __save_categories(self):
        with open('categories.json', 'w', encoding='utf-8') as file:
            json.dump(self.__categories, file, indent=4)
    

    def __process_server(self):
        try:
            self.socket.listen()
            logs.d("server start on", self.address, ":", self.port)
            while self.__working:
                cl, _ = self.socket.accept()
                logs.d("new client", cl.getpeername())
                Thread(target=self.__test_client, args=(cl,)).start()
        except Exception as ex:
            logs.error("failed start server! Exception:", str(ex))

    

    def __test_client(self, cl: socket.socket):
        try:
            data = cl.recv(1024)
            if not data:
                logs.error("client", cl.getpeername(), "not responding!")
                raise Exception("client not responding!")
            json_data = json.loads(data.decode('utf-8'))
            if "name" not in json_data:
                logs.error("wrong answer from client", cl.getpeername())
                raise Exception("wrong answer from client!")
            else:
                name = json_data['name']
                id = json_data['id']

                send_data = dict(event="get_products")
                send_data['products'] = self.__products
                send_data['categories'] = self.__categories
                PushyAPI.sendPushNotification(title="", message="", data=json.dumps(dict(data=send_data), ensure_ascii=False, indent=4, cls=productEncoder), to=id, options=None)

                for _cl in self.__clients:
                    if _cl.name == name and _cl.id == id:
                        try:
                            _cl.socket.close()
                        except: pass
                        _cl.socket = cl
                        logs.d("reconnect person:", _cl.socket.getpeername(), "name:", name)
                        self.__process_client(_cl)
                        break
                else:
                    p = client(id, name, cl)
                    self.__clients.append(p)
                    logs.d("new person", cl.getpeername(), "name:", name)
                    self.__process_client(p)
                    


        except Exception as ex:
            logs.error("disconnect client", cl.getpeername(), "Подробно:", str(ex))
            cl.close()
    
    def __process_client(self, client: client):
        try:
            while True:
                data = client.socket.recv(1024)
                if not data:
                    break
                self.__process_json_data(data.decode('utf-8'), client)
            raise Exception('client', client.socket.getpeername(), 'not responding!')
        except Exception as ex:
            logs.error(str(ex), "socket close!")
    

    def __process_json_data(self, data: str, client: client):
        json_data = json.loads(data)
        logs.d(json_data, 'from', client.name)
        command = json_data['command']
        send_data = dict(event=command)
        title, message = "", ""
        if command == 'add_product':
            _product = json_data['data']
            p = product(id=_product['Id'], name=_product['Name'], price=_product['Price'], count=_product['Count'], isWeight=_product['IsWeight'], completed=_product['Completed'], category=_product['Category'] )
            if p.Category not in self.__categories:
                self.__categories.append(p.Category)
                self.__save_categories()
            self.__products.append(p)
            title, message = f"Добавление продукта в список {p.Category}!", f"Добавлен продукт {p.Name}, стоимость {p.Price * p.Count} руб"
            self.__save_products()
            send_data['data'] = _product

        elif command == "add_category":
            _category = json_data['data']
            if _category not in self.__categories:
                self.__categories.append(_category)
                self.__save_categories()
            title, message = "Добавлена новая категория продуктов!", f"Добавлена категория {_category}"
            send_data['data'] = _category

        elif command == "remove_product":
            _product = json_data['data']
            p = [_p for _p in self.__products if _p.Id == _product['Id'] and _p.Name == _product['Name']][0]
            self.__products.remove(p)
            self.__save_products()
            title, message = f"Удален товар из {_product['Category']}!", f"Убран товар {_product['Name']}"
            send_data['data'] = _product

        elif command == 'remove_products':
            _products = json_data['data']
            products = [_p for _p in self.__products for __p in _products if _p.Id == __p['Id'] and _p.Name == __p['Name']]
            for p in products:
                self.__products.remove(p)
            self.__save_products()
            send_data['data'] = _products

        elif command == 'remove_group':
            _groupName = json_data['data']
            self.__categories.remove(_groupName)
            self.__products = [_p for _p in self.__products if _p.Category != _groupName]
            self.__save_categories()
            self.__save_products()
            title, message = 'Удаление категории!', f'Удалена категория {_groupName}'
            send_data['data'] = _groupName

        elif command == 'change_namegroup':
            names = json_data['data']
            old, new = names['old_groupname'], names['new_groupname']
            self.__categories.remove(old)
            self.__categories.append(new)
            self.__save_categories()

            for p in self.__products:
                if p.Category == old:
                    p.Category = new
            self.__save_products()


        elif command == 'change_product':
            _product = json_data['data']
            oldName = ''
            for p in self.__products:
                if p.Id == _product['Id']:
                    oldName = p.Name
                    p.Name = _product['Name']
                    p.set_price(_product['Price'])
                    p.set_count(_product['Count'])
                    p.IsWeight = _product['IsWeight']
                    break
            self.__save_products()
            title, message = f"Изменен товар в {_product['Category']}!", f"Проверьте список, в нем поменялся {oldName}"
            send_data['data'] = _product
        
        elif command == 'complete_product':
            _product = json_data['data']
            for p in self.__products:
                if p.Name == _product['Name'] and p.Id == _product['Id']:
                    send_data['category'] = p.Category
                    p.set_complete(True)
                    _product['Completed'] = True
                    _product['Category'] = p.Category = 'Завершенные'
                    break
            send_data['data'] = _product
            title, message = "Покупка товара", f"Товар {_product['Name']} куплен"
            self.__save_products()
            
        elif command == 'change_user':
            __user = json_data['data']
            for p in self.__clients:
                if p.personal_id == __user['personal_id']:
                    p.name = __user['userName']
                    break
            send_data['data'] = __user
        
        _data = dict(data=json.dumps(send_data, ensure_ascii=False, indent=4, cls=productEncoder))
        for _cl in self.__clients:
            PushyAPI.sendPushNotification(title, message, _data, _cl.id, None)
        