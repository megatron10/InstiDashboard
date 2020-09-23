# from flask import (
#     Blueprint, current_app, flash, g, redirect, render_template, request,
#     session, url_for, jsonify
# )
import datetime
from app.db import get_db, exec_sql, rollback_db


def fixDates(inpDict: dict) -> dict:
    for key in inpDict:
        if type(inpDict[key]) == datetime.date:
            inpDict[key] = inpDict[key].strftime("%Y-%m-%d")
    return inpDict


def getId(cur):
    return cur.fetchone()[0]


def getAll(cur):
    colNames = [col[0] for col in cur.description]
    return [fixDates(dict(zip(colNames, row))) for row in cur.fetchall()]


def getRow(cur):
    row = cur.fetchone()
    colNames = [col[0] for col in cur.description]
    return fixDates(dict(zip(colNames, row))) if row else "NA"


def errorHandler(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            rollback_db(e)
            print(e)
            print("ATTENTION!")
            return e
    return inner_function


class Read:
    @staticmethod
    def read(self):
        pass


class Create:
    @staticmethod
    def create(self):
        pass


class Update:
    @staticmethod
    def update(self):
        pass


class Delete:
    @staticmethod
    def delete(self):
        pass


class Organisation(Create):
    @staticmethod
    @errorHandler
    def create(name: str, type: str) -> int:
        cur = exec_sql(f'''
            INSERT INTO organisation(name, type)
            VALUES (\'{name}\', \'{type}\')
            RETURNING org_id; ''')

        return getId(cur)  # return id of new org


class ListOrgs(Read):
    @staticmethod
    @errorHandler
    def read() -> list:
        cur = exec_sql(f'''SELECT * FROM organisation;''')

        return getAll(cur)


class Course(Create, Read):
    @staticmethod
    @errorHandler
    def create(kyc: str, type: str, title: str, course_code: str, org_id: int) -> int:
        cur = exec_sql(f'''
            INSERT INTO course(kyc, type, title, course_code, org_id)
            VALUES (\'{kyc}\', \'{type}\', \'{title}\', \'{course_code}\', {org_id})
            RETURNING course_id; ''')

        return getId(cur)

    @ staticmethod
    @errorHandler
    def read(course_id: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM course
            WHERE course_id = {course_id};
        ''')

        return getRow(cur)


class ListCourses(Read):
    @ staticmethod
    @ errorHandler
    def read(org_id: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM course
            WHERE org_id = {org_id};
        ''')

        return getAll(cur)


class Offering(Create, Read):
    @staticmethod
    @errorHandler
    def read(offering_id: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM offering
            WHERE offering_id = {offering_id};
        ''')
        return getRow(cur)

    @staticmethod
    @errorHandler
    def create(course_id: int, cal_link: str, grading_scheme: str, instructor: str, slot_id: int, start_date: str, end_date: str, previous_offering_id: int) -> int:
        cur = exec_sql(f'''
            INSERT INTO Offering(course_id, cal_link, grading_scheme, instructor, slot_id, start_date, end_date, previous_offering_id)
            VALUES ({course_id}, \'{cal_link}\', \'{grading_scheme}\', \'{instructor}\', {slot_id}, \'{start_date}\', \'{end_date}\', {previous_offering_id if previous_offering_id != None else "NULL"})
            RETURNING offering_id;
        ''')

        return getId(cur)


class ListOfferings(Read):
    @staticmethod
    @errorHandler
    def read(course_id: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM offering
            WHERE course_id = {course_id};
        ''')

        return getAll(cur)

# TODO : allow updating ratings


class Rating(Create):

    @staticmethod
    @errorHandler
    def create(user_id: int, offering_id: int, practice_rating: float, content_rating: float, theory_rating: float, litemeter: float) -> None:
        cur = exec_sql(f'''
            INSERT INTO rating(user_id, offering_id, practice_rating, content_rating, theory_rating, litemeter)
            VALUES({user_id}, {offering_id}, {practice_rating}, {content_rating}, {theory_rating}, {litemeter});
        ''')

        cur = exec_sql(f'''
            UPDATE offering
            SET nratings = nratings + 1,
                practice_rating = practice_rating + {practice_rating},
                content_rating = content_rating + {content_rating},
                theory_rating = theory_rating + {theory_rating},
                litemeter = litemeter + {litemeter}
            WHERE offering_id = {offering_id};
        ''')

        return None


class Resource(Create, Read):
    @staticmethod
    @errorHandler
    def create(offering_id: int, user_id: int, type: str = "", link: str = "", about: str = "") -> int:
        cur = exec_sql(f'''
            INSERT INTO resource(offering_id, user_id, type, link, about)
            VALUES ({offering_id}, {user_id}, \'{type}\', \'{link}\', \'{about}\')
            RETURNING resource_id;
        ''')

        return getId(cur)

    @staticmethod
    @errorHandler
    def read(resource_id: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM resource
            WHERE resource_id = {resource_id};
        ''')

        return getRow(cur)


class ListResources(Read):
    @staticmethod
    @errorHandler
    def read(offering_id: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM resource
            WHERE offering_id = {offering_id};
        ''')

        return getAll(cur)


class Slot(Create, Read):
    @staticmethod
    @errorHandler
    # dict int (day) -> dict {startTime: str, endTime: str}
    def create(org_id: int, slot_code: str) -> int:
        cur = exec_sql(f'''
            INSERT INTO slot(org_id, slot_code)
            VALUES ({org_id}, \'{slot_code}\')
            RETURNING slot_id;
        ''')

        return getId(cur)

    @staticmethod
    @errorHandler
    def read(slot_id: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM slot
            WHERE slot_id = {slot_id};
        ''')

        return getRow(cur)


class SlotSchedule(Create, Read):
    @staticmethod
    @errorHandler
    # dict int (day) -> dict {startTime: str, endTime: str}
    def create(slot_id: int, schedule: dict) -> int:
        times = [
            f"({slot_id}, {day}, \'{schedule[day]['start_time']}\', \'{schedule[day]['end_time']}\')"
            for day in schedule.keys() if day.isdigit() and int(day) < 7
        ]
        cur = exec_sql('''
            INSERT INTO slot_schedule(slot_id, day, start_time, end_time)
            VALUES
        ''' + ' ' + (', '.join(times)) + ';')

        return slot_id

    @staticmethod
    @errorHandler
    def read(slot_id: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM slot_schedule
            WHERE slot_id = {slot_id};
        ''')

        return getAll(cur)


class ListSlots(Read):
    @staticmethod
    @errorHandler
    def read(org_id: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM slot
            WHERE org_id = {org_id};
        ''')

        return getAll(cur)


class Usr(Create, Read):
    @staticmethod
    @errorHandler
    def create(email, token):
        cur = exec_sql(f'''
            INSERT INTO usr(email, token)
            VALUES (\'{email}\', \'{token.to_json()}\')
            RETURNING user_id;
        ''')

        return getId(cur)

    @staticmethod
    @errorHandler
    def read(user_id: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM usr
            WHERE user_id = {user_id};
        ''')

        return getRow(cur)

    @staticmethod
    @errorHandler
    def readE(email: str) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM usr
            WHERE email = \'{email}\';
        ''')

        return getRow(cur)

    @staticmethod
    @errorHandler
    def update(email, token) -> None:
        cur = exec_sql(f'''
            UPDATE usr
            SET token = \'{token.to_json()}\'
            WHERE email = \'{email}\';
        ''')

        return None


class Subscription(Create, Delete):
    @staticmethod
    @errorHandler
    def create(user_id: int, offering_id: int) -> None:
        cur = exec_sql(f'''
            INSERT INTO subscription(user_id, offering_id)
            VALUES ({user_id}, {offering_id});
        ''')

        return None

    @staticmethod
    @errorHandler
    def delete(user_id: int, offering_id: int) -> None:
        cur = exec_sql(f'''
            DELETE FROM subscription
            WHERE user_id = {user_id} AND offering_id = {offering_id};
        ''')

        return None


class ListSubscriptions(Read):
    @staticmethod
    @errorHandler
    def read(user_id: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM subscription
            WHERE user_id = {user_id};
        ''')

        return getAll(cur)


class Manager(Create):
    @staticmethod
    @errorHandler
    def create(user_id: int, org_id: int) -> None:
        cur = exec_sql(f'''
            INSERT INTO manager(user_id, org_id)
            VALUES ({user_id}, {org_id});
        ''')
        return None


def makeSlot(org_id, reqBody):
    slot_id = Slot.create(org_id, reqBody['slot_code'])
    status = SlotSchedule.create(slot_id, reqBody)
    return slot_id, (slot_id == status)


def getSlotIdByCode(org_id: int, slot_code: str) -> int:
    cur = exec_sql(f'''
        SELECT slot_id
        FROM Slot
        WHERE org_id = {org_id} AND slot_code = \'{slot_code}\';
    ''')

    return cur.fetchone()[0] if cur.rowcount else -1


def signin(email, credentials):
    row = Usr.readE(email)
    if row == "NA":
        return Usr.create(email, credentials)
    Usr.update(email, credentials)
    return row['user_id']

def isManager(user_id, org_id):
    cur = exec_sql(f'''
        SELECT * FROM manager
        WHERE user_id = {user_id} AND org_id = {org_id};
    ''')
    row = getRow(cur)
    return row != "NA"