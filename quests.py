import sqlite3
import random
import json

class auto_quests():
    def generator():
        # Устанавливаем соединение с базой данных
        conn = sqlite3.connect("database/Player/plr.db")
        cursor = conn.cursor()

        # Обрабатываем каждую запись в таблице plrs
        cursor.execute("SELECT lowID, brawlerData, trophies FROM plrs")
        player_data = cursor.fetchall()

        for player in player_data:
            lowID = player[0]
            data = json.loads(player[1])
            unlocked = [int(key) for key, value in data['UnlockedBrawlers'].items() if value == 1]
            unlocked_brawlers = random.choice([unlocked])
            quests = []

            trophies = player[2]

            if trophies < 300:
                continue  # Пропускаем генерацию квестов, если трофеев меньше 300

            # Проверяем количество квестов у игрока
            cursor.execute("SELECT quests FROM plrs WHERE lowID = ?", (lowID,))
            current_quests = json.loads(cursor.fetchone()[0])
            if len(current_quests) >= 18:
                # Удаляем все текущие квесты
                current_quests = []
                cursor.execute("UPDATE plrs SET quests = ? WHERE lowID = ?", (json.dumps(current_quests), lowID))
                conn.commit()

            for i in range(6):  # Генерируем 3 квеста для каждого игрока
                brawler_id = random.choice(unlocked_brawlers)
                win_count = random.randint(3, 8)
                prize = random.choice([100, 200, 400, 500, 550])
                qt = 1
                gm = random.choice([0, 6, 3])
                quest = {"id": brawler_id, "state": 0, "win_count": win_count, "counts": 0, "prize": prize, "QT": qt, "GM": gm}
                quests.append(quest)

            # Обновляем поле quests для текущего игрока
            current_quests.extend(quests)
            cursor.execute("UPDATE plrs SET quests = ? WHERE lowID = ?", (json.dumps(current_quests), lowID))
            conn.commit()

        # Закрываем соединение с базой данных
        conn.close()
