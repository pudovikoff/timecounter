import sqlite3
import argparse
import datetime
import pandas as pd
import numpy as np


def get_day(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    delta = datetime.timedelta(days=0, hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)
    return date - delta

def get_month(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    res = datetime.datetime(year=date.year, month=date.month, day=1)
    return date.month

def get_week(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.isocalendar().week


def start_work(con):
    cursor = con.cursor()

    cursor.execute("SELECT * FROM timelog ORDER BY id DESC LIMIT 1")
    last = cursor.fetchone()

    # if it is the first log or previous work was ended
    if not last or last[1] < last[2]:
        last_id = last[0] if last else -1
        start_time = datetime.datetime.now()
        t = cursor.execute("""INSERT INTO timelog (id, start_timestamp, end_timestamp)
                    VALUES (?, ?, ?)""",
                    (last_id + 1, start_time.timestamp(), 0))
        if t.rowcount == 1:
            print(f"Your work was started at {start_time}")
    else:
        print("Previous work was not ended")


def create_table(con):
    cursor = con.cursor()

    cursor.execute("""CREATE TABLE timelog
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                start_timestamp INTEGER, 
                end_timestamp INTEGER)
            """)
    
    print("Your logging table was created")
        


def end_work(con):
    cursor = con.cursor()

    cursor.execute("SELECT * FROM timelog ORDER BY id DESC LIMIT 1")
    last = cursor.fetchone()
    last_id = last[0]

    if last[2] == 0:
        end_time = datetime.datetime.now()
        start_date = datetime.datetime.fromtimestamp(last[1])
        while start_date.day != end_time.day:
            end_day = datetime.datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=23, minute=59, second=59, microsecond=999999)
            cursor.execute("UPDATE timelog SET end_timestamp=? WHERE id=?", (end_day.timestamp(), last_id))
            con.commit()

            start_date = end_day + datetime.timedelta(microseconds=1)
            print(start_date)
            cursor.execute("""INSERT INTO timelog (id, start_timestamp, end_timestamp)
                    VALUES (?, ?, ?)""",
                    (last_id + 1, start_date.timestamp(), 0))
            last_id += 1
        cursor.execute("UPDATE timelog SET end_timestamp=? WHERE id=?", (end_time.timestamp(), last_id))
        con.commit()

        print(f"Your work was started at {datetime.datetime.fromtimestamp(last[1])} \nand ended at {end_time}")
    else:
        print("Your work was not started")

def analitic(con, aggregate="day"):
    data = pd.read_sql_query("SELECT * FROM timelog", con, index_col="id")
    data["work_time"] = np.array(list(map(datetime.datetime.fromtimestamp ,data["end_timestamp"]))) -\
                    np.array(list(map(datetime.datetime.fromtimestamp ,data["start_timestamp"] )))
    data["day"] = np.array(list(map(get_day ,data["start_timestamp"] )))
    data["month"] = np.array(list(map(get_month ,data["start_timestamp"] )))
    data["week"] = np.array(list(map(get_week ,data["start_timestamp"] )))
    data = data[[aggregate, "work_time"]].groupby(aggregate).sum()
    print(data)
    data.to_csv(f"statistics_{aggregate}_{datetime.datetime.now().timestamp()}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['start', 'end', 'analitic'], default='analitic', type=str, required=False,
                         help="What action to record now - start or end of work or see statistics")
    parser.add_argument('--init', choices=[0, 1], default=False, type=int, required=False,
                         help="Create your own database by 1, nothing to do by 0")
    parser.add_argument('--db_path', default="timelogger.db", type=str, required=False,
                         help="Path to the SQLite3 database with records")
    parser.add_argument('--aggregation', choices=['day', 'week', 'month'], default='day', type=str, required=False,
                         help="On which time period aggregate statistics, working only with --action==\'analitic\'")
    args = parser.parse_args()
    # print(args)


    with sqlite3.connect(args.db_path) as con:
        if args.init:
            create_table(con)
        elif args.action == 'start':
            start_work(con)
        elif args.action == 'end':
            end_work(con)
        elif args.action == 'analitic':
            print("---- I am an analitic ------")
            analitic(con, args.aggregation)
            
    