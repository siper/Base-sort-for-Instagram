import urllib.request
import re 
import os.path
import http
import time
import logging
import timeit
import configparser
from datetime import datetime

# Установка папки со скриптом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Путь к файлу настроек settings.ini
SETTINGS = os.path.join(BASE_DIR, "settings.ini")
# Парсер для файла настроек
cfg = configparser.ConfigParser()
# Читаем файл настроек
try:
    cfg.read(SETTINGS)
except FileNotFoundError:
    # Если файл настроек не найден, то вываливаемся с ошибкой
    logging.info("Ошибка! Файл настроек не найден\n")
    print("Ошибка! Файл настроек не найден\n")
    sys.exit(1)

# Загрузка настроек
GOOD_ACC = cfg.get("folders", "GOOD_ACC")
BAD_WORDS = cfg.get("folders", "BAD_WORDS")
UNSORT = cfg.get("folders", "UNSORT")
LOG = cfg.get("folders", "LOG")
HIDDEN_PROFILE_FILE = cfg.get("folders", "HIDDEN_PROFILE_FILE")
BAD_ACC = cfg.get("folders", "BAD_ACC")
AVATAR_SW = cfg.getboolean("filters", "AVATAR_SW")
HIDDEN_PROFILE = cfg.getboolean("filters", "HIDDEN_PROFILE")
HIDDEN_PROFILE_FILE_SW = cfg.getboolean("filters", "HIDDEN_PROFILE_FILE_SW")
FOLLOW_SW = cfg.getboolean("filters", "FOLLOW_SW")
FOLLOW_COUNT_FROM = cfg.getint("filters", "FOLLOW_COUNT_FROM")
FOLLOW_COUNT_TILL = cfg.getint("filters", "FOLLOW_COUNT_TILL")
FOLLOWED_BY_SW = cfg.getboolean("filters", "FOLLOWED_BY_SW")
FOLLOWED_BY_COUNT_FROM = cfg.getint("filters", "FOLLOWED_BY_COUNT_FROM")
FOLLOWED_BY_COUNT_TILL = cfg.getint("filters", "FOLLOWED_BY_COUNT_TILL")
LAST_POST_SW = cfg.getboolean("filters", "LAST_POST_SW")
POSTS_COUNT_SW = cfg.getboolean("filters", "POSTS_COUNT_SW")
POSTS_COUNT_FROM = cfg.getint("filters", "POSTS_COUNT_FROM")
POSTS_COUNT_TILL = cfg.getint("filters", "POSTS_COUNT_TILL")
LAST_POST_DAYS = cfg.getint("filters", "LAST_POST_DAYS")
RECONNECT_SW = cfg.getboolean("system", "RECONNECT_SW")
# Абсолютные пути к файлу
UNSORT = os.path.join(BASE_DIR, UNSORT)
BAD_WORDS = os.path.join(BASE_DIR, BAD_WORDS)
GOOD_ACC = os.path.join(BASE_DIR, GOOD_ACC)
BAD_ACC = os.path.join(BASE_DIR, BAD_ACC)
HIDDEN_PROFILE_FILE = os.path.join(BASE_DIR, HIDDEN_PROFILE_FILE)
LOG = os.path.join(BASE_DIR, LOG)

logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.DEBUG, filename=LOG)

