import logging
import socket
import time
import os
from threading import Thread
import requests
from datetime import datetime, timedelta
from Logic.Device import Device
from Logic.Player import Players
from Logic.LogicMessageFactory import packets
from collections import defaultdict
import sqlite3 as sql
import json
from datetime import datetime
from database.DataBase import DataBase
import traceback

def _(*args):
    print('\033[0m[\033[94mCORE DEBUG\033[0m]', *args)

class Server:
    Clients = {"ClientCounts": 0, "Clients": {}}
    ThreadCount = 0
    MAX_CONNECTIONS_PER_IP = 9999

    def __init__(self, ip: str, port: int):
        #self.server = socket.socket()
        self.port = port
        self.ip = ip
        self.ip_counts = defaultdict(int)

    def get_country(self, ip):
        url = f"http://ip-api.com/json/{ip}"
        try:
            response = requests.get(url)
            data = response.json()
            country = data.get("countryCode", "Unknown")
        except (requests.RequestException, ValueError):
            country = "Unknown"
        return country
    
    def get_payments_data(self):
        url = f"https://easydonate.ru/api/v2/shop/83db9d44de0d37b77f0a8a11db8dd973/payments"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    def start(self):
        try:
            start_time = time.time()
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.ip, self.port))
            _(f"Server is listening on port {self.port}")
            if os.path.exists("database/Player/plr.db"):
                conn = sql.connect("database/Player/plr.db")
                c = conn.cursor()
                c.execute("UPDATE plrs SET roomID=0")
                c.execute("UPDATE plrs SET online=0")
                c.execute("SELECT * FROM plrs")
                conn.commit()
                conn.close()
            else:
                self.conn = sql.connect("database/Player/plr.db")
                self.cur = self.conn.cursor()
                self.cur.execute("CREATE TABLE IF NOT EXISTS plrs (token TEXT, lowID INT, name TEXT, trophies INT, gold INT, gems INT, starpoints INT, Troproad INT, profile_icon INT, name_color INT, clubID INT, clubRole INT, brawlerID INT, skinID INT, roomID INT, online INT, playerExp INT, SCC TEXT, trioWINS INT, sdWINS INT, theme INT, BPTOKEN INT, BPXP INT, freepass INT, buypass INT, friends JSON, brawlerData JSON, BrawlPass JSON)")
                self.conn.commit()
            self.server.listen()
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            payments_data = "Poje"#self.get_payments_data()
            print(f"Time done {execution_time_ms:.2f}")
            while True:

                client, address = self.server.accept()
                country = self.get_country(address[0])
                ALLOWED_COUNTRIES = {"RU", "BY", "UA", "UKR", "FI", "DE", "PL", "KZ", "MD", "KG", "IL", "BR"}
                if country in ALLOWED_COUNTRIES:
                    if country != "PL":
                        _(f'Attach! IP: {address[0]} {country}')
                    ClientThread(client, address, self.ip_counts).start()
                    Server.ThreadCount += 1
                else:
                    client.close()
        except KeyboardInterrupt:
                print("\n[*] Shutting down the proxy server.")
                self.server.close()


    def check_connection_limit(self, ip):
        count = self.ip_counts[ip]
        if count >= self.MAX_CONNECTIONS_PER_IP:
            return False
        self.ip_counts[ip] += 1
        return True


class ClientThread(Thread):
    def __init__(self, client, address, ip_counts):
        super().__init__()
        self.client = client
        self.address = address
        self.device = Device(self.client)
        self.player = Players(self.device)
        self.ip_counts = ip_counts

    def recvall(self, length: int):
        data = b''
        while len(data) < length:
            s = self.client.recv(length)
            if not s:
                print("Receive Error!")
                break
            data += s
        return data

    def run(self):
        last_packet = time.time()
        self.client.settimeout(20)  # Set socket timeout
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
                    self.address[0] = 0
                    del self.address[0]
                    DataBase.replaceValue(self, 'online', 0)
                    Server.ThreadCount -= 1
                    self.client.close()
                    break
        except ConnectionAbortedError:
            self.decrease_connection_count()
        except ConnectionResetError:
            self.decrease_connection_count()
        except TimeoutError:
            self.decrease_connection_count()
        except socket.timeout:  # Catch socket timeout
            self.decrease_connection_count()
        except BrokenPipeError:
            import sqlite3
            conn = sqlite3.connect("database/Player/plr.db")
            cursor = conn.cursor()
            delete_query = f"DELETE FROM plrs WHERE lowID = {self.player.low_id}"
            cursor.execute(delete_query)
            conn.commit()
            cursor.close()
            conn.close()
            Server.ThreadCount -= 1
            self.client.close()
    def decrease_connection_count(self):
        DataBase.replaceValue(self, "online", 0)
        Server.ThreadCount -= 1
        self.client.close()
        #print(f"[*] Ip: {self.address[0]} disconnected!")
def load_config(filename):
    with open(filename) as f:
        config = json.load(f)
    return config

if __name__ == '__main__':
    server = Server('0.0.0.0', 9339)
    server.start()