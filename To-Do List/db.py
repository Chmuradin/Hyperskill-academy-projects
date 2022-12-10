from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task

    @staticmethod
    def add_task() -> None:
        task = input("\nEnter a task\n")
        date = input("\nEnter a deadline")
        if not date:
            date = datetime.today().strftime("%Y-%m-%d")
        new_row = Task(task=task,
                       deadline=datetime.strptime(date, "%Y-%m-%d").date())
        session.add(new_row)
        session.commit()

    @staticmethod
    def delete_task(index: int) -> None:
        session.query(Task).filter(Task.id == index).delete()
        session.commit()

    @staticmethod
    def find_all():
        return session.query(Task.task, Task.deadline).order_by(Task.deadline).all()

    @staticmethod
    def find_day(date=datetime.today(), td=0, long=True, short=False):
        day = date + timedelta(td)
        if long:
            print(weekDays[day.weekday()], day.strftime("%d %b"))
        if short:
            print(f'Today {day.strftime("%d %b")}:')
        return session.query(Task).filter(Task.deadline == day.strftime("%Y-%m-%d")).all()

    @staticmethod
    def missed():
        return session.query(Task.task, Task.deadline).filter(Task.deadline < datetime.today().date()).all()


FILE_NAME = "todo.db"

engine = create_engine(f"sqlite:///{FILE_NAME}?check_same_thread=False")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
