import threading as th
import datetime
import time
from random import seed
from random import randint
import sqlite3 as sql
import os
import zipfile as zf
from werkzeug.utils import secure_filename
import string

active_pins = []


seed(1)

def loop():
    print("Loop Started...")
    connection = sql.connect(os.path.dirname(__file__)+"/active_files.db")
    cursor=connection.cursor()

    m = cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table';''').fetchall()
    # if the count is 1, then table exists
    if ("pins",) not in m:
        cursor.execute(
            f""" CREATE TABLE {"pins"} (pin INTEGER PRIMARY KEY, filename TEXT, timeOfrecieve timestamp);""")
        connection.commit()
    connection.close()

    # connect to database
    connection = sql.connect(os.path.dirname(__file__) + "/active_files.db")
    cursor = connection.cursor()
    # get all pins
    select = """SELECT pin from pins"""
    select = cursor.execute(select).fetchall()
    # close connection to database
    connection.close()

    for m in select:
        active_pins.append(m[0])
    while True:
        #connect to database
        connection = sql.connect(os.path.dirname(__file__)+"/active_files.db")
        cursor = connection.cursor()
        #get all pins
        select = """SELECT pin, timeOfrecieve, filename from pins"""
        select = cursor.execute(select).fetchall()
        # close connection to database
        connection.close()
        for pin, timeOfrecieve, filename in select:
            #convert string to time
            timeOfrecieve = datetime.datetime.strptime(timeOfrecieve, "%Y-%m-%d %H:%M:%S.%f")
            #check if 10 minutes had passed
            if (datetime.datetime.now() - timeOfrecieve).total_seconds() >= 600:
                #delete file from database and storage
                print("File " + str(pin)+" Deleted")
                os.remove(os.path.dirname(__file__) + f"/Files/{filename}")
                if str(filename).find("/") != -1:
                    os.rmdir(os.path.dirname(__file__)+f"/Files/{pin}")
                connection = sql.connect(os.path.dirname(__file__) + "/active_files.db")
                cursor = connection.cursor()
                cursor.execute("""DELETE FROM pins WHERE pin=?""", (pin,))
                connection.commit()
                connection.close()
                try:
                    active_pins.remove(int(pin))
                except:
                    pass

        time.sleep(300)
    print("Loop Ended...")

def mainLoop():
    #File check loop
    print("Starting Loop...")
    loopT = th.Thread(target=loop, daemon=True)
    loopT.start()
    #Other

def safe_file(file, pin, compress):
    now = datetime.datetime.now()
    filename = str(file.filename)
    filename = filename.strip().replace(' ', '_')
    valid_chars = "-_. %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)

    if compress:
        data_tuple = (pin, str(pin) + ".zip", now)
        th.Thread(target=create_compressed_file, args=(file, pin,), daemon=True).start()
    else:
        data_tuple = (pin, str(pin) + "/" + filename, now)

    connection = sql.connect(os.path.dirname(__file__)+"/active_files.db")
    sqlite_insert_with_param = """INSERT INTO 'pins'
                                      ('pin', 'filename','timeOfrecieve') 
                                      VALUES (?, ?, ?);"""
    cursor = connection.cursor()
    cursor.execute(sqlite_insert_with_param, data_tuple)
    connection.commit()
    connection.close()
    return pin, now.strftime("%m/%d/%Y, %H:%M:%S")

def pin_generator():
    pin = randint(100000, 999999)
    while pin in active_pins:
        pin = randint(100000, 999999)
    active_pins.append(pin)
    return pin

def create_compressed_file(file, pin):
    with zf.ZipFile(os.path.dirname(__file__)+"/Files/"+str(pin)+".zip", "w", zf.ZIP_DEFLATED) as zipfile:
        zipfile.write(os.path.dirname(__file__)+f"/{pin}/"+secure_filename(file.filename), secure_filename(file.filename))
        os.remove(os.path.dirname(__file__)+f"/{pin}/"+secure_filename(file.filename))
        os.rmdir(os.path.dirname(__file__)+f"/{pin}")
        zipfile.close()

def get_file(pin, endings):
    sqlite_get_with_param = f"""SELECT pin, filename FROM pins WHERE pin={int(pin)}"""
    connection = sql.connect(os.path.dirname(__file__) + "/active_files.db")
    cursor = connection.cursor()
    m = cursor.execute(sqlite_get_with_param).fetchall()
    connection.close()
    if m != []:
        if (str(m[0][1]).split("."))[1] in endings:
            return os.path.dirname(__file__)+f"/Files/", m[0][1]
        else:
            return os.path.dirname(__file__)+"/Files/", m[0][1]
    else:
        return None, None

def get_admin_data():
    pass