import pyodbc 
import os

from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

class db:

    conn = None
    cursor = None

    @staticmethod
    def GetDBConnection():
        if(db.conn == None):
            db.conn = pyodbc.connect(os.getenv("Connection_String"))

        return db.conn

    @staticmethod
    def GetDBCursor():
        if(db.cursor == None):
            db.cursor = db.GetDBConnection().cursor()

        return db.cursor

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

