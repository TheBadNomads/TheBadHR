from db import db

class position:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.name = attrs[1]

    def GetPositions():
        db.GetDBCursor().execute('SELECT * FROM [positions]')
        rows = db.GetDBCursor().fetchall()
        positions = []
        for row in rows:
            positions.append(position(row))
        
        return positions