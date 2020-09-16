from flask_restful import Resource, reqparse
from . import orgs_api

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request,
    session, url_for, jsonify
)

from app.db import get_db, exec_sql


class ListOrgs(Resource):
    def get(self):
        # sample exec_sql and output extraction.
        cur = exec_sql('SELECT * FROM usr;')
        output = cur.fetchall()
        return ' '.join(map(str, output))

    def post(self):
        """
            request.json = {
                "orgName" : "name",
                "type" : "type"
            }
        """
        return jsonify(request.json)


class ListCourses(Resource):
    def get(self, orgId):
        # fetch list of courses (dictionaries with SQL columns as keys)
        return jsonify({'courses': [1, 2, 3]})

    def post(self, orgId):
        """
            request.json = {
                "KYC" : "info",
                "type" : "type",
                "title' : "title",
                "courseCode" : "CSasde"
            }
        """
        return jsonify(request.json)


class ListSlots(Resource):
    def get(self, orgId):
        # fetch list of slots (dictionaries with SQL columns as keys)
        return jsonify({'slots': [1, 2, 3]})

    def post(self, orgId):
        """
            request.json = {
                "slotCode" : "Code",
                "events" : {
                    "Monday" : {
                        "start" : "2:30",
                        "end" : "4:00"
                    },
                    "Tuesday" : {
                        "start" : "4:00",
                        "end" : "5:30"
                    }
                }
            }
        """
        return jsonify(request.json)


class Course(Resource):
    def get(self, orgId, courseId):
        return jsonify({'KYC': "lite"})
        # fetch list of slots (dictionaries with SQL columns as keys)

    def post(self, orgId, courseId):
        '''
            request.json = {
                "referenceBooks" : "",
                "instructor" : "",
                "gradingScheme" : "",
                "startDate" : DATE,
                "endDate" : DATE,
                "slotCode" : "Code", #If this exists in the db look no further
                "events" : {
                    "Monday" : {
                        "start" : "2:30",
                        "end" : "4:00"
                    },
                    "Tuesday" : {
                        "start" : "4:00",
                        "end" : "5:30"
                    }
                }
            }
        '''
        return jsonify(request.json)


class Offering(Resource):
    def get(self, orgId, courseId, offeringId):
        return jsonify({"slotId": 1})


class Rating(Resource):
    def get(self, orgId, courseId, offeringId):
        return jsonify({"lite": 5})

    def post(self, orgId, courseId, offeringId):
        # parameters and values
        return jsonify(request.json)

#Resc -> Resource
class Resc(Resource):
    def get(self, orgId, courseId, offeringId):
        return jsonify({"lite": 5})

    def post(self, orgId, courseId, offeringId):
        # parameters and values
        return jsonify(request.json)


orgs_api.add_resource(ListOrgs, '/')
orgs_api.add_resource(ListCourses, '/<int:orgId>/courses')
orgs_api.add_resource(ListSlots, '/<int:orgId>/slots')
orgs_api.add_resource(Course, '/<int:orgId>/<int:courseId>')
orgs_api.add_resource(Offering, '/<int:orgId>/<int:courseId>/<int:offeringId>')
orgs_api.add_resource(
    Rating, '/<int:orgId>/<int:courseId>/<int:offeringId>/rating')
orgs_api.add_resource(
    Resc, '/<int:orgId>/<int:courseId>/<int:offeringId>/resource')
