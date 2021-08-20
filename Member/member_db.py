from db import db
from datetime import datetime

class member:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.name = attrs[1]
        self.email = attrs[2]
        self.start_date = attrs[3]
        self.leave_date = attrs[4]
        self.position = attrs[5]

    def GetMemeberByID(id):
        db.GetDBCursor().execute(f'SELECT * FROM [members] WHERE id = {id}')
        row = db.GetDBCursor().fetchone()
        
        return member(row)
    
    def GetMemebers():
        db.GetDBCursor().execute(f'SELECT * FROM [members]')
        rows = db.GetDBCursor().fetchall()
        members = []
        for row in rows:
            members.append(member(row))
        
        return members
    
    def InsertMember(id:int, name:str, email:str, start_date:datetime, leave_date:datetime, position:int):
        success = True
        try:
            db.GetDBCursor().execute(
                "INSERT INTO [members] (id, name, email, start_date, leave_date, position) VALUES (?, ?, ?, ?, ?, ?)",
                (id, name, email, start_date, leave_date, position)
            )    
            db.GetDBConnection().commit()
            # TODO: Insert Leave balance on success

        except Exception as e:
            db.GetDBConnection().rollback()
            success = False
        
        return success
