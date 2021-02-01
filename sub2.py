from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import threading
import json
import re
import sqlite3
import os
from urllib.request import urlopen
from urllib.error import *
import time

DATABASE_PATH = 'database/card_database.db'

sub_form = uic.loadUiType("db.ui")[0]


class Sub2(QDialog, sub_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushGen.clicked.connect(self.generate_databases)
        self.pushUpdate.clicked.connect(self.update_databases)

        self.database_thread = None

    def generate_databases(self):
        self.pushGen.setEnabled(False)
        self.pushUpdate.setEnabled(False)
        reply = QMessageBox.question(self, '데이터베이스 생성', '데이터베이스를 생성하시겠습니까?\n이 작업은 시간이 소요됩니다.' +
                                     '\n확실하지 않다면 데이터베이스를 업데이트하세요.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.database_thread = CreateDatabaseThread(self.update_card_progress_text, self.finish)
        else:
            self.finish()

    def update_databases(self):
        self.pushGen.setEnabled(False)
        self.pushUpdate.setEnabled(False)
        self.database_thread = UpdateDatabaseThread(self.update_card_progress_text, self.finish)

    def finish(self):
        self.update_card_progress_text('완료')
        self.pushGen.setEnabled(True)
        self.pushUpdate.setEnabled(True)

    def update_card_progress_text(self, text):
        self.label_db_progress.setText(text)

    def close_popup(self):
        if self.database_thread:
            if self.database_thread.isAlive():
                return

        self.master.destroy()


class UpdateDatabaseThread(threading.Thread):
    def __init__(self, card_print_function, finish_function):
        super().__init__(name='Database-Thread')
        self.daemon = True
        self.card_print_function = card_print_function
        self.finish_function = finish_function
        self.start()

    def run(self):
        update_card_database(self.card_print_function)
        self.finish_function()


class CreateDatabaseThread(threading.Thread):
    def __init__(self, card_print_function, finish_function):
        super().__init__(name='Database-Thread')
        self.daemon = True
        self.card_print_function = card_print_function
        self.finish_function = finish_function
        self.start()

    def run(self):
        create_card_database(self.card_print_function)
        self.finish_function()


def create_card_database(print_function):
    print_function('웹사이트 접속중...')
    try:
        with urlopen("https://shadowverse-portal.com/api/v1/cards?format=json&lang=ko") as response:
            source = response.read()
    except TimeoutError:
        print_function('웹사이트 접속에 실패했습니다. 다시 데이터베이스를 업데이트하세요.')
        return
    except URLError:
        print_function('웹사이트 접속에 실패했습니다. 인터넷 연결을 체크해주세요.')
        return

    print_function('카드 분류중...')
    cards_json = json.loads(source)
    cards_iterator = filter(lambda _card: _card['card_name'] is not None, cards_json['data']['cards'])
    cards = list(cards_iterator)

    for card in cards:
        card['card_name'] = card['card_name'].replace('\\', '').strip()
        card['description'] = replace_text(card['description'])
        card['evo_description'] = replace_text(card['evo_description'])

    if os.path.exists(DATABASE_PATH):
        try:
            os.remove(DATABASE_PATH)
        except OSError as e:
            print('Error while deleting file: ', DATABASE_PATH)
            print(e)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    print_function('테이블 작성중...')

    c.execute("""CREATE TABLE cards (
                    card_id integer,
                    card_set_id integer,
                    card_name text,
                    char_type integer,
                    clan integer,
                    tribe_name text,
                    skill_disc text,
                    evo_skill_disc text,
                    cost integer,
                    atk integer,
                    life integer,
                    evo_atk integer,
                    evo_life integer,
                    rarity integer,
                    use_red_ether integer,
                    description text,
                    evo_description text
                    )""")

    conn.commit()

    print_function('카드 정보 쓰는중...')
    for index, card in enumerate(cards):
        insert_card(card, conn, c)
        print_function(str(index + 1) + ' / ' + str(len(cards)) + ' 카드 정보 작성 완료.')

    print_function('완료.')

    conn.close()


def update_card_database(print_function):
    if not os.path.exists(DATABASE_PATH):
        create_card_database(print_function)
        return

    print_function('웹사이트 접속중...')
    try:
        with urlopen("https://shadowverse-portal.com/api/v1/cards?format=json&lang=ko") as response:
            source = response.read()
    except TimeoutError:
        print_function('웹사이트 접속에 실패했습니다. 다시 데이터베이스를 업데이트하세요.')
        return
    except URLError:
        print_function('웹사이트 접속에 실패했습니다. 인터넷 연결을 체크해주세요.')
        return

    print_function('카드 분류중...')
    cards_json = json.loads(source)
    cards_iterator = filter(lambda _card: _card['card_name'] is not None, cards_json['data']['cards'])
    cards = list(cards_iterator)

    for card in cards:
        card['card_name'] = card['card_name'].replace('\\', '').strip()
        card['description'] = replace_text(card['description'])
        card['evo_description'] = replace_text(card['evo_description'])

    conn = sqlite3.connect(DATABASE_PATH)
    print_function('카드 ID 검색중...')
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    card_ids = c.execute('SELECT card_id FROM cards').fetchall()
    num_of_cards = len(cards)

    print_function('카드 정보 쓰는중...')
    for index, card in enumerate(cards):
        if card['card_id'] not in card_ids:
            insert_card(card, conn, c)

        print_function(str(index + 1) + ' / ' + str(num_of_cards) + ' 카드 정보 작성 완료.')
    conn.close()
    print_function('완료.')


def replace_text(text):
    br = re.compile('<br>')
    line = re.compile('----------')

    text = re.sub(br, '\n', text)
    text = re.sub(line, '─────────', text)

    return text


def insert_card(card, conn, cursor):
    with conn:
        cursor.execute("""INSERT INTO cards VALUES (:card_id,
            :card_set_id,
            :card_name,
            :char_type,
            :clan,
            :tribe_name,
            :skill_disc,
            :evo_skill_disc,
            :cost,
            :atk,
            :life,
            :evo_atk,
            :evo_life,
            :rarity,
            :use_red_ether,
            :description,
            :evo_description)""",
            {
                'card_id': card['card_id'],
                'card_set_id': card['card_set_id'],
                'card_name': card['card_name'],
                'char_type': card['char_type'],
                'clan': card['clan'],
                'tribe_name': card['tribe_name'],
                'skill_disc': card['skill_disc'],
                'evo_skill_disc': card['evo_skill_disc'],
                'cost': card['cost'],
                'atk': card['atk'],
                'life': card['life'],
                'evo_atk': card['evo_atk'],
                'evo_life': card['evo_life'],
                'rarity': card['rarity'],
                'use_red_ether': card['use_red_ether'],
                'description': card['description'],
                'evo_description': card['evo_description']
            })
