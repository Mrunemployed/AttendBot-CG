from typing import Any
import pandas as pd
from datetime import datetime
import datetime

class Bribe():

    def __init__(self) -> None:
        pass
    
    def manipulate(self,df:pd.DataFrame):
        try:
            for i,j in df.iterrows():
                if df.loc[i,"Rostered shift"] == "PH" | df.loc[i,"Rostered shift"] == "WO" | df.loc[i,"Attended shift"] == "Leave":
                    df.loc[i,"Mode"] = "ignore"
                elif df.loc[i,"Attendance status"] == "PendingApproval":
                    df.loc[i,"Mode"] = "ignore"
                elif type(df.loc[i,"Date"])!= float:
                    if datetime.datetime.strptime(df.loc[i,"Date"],"%d-%b-%Y") >= datetime.datetime.now():
                        df.loc[i,"Mode"] = "ignore"
                    else:
                        pass
                else:
                    in_time = df.loc[i,"In Time"]
                    out_time = df.loc[i,"Out Time"]

                    if type(in_time) == float and type(out_time) == float:
                        pass
                    else:
                        diff = datetime.datetime.strptime(out_time,"%H:%M") - datetime.datetime.strptime(in_time,"%H:%M")
                        if int(in_time[:2]) == 0 and int(out_time[:2]) == 0:
                            df.loc[i,"Mode"] = "Manual Swipe Attendence"
                        elif int(in_time[:2]) != 0 and int(out_time[:2]) != 0 and diff < datetime.timedelta(hours=8):
                            df.loc[i,"Mode"] = "Swipe Adjustment"
                        else:
                            df.loc[i,"Mode"] = "ignore"
                df.fillna("NoValue",inplace=True)
            return df
        except Exception as e:
            return str(e)

# df = pd.read_excel("5-attendence-data.xlsx")
# br = Bribe()
# br.manipulate(df)

