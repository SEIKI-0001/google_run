from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Optional
from google.cloud import storage
import pandas as pd
import json
import os

app = Flask(__name__)

# ========= Config =========
USER_TZ = os.getenv("USER_TZ", "Asia/Tokyo")   # 例: "Asia/Tokyo"
TZ_OFFSET = os.getenv("TZ_OFFSET", "+09:00")   # 例: "+09:00"

# ========= Dataclasses / Planner =========
@dataclass
class UserSetting:
    user_id: str
    target_exam: datetime
    start_date: datetime
    weekday_minutes: int
    weekend_minutes: int
    rest_days: List[str]
    weekday_start: str
    weekend_start: str
    book_keyword: str

@dataclass
class Task:
    WBS: str
    Task_Name: str
    Date: datetime
    Duration: int
    Status: str = "未着手"
    @property
    def Day(self) -> str:
        return ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")[self.Date.weekday()]

MIN1, MIN2, MIN3 = 10, 7, 5

def next_day(d: datetime) -> datetime:
    return d + timedelta(days=1)

def is_weekend(d: datetime) -> bool:
    return d.weekday() >= 5

def calculate_available_time(user: UserSetting, date: datetime) -> int:
    if user.Day in user.rest_days:
        return 0
    return user.weekend_minutes if is_weekend(date) else user.weekday_minutes

class StudyPlanner:
    def __init__(self, user: UserSetting, chapter_items_list: List[str]):
        self.user = user
        self.chapter_items_list = chapter_items_list
        self.tasks: List[Task] = []
        self.wbs_counter = 0
        self.last_study_date: Optional[datetime] = None
        self.first_round_tasks: List[str] = []
        self.is_short = (self.user.target_exam - self.user.start_date).days <= 31

    def add_task(self, name: str, date: datetime, minutes: int):
        task = Task(f"wbs{self.wbs_counter}", name, date, minutes)
        self.tasks.append(task)
        self.wbs_counter += 1
        if self.last_study_date is None or date > self.last_study_date:
            self.last_study_date = date

    def step1_first_round(self):
        current_date = next_day(self.user.start_date)
        while self.chapter_items_list:
            available = calculate_available_time(self.user, current_date)
            while available >= MIN1 and self.chapter_items_list:
                name = self.chapter_items_list.pop(0)
                self.first_round_tasks.append(name)
                self.add_task(name, current_date, MIN1)
                available -= MIN1
            current_date = next_day(current_date)

    def step2_second_round(self):
        tasks = [(f"(2nd) {n}", MIN2) for n in self.first_round_tasks]
        current_date = next_day(self.last_study_date)
        for name, dur in tasks:
            self.add_task(name, current_date, dur)
            current_date = next_day(current_date)

    def step3_first_exam(self):
        tasks = [("過去問 2025年 (1/2)", 60), ("過去問 2025年 (2/2)", 60)]
        current_date = next_day(self.last_study_date)
        for name, dur in tasks:
            self.add_task(name, current_date, dur)
            current_date = next_day(current_date)

    def run_all(self):
        self.step1_first_round()
        self.step3_first_exam()
        self.step2_second_round()
        self.plan_df = pd.DataFrame([{
            "WBS": t.WBS,
            "Task Name": t.Task_Name,
            "Date": t.Date.strftime('%Y-%m-%d'),
            "Day": t.Day,
            "Duration": t.Duration,
            "Status": t.Status
        } for t in self.tasks])

# ========= Routes =========
@app.route("/")
@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})

@app.route("/generate", methods=["POST"])
def generate_plan():
    data = request.get_json() or {}
    user_id = data.get("user_id", "dummy")
    try:
        user = UserSetting(
            user_id=user_id,
            target_exam=datetime.strptime(data["target_exam_date"], "%Y-%m-%d"),
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d"),
            weekday_minutes=data["weekday_minutes"],
            weekend_minutes=data["weekend_minutes"],
            rest_days=data.get("rest_days", ["Wed"]),
            weekday_start=data.get("weekday_start", "20:00"),
            weekend_start=data.get("weekend_start", "13:00"),
            book_keyword=data["book_keyword"]
        )
        chapter_items_list = data.get("chapter_items_list", ["Chap1-1","Chap1-2"])
        planner = StudyPlanner(user, chapter_items_list)
        planner.run_all()
        return jsonify({"plan": planner.plan_df.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
