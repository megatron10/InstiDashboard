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
    return [dict(zip(colNames, row)) for row in cur.fetchall()]


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
            INSERT INTO Organisation(name, type)
            VALUES (\'{name}\', \'{type}\')
            RETURNING orgId; ''')

        return getId(cur)  # return id of new org


class ListOrgs(Read):
    @staticmethod
    @errorHandler
    def read() -> list:
        cur = exec_sql(f'''SELECT * FROM Organisation;''')

        return getAll(cur)


class Course(Create, Read):
    @staticmethod
    @errorHandler
    def create(kyc: str, type: str, title: str, courseCode: str, orgId: int) -> int:
        cur = exec_sql(f'''
            INSERT INTO Course(kyc, type, title, courseCode, orgId)
            VALUES (\'{kyc}\', \'{type}\', \'{title}\', \'{courseCode}\', {orgId})
            RETURNING courseId; ''')

        return getId(cur)

    @ staticmethod
    @errorHandler
    def read(courseId: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM Course
            WHERE courseId = {courseId};
        ''')

        return getRow(cur)


class ListCourses(Read):
    @ staticmethod
    @ errorHandler
    def read(orgId: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM Course
            WHERE orgId = {orgId};
        ''')

        return getAll(cur)


class Offering(Create, Read):
    @staticmethod
    @errorHandler
    def read(offeringId: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM Offering
            WHERE offeringId = {offeringId};
        ''')
        print('HEY')
        return getRow(cur)

    @staticmethod
    @errorHandler
    def create(courseId: int, referenceBooks: str, gradingScheme: str, instructor: str, slotId: int, startDate: str, endDate: str, previousOfferingId: int) -> int:
        cur = exec_sql(f'''
            INSERT INTO Offering(courseId, referenceBooks, gradingScheme, instructor, slotId, startDate, endDate, previousOfferingId)
            VALUES ({courseId}, \'{referenceBooks}\', \'{gradingScheme}\', \'{instructor}\', {slotId}, \'{startDate}\', \'{endDate}\', {previousOfferingId if previousOfferingId != None else "NULL"})
            RETURNING offeringId;
        ''')

        return getId(cur)


class ListOfferings(Read):
    @staticmethod
    @errorHandler
    def read(courseId: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM Offering
            WHERE courseId = {courseId};
        ''')

        return getAll(cur)


# class Rating(Resource):
#     @staticmethod
#     @errorHandler
#     def read(offeringId: int) -> tuple:
#         cur = exec_sql(f'''
#             SELECT practiceRating, contentRating, thoeryRating, litemeter, nratings
#             FROM Offering
#             WHERE offeringId = {offeringId};
#         ''')

#         return getRow(cur)

#     @staticmethod
#     @errorHandler
#     def create(offeringId: int, practiceRating: float, contentRating: float, theoryRating: float, litemeter: float) -> None:
#         cur = exec_sql(f'''
#             UPDATE Offering
#             SET nratings = nratings + 1,
#                 practiceRating = practiceRating + {practiceRating},
#                 contentRating = contentRating + {contentRating},
#                 theoryRating = theoryRating + {theoryRating},
#                 litemeter = litemeter + {litemeter}
#             WHERE offeringId = {offeringId};
#         ''')

#         return getId(cur)

class Resource(Create, Read):
    @staticmethod
    @errorHandler
    def create(offeringId: int, userId: int, type: str, link: str, about: str) -> int:
        cur = exec_sql(f'''
            INSERT INTO Resources(offeringId, userId, type, link, about)
            VALUES ({offeringId}, {userId}, \'{type}\', \'{link}\', \'{about}\')
            RETURNING resourceId;
        ''')

        return getId(cur)

    @staticmethod
    @errorHandler
    def read(resourceId: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM Resources
            WHERE resourceId = {resourceId};
        ''')

        return getRow(cur)


class ListResources(Read):
    @staticmethod
    @errorHandler
    def read(offeringId: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM Resources
            WHERE offeringId = {offeringId};
        ''')

        return getAll(cur)


class Slot(Create, Read):
    @staticmethod
    @errorHandler
    # dict int (day) -> dict {startTime: str, endTime: str}
    def create(orgId: int, slotCode: str) -> int:
        cur = exec_sql(f'''
            INSERT INTO Slot(orgId, slotCode)
            VALUES ({orgId}, \'{slotCode}\')
            RETURNING slotId;
        ''')

        return getId(cur)

    @staticmethod
    @errorHandler
    def read(slotId: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM Slot
            WHERE slotId = {slotId};
        ''')

        return getRow(cur)


class SlotSchedule(Create, Read):
    @staticmethod
    @errorHandler
    # dict int (day) -> dict {startTime: str, endTime: str}
    def create(slotId: int, schedule: dict) -> int:
        times = [
            f"({slotId}, {day}, \'{schedule[day]['startTime']}\', \'{schedule[day]['endTime']}\')"
            for day in schedule.keys() if day.isdigit() and int(day) < 7
        ]
        cur = exec_sql('''
            INSERT INTO SlotSchedule(slotId, day, startTime, endTime)
            VALUES
        ''' + ' ' + (', '.join(times)) + ';')

        return slotId

    @staticmethod
    @errorHandler
    def read(slotId: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM SlotSchedule
            WHERE slotId = {slotId};
        ''')

        return getAll(cur)


class ListSlots(Read):
    @staticmethod
    @errorHandler
    def read(orgId: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM Slot
            WHERE orgId = {orgId};
        ''')

        return getAll(cur)


class Usr(Create, Read):
    @staticmethod
    @errorHandler
    def create(email, token):
        cur = exec_sql(f'''
            INSERT INTO Usr(email, token)
            VALUES (\'{email}\', \'{token.to_json()}\')
            RETURNING userId;
        ''')

        return getId(cur)

    @staticmethod
    @errorHandler
    def read(userId: int) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM Usr
            WHERE userId = {userId};
        ''')

        return getRow(cur)

    @staticmethod
    @errorHandler
    def readE(email: str) -> tuple:
        cur = exec_sql(f'''
            SELECT * FROM Usr
            WHERE email = \'{email}\';
        ''')

        return getRow(cur)

    @staticmethod
    @errorHandler
    def update(email, token):
        cur = exec_sql(f'''
            UPDATE Usr
            SET token = \'{token.to_json()}\'
            WHERE email = \'{email}\';
        ''')

        return 'cool'


class Subscription(Create, Delete):
    @staticmethod
    @errorHandler
    def create(userId: int, offeringId: int) -> None:
        cur = exec_sql(f'''
            INSERT INTO Subscriptions(userId, offeringId)
            VALUES ({userId}, {offeringId});
        ''')

        return None

    @staticmethod
    @errorHandler
    def delete(userId: int, offeringId: int) -> None:
        cur = exec_sql(f'''
            DELETE FROM Subscriptions
            WHERE userId = {userId} AND offeringId = {offeringId};
        ''')

        return None


class ListSubscriptions(Read):
    @staticmethod
    @errorHandler
    def read(userId: int) -> list:
        cur = exec_sql(f'''
            SELECT * FROM Subscriptions
            WHERE userId = {userId};
        ''')

        return getAll(cur)


def makeSlot(orgId, reqBody):
    slotId = Slot.create(orgId, reqBody['slotCode'])
    status = SlotSchedule.create(slotId, reqBody)
    return slotId, (slotId == status)


def getSlotIdByCode(orgId: int, slotCode: str) -> int:
    cur = exec_sql(f'''
        SELECT slotId
        FROM Slot
        WHERE orgId = {orgId} AND slotCode = \'{slotCode}\';
    ''')

    return cur.fetchone()[0] if cur.rowcount else -1

def signin(email, credentials):
    row = Usr.readE(email)
    if row == "NA":
        return Usr.create(email, credentials)
    Usr.update(email, credentials)
    return row['userid']
