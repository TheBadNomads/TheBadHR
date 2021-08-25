from db import db
from datetime import datetime

class member:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.name = attrs[1]
        self.email = attrs[2]
        self.start_date = attrs[3]

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
    
    def InsertMember(id:int, name:str, email:str, start_date:datetime):
        try:
            db.GetDBCursor().execute(
                "INSERT INTO [members] (id, name, email, start_date, leave_date) VALUES (?, ?, ?, ?, ?)",
                (id, name, email, start_date, datetime.strptime('1/1/3000', '%m/%d/%Y'))
            )    
            db.GetDBConnection().commit()
            # TODO: Insert Leave balance on success

            return "Success"

        except Exception as e:
            db.GetDBConnection().rollback()

            return "failed"