HEADERS = {
    'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.12) Gecko/20100101 Firefox/10.0.12 Iceweasel/10.0.12',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'deflate',
    'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
    'Cache-Control': 'max-age=0',
    'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

description_pt = re.compile("<meta content=\"(.+?)\" name=\"description\" />")
follow_pt = re.compile("follows\":\{\"count\":(\d+)\}")
followed_by_pt = re.compile("\"followed_by\":\{\"count\":(\d+)\}")
last_post_date_pt = re.compile("\"date\":(\d+)")
hidden_acc_pt = re.compile("\"is_private\":(true)")
posts_count_pt = re.compile("\"media\":\{\"count\":(\d+)")
avatar_pt = re.compile("\"profile_pic_url\":\"(.+?)\"")


def get_page(url):
    req = urllib.request.Request(url, headers=HEADERS)
    data = urllib.request.urlopen(req).read()
    text = data.decode("utf-8", "ignore")
    return text


def get_txt(fname):
    f = open(fname, "r", encoding="utf8")
    file_list = [line.strip() for line in f]
    f.close()
    return file_list 


def write_in_file(fname, acc_login):
    f = open(fname, "a+", encoding="utf8")
    f.write(acc_login + "\n")
    f.close()


try:
    accounts = get_txt(UNSORT)
except FileNotFoundError:
    # Если файл не найден, то вываливаемся с ошибкой
    logging.info("Ошибка! Файл с базой аккаунтов не найден\n")
    print("Ошибка! Файл с базой аккаунтов не найден\n")
    sys.exit(1)

try:
    stop_words = get_txt(BAD_WORDS)
except FileNotFoundError:
    # Если файл не найден, то вываливаемся с ошибкой
    logging.info("Ошибка! Файл с стоп-словами не найден\n")
    print("Ошибка! Файл с стоп-словами не найден\n")
    sys.exit(1)
old_accounts = []
# Ищем уже отфильтрованные аккаунты
try:
    old_accounts.extend(get_txt(GOOD_ACC))
except FileNotFoundError:
    pass
try:
    old_accounts.extend(get_txt(BAD_ACC))
except FileNotFoundError:
    pass
try:
    old_accounts.extend(get_txt(HIDDEN_PROFILE_FILE))
except FileNotFoundError:
    pass
if old_accounts:
    for old_account in old_accounts:
        try:
            accounts.remove(old_account)
        except ValueError:
            pass
print("Количество аккаунтов в базе: " + str(len(accounts)) + "\n")
logging.info("Количество аккаунтов в базе: " + str(len(accounts)) + "\n")
for account in accounts:
    start_time = timeit.default_timer()
    page = ""
    print("Проверка аккаунта: " + account)
    logging.info("Проверка аккаунта: " + account)
    try:
        page = get_page("http://instagram.com/" + account + "/")
    except urllib.error.HTTPError:
        print("Аккаунт " + account + " не существует")
        logging.info("Аккаунт " + account + " не существует")
        print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
        logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
        write_in_file(BAD_ACC, account)
        continue
    except http.client.RemoteDisconnected:
        print("Ошибка доступа к сайту")
        logging.info("Ошибка доступа к сайту")
        if RECONNECT_SW:
            print("Переподключение включено в настройках")
            logging.info("Переподключение включено в настройках")
            sleep_time = 60
            while page == "":
                print("Ждем " + str(sleep_time) + " секунд")
                logging.info("Ждем " + str(sleep_time) + " секунд")
                time.sleep(sleep_time)
                print("Переподключение...")
                logging.info("Переподключение...")
                try:
                    page = get_page("http://instagram.com/" + account + "/")
                except http.client.RemoteDisconnected:
                    sleep_time += sleep_time
        else:
            print("Завершение скрипта")
            logging.info("Завершение скрипта")
            sys.exit(1)
    # Проверка на наличие аватара
    if AVATAR_SW:
        avatar = avatar_pt.findall(page)
        if avatar:
            avatar = avatar[0]
        else:
            print("Завершено за: {0:.5f} секунд".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд".format(timeit.default_timer() - start_time))
            print("Странная ошибка связанная с аватаром у аккаунта: " + account)
            logging.info("Странная ошибка связанная с аватаром у аккаунта: " + account)
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
        if avatar != "https:\/\/scontent.cdninstagram.com\/t51.2885-19\/11906329_960233084022564_1448528159_a.jpg":
            pass
        else:
            print("Аккаунт " + account + " не подходит по аватару")
            logging.info("Аккаунт " + account + " не подходит по аватару")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
    # Конец проверки на наличие аватара
    # Проверка по подпискам
    if FOLLOW_SW:
        follow = follow_pt.findall(page)
        if follow:
            follow = int(follow[0])
        else:
            follow = 0
        if FOLLOW_COUNT_FROM < follow < FOLLOW_COUNT_TILL:
            pass
        else:
            print("Аккаунт " + account + " не подходит по подпискам")
            logging.info("Аккаунт " + account + " не подходит по подпискам")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
    # Конец проверки по подпискам
    # Проверка по подписчикам
    if FOLLOWED_BY_SW:
        followed_by = follow_pt.findall(page)
        if followed_by:
            followed_by = int(followed_by[0])
        else:
            followed_by = 0
        if FOLLOWED_BY_COUNT_FROM < followed_by < FOLLOWED_BY_COUNT_TILL:
            pass
        else:
            print("Аккаунт " + account + " не подходит по подписчикам")
            logging.info("Аккаунт " + account + " не подходит по подписчикам")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
    # Конец проверки по подписчикам
    description = description_pt.findall(page)[0]
    # Проверка на видимость профиля
    hidden_aac = hidden_acc_pt.findall(page)
    if hidden_aac and hidden_aac[0] == "true":
        if HIDDEN_PROFILE:
            print("Скрытый аккаунт " + account + " добавлен")
            logging.info("Скрытый аккаунт " + account + " добавлен")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            if HIDDEN_PROFILE_FILE_SW:
                write_in_file(HIDDEN_PROFILE_FILE, account)
            else:
                write_in_file(GOOD_ACC, account)
            continue
        else:
            print("Скрытый аккаунт " + account + " добавлен в список негодных аккаунтов")
            logging.info("Скрытый аккаунт " + account + " добавлен в список негодных аккаунтов")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
    # Конец проверки на видимость профиля
    # Проверка по количеству постов
    if POSTS_COUNT_SW:
        posts_count = posts_count_pt.findall(page)
        if posts_count:
            posts_count = int(posts_count[0])
        else:
            posts_count = 0
        if POSTS_COUNT_FROM < posts_count < POSTS_COUNT_TILL:
            pass
        else:
            print("Аккаунт " + account + " не подходит по количеству постов")
            logging.info("Аккаунт " + account + " не подходит по количеству постов")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
    # Конец проверки по количеству постов
    # Проверка на дату последнего поста
    if LAST_POST_SW:
        last_post_date = last_post_date_pt.findall(page)
        if last_post_date:
            last_post_date = time.gmtime(int(last_post_date[0]))
            last_post_date = datetime(year=last_post_date[0], month=last_post_date[1], day=last_post_date[2])
            last_post_date = datetime.toordinal(last_post_date)
            now_date = datetime.toordinal(datetime.now())
            if (now_date - last_post_date) <= LAST_POST_DAYS:
                pass
            else:
                print("Аккаунт " + account + " не проходит по дате последнего поста")
                logging.info("Аккаунт " + account + " не проходит по дате последнего поста")
                print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
                logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
                write_in_file(BAD_ACC, account)
                continue
        else:
            print("Аккаунт " + account + " не имеет постов")
            logging.info("Аккаунт " + account + " не имеет постов")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            continue
    # Конец проверки на дату последнего поста
    # Проверка по ключевым словам
    if description.startswith("Смотрите фото и видео от"):
        print("Аккаунт " + account + " добавлен")
        logging.info("Аккаунт " + account + " добавлен")
        print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
        logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
        write_in_file(GOOD_ACC, account)
        continue
    description = description.lower()
    for stop_word in stop_words:
        if stop_word.lower() in description:
            print("Аккаунт " + account + " не подходит по стоп-словам")
            logging.info("Аккаунт " + account + " не подходит по стоп-словам")
            print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
            write_in_file(BAD_ACC, account)
            break
    else:
        print("Аккаунт " + account + " добавлен")
        logging.info("Аккаунт " + account + " добавлен")
        print("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
        logging.info("Завершено за: {0:.5f} секунд\n".format(timeit.default_timer() - start_time))
        write_in_file(GOOD_ACC, account)
    # Конец проверки по ключевым словам
print("Сортировка закончена!")
print("Профильтровано аккаунтов за сеанс: " + str(len(accounts)) + "\n")
if len(accounts) != 0:
    logging.info("Сортировка закончена!")
    logging.info("Профильтровано аккаунтов за сеанс: " + str(len(accounts)) + "\n")
