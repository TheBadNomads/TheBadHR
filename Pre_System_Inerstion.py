import Utilities
import pandas as pd
import os

from datetime import datetime, timedelta
from Member import member_db 
from Leave import leave_db

data = pd.read_excel(os.getenv("Pre_System_Leaves_excel_Path"))
data_dic = data.T.to_dict().values()

for record in data_dic:
    date = datetime(2021, 12, 1)
    days_count = record["Days_Count"]
    automatic_leave_id = -1
    for counter in range(days_count):
        leave_db.InsertLeave(record["Member_ID"], automatic_leave_id, record["Leave_Type"], date, "", "", "Approved", record["Is_Emergency"], record["Is_Unpaid"])
