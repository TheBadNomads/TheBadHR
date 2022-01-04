import pandas as pd

from datetime import datetime
from Leave import leave_db

path = input("Please enter the path of your csv file:\n")
data = pd.read_csv(path)
data_dic = data.iterrows()

for index, record in data_dic:
    date = datetime(2021, 12, 1)
    days_count = record["Days_Count"]
    automatic_leave_id = -1
    for counter in range(days_count):
        leave_db.InsertLeave(record["Member_ID"], automatic_leave_id, record["Leave_Type"], date, "", "", "Approved", record["Is_Emergency"], record["Is_Unpaid"])
