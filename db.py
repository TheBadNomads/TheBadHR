import sqlite3
import os

from dotenv import load_dotenv

load_dotenv()

class db:

    conn = None
    cursor = None

    @staticmethod
    def getConnection():
        if(db.conn == None):
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, os.getenv("DB_File"))
            db.conn = sqlite3.connect(db_path, detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        
        return db.conn

    @staticmethod
    def getCursor():
        if(db.cursor == None):
            db.cursor = db.getConnection().cursor()

        return db.cursor

    @staticmethod
    def commit():
        return db.getConnection().commit()

    @staticmethod
    def execute(query, params = ()):
        db.getCursor().execute(query, params)
        return db.commit()

    def GetCaption(captionCode):
        captions = {
            1: "Your leave request has been sent",
            2: "You dont have enough leaves to request, your current balance is ",
            3: "Please select valid dates",
            4: "Your Request has failed, try again later",
            5: "Your annual leave request was approved",
            6: "Your annual leave request was rejected",
            7: "Your request is being processed",
            8: "It is past core hours your leave request with be considered as an emergency leave",
            9: "Your emergency leave request was approved",
            10: "Your emergency leave request was rejected",
            11: "Your sick leave request was approved",
            12: "Your sick leave request was rejected",
        }

        return captions[captionCode] if captions[captionCode] != None else "Invalid caption code"
