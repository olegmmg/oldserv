import socket
import time
import os
from threading import *
import sqlite3
from database.DataBase import DataBase
from Logic.Device import Device
from Logic.Player import Players
from Logic.LogicMessageFactory import packets
from Utils.Config import Config
from Utils.Helpers import Helpers
import json
from flask import Flask
import threading

def _(*args):
    print('[INFO]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()

addr = {}
block = []

# Создаем Flask приложение для health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Game server is running", 200

@app.route('/status')
def status():
    return json.dumps({
        "status": "online",
        "players": Server.ThreadCount if 'Server' in globals() else 0,
        "clients": Server.Clients["ClientCounts"] if 'Server' in globals() else 0
    }), 200

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

class Server:
    Clients = {"ClientCounts": 0, "Clients": {}}
    ThreadCount = 0
    
    def __init__(self, ip: str, port: int):
        self.server = socket.socket()
        self.port = port
        self.ip = ip
        
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        print(f'Server | Game server started! {self.ip}:{self.port}')
        
        # Создаем директорию если её нет
        if not os.path.exists("database/Player"):
            os.makedirs("database/Player")
        
        # Подключаемся к базе данных
        conn = sqlite3.connect("database/Player/plr.db")
        c = conn.cursor()
        
        # ВСЕГДА создаем таблицу, если она не существует
        c.execute("""CREATE TABLE IF NOT EXISTS plrs (
            token TEXT, 
            lowID INT, 
            name TEXT, 
            trophies INT, 
            gold INT, 
            gems INT, 
            starpoints INT, 
            tickets INT, 
            Troproad INT, 
            profile_icon INT, 
            name_color INT,
            clubID INT, 
            clubRole INT, 
            brawlerData JSON, 
            brawlerID INT, 
            skinID INT, 
            roomID INT, 
            box INT, 
            bigbox INT, 
            online INT, 
            vip INT, 
            playerExp INT, 
            friends JSON, 
            SCC TEXT,
            trioWINS INT,
            sdWINS INT, 
            theme INT, 
            BPTOKEN INT, 
            BPXP INT, 
            quests JSON, 
            freepass INT, 
            buypass INT, 
            notifRead INT, 
            notifRead2 INT
        )""")
        
        # Проверяем существование колонок и добавляем отсутствующие
        c.execute("PRAGMA table_info(plrs)")
        columns = [column[1] for column in c.fetchall()]
        
        # Список всех колонок, которые должны быть
        required_columns = {
            'roomID': 'INT', 'online': 'INT', 'token': 'TEXT', 'lowID': 'INT',
            'name': 'TEXT', 'trophies': 'INT', 'gold': 'INT', 'gems': 'INT',
            'starpoints': 'INT', 'tickets': 'INT', 'Troproad': 'INT',
            'profile_icon': 'INT', 'name_color': 'INT', 'clubID': 'INT',
            'clubRole': 'INT', 'brawlerData': 'JSON', 'brawlerID': 'INT',
            'skinID': 'INT', 'box': 'INT', 'bigbox': 'INT', 'vip': 'INT',
            'playerExp': 'INT', 'friends': 'JSON', 'SCC': 'TEXT',
            'trioWINS': 'INT', 'sdWINS': 'INT', 'theme': 'INT',
            'BPTOKEN': 'INT', 'BPXP': 'INT', 'quests': 'JSON',
            'freepass': 'INT', 'buypass': 'INT', 'notifRead': 'INT',
            'notifRead2': 'INT'
        }
        
        # Добавляем отсутствующие колонки
        for col, col_type in required_columns.items():
            if col not in columns:
                try:
                    c.execute(f"ALTER TABLE plrs ADD COLUMN {col} {col_type}")
                    print(f"Added column: {col}")
                except:
                    pass
        
        # Теперь обновляем данные
        c.execute("UPDATE plrs SET roomID=0")
        c.execute("UPDATE plrs SET online=0")
        conn.commit()
        conn.close()
        
        while True:
            self.server.listen()
            client, address = self.server.accept()
            if address[0] in addr:
                addr[address[0]] += 1
            else:
                addr[address[0]] = 0
            
            # Убираем iptables, просто блокируем через код
            if address[0] in block:
                client.close()
            elif addr[address[0]] >= 4:
                block.append(address[0])
                try:
                    config = open('config.json', 'r')
                    content = config.read()
                    settings = json.loads(content)
                    settings['block'].append(address[0])
                    print(f"{settings['block']}")
                    config.close()
                except:
                    pass
                client.close()
            else:
                ClientThread(client, address).start()
                Server.ThreadCount += 1

class ClientThread(Thread):
    def __init__(self, client, address):
        super().__init__()
        self.client = client
        self.address = address
        self.device = Device(self.client)
        self.player = Players(self.device)

    def recvall(self, length: int):
        data = b''
        while len(data) < length:
            s = self.client.recv(length)
            if not s:
                block.append(self.address[0])
                break
            data += s
        return data

    def run(self):
        last_packet = time.time()
        try:
            while True:
                header = self.client.recv(7)
                if len(header) > 0:
                    last_packet = time.time()
                    packet_id = int.from_bytes(header[:2], 'big')
                    length = int.from_bytes(header[2:5], 'big')
                    data = self.recvall(length)
                    if packet_id in packets:
                        message = packets[packet_id](self.client, self.player, data)
                        message.decode()
                        message.process()
                        if packet_id == 10101:
                            Server.Clients["Clients"][str(self.player.low_id)] = {"SocketInfo": self.client}
                            Server.Clients["ClientCounts"] = Server.ThreadCount
                            self.player.ClientDict = Server.Clients
                if time.time() - last_packet > 9:
                    if self.address[0] in addr:
                        del addr[self.address[0]]
                    DataBase.replaceValue(self, 'online', 0)
                    Server.ThreadCount -= 1
                    print(f"Player Online {Server.ThreadCount}")
                    self.client.close()
                    break
        except (ConnectionAbortedError, ConnectionResetError, TimeoutError):
            if self.address[0] in addr:
                del addr[self.address[0]]
            DataBase.replaceValue(self, 'online', 0)
            Server.ThreadCount -= 1
            print(f"Player Online {Server.ThreadCount}")
            self.client.close()

if __name__ == '__main__':
    # Запускаем HTTP сервер для health check на порту 10000
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    # Запускаем игровой сервер на порту 10001 (или другом свободном порту)
    GAME_PORT = 10001  # Используем другой порт
    server = Server('0.0.0.0', GAME_PORT)
    server.start()
