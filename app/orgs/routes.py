from flask_restful import Resource, reqparse
from . import orgs_api

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request,
    session, url_for, jsonify, make_response
)

from app.db import get_db, exec_sql
import app.dbOps as dbOps



class ListOrgs(Resource):
    def get(self):
        return dbOps.ListOrgs.read()

    def post(self):
        """
            request.json = {
                "name" : "name",
                "type" : "type"
            }
        """
        reqBody = request.get_json()
        orgId = dbOps.Organisation.create(**reqBody)
        return make_response(f'Organisation indexed : {orgId}')


class ListCourses(Resource):
    def get(self, orgId):
        return dbOps.ListCourses.read(orgId)

    def post(self, orgId):
        """
            request.json = {
                "kyc" : "info",
                "type" : "type",
                "title' : "title",
                "courseCode" : "CSasde"
            }
        """
        reqBody = request.get_json()
        reqBody['orgId'] = orgId
        courseId = dbOps.Course.create(**reqBody)
        return make_response(f'Course indexed at : {courseId}')


class ListSlots(Resource):
    def get(self, orgId):
        return dbOps.ListSlots.read(orgId)

    def post(self, orgId):
        """
            request.json = {
                "slotCode" : "Code",
                "0" : { #Sunday
                    "startTime" : "2:30",
                    "endTime" : "4:00"
                },
                "1" : { #Monday
                    "startTime" : "4:00",
                    "endTime" : "5:30"
                }....
            }
        """
        reqBody = request.get_json()
        slotId, status = dbOps.makeSlot(orgId, reqBody)
        return make_response(f'Slot indexed at : {slotId}, schedule status : {status}')


class Course(Resource):
    def get(self, orgId, courseId):
        return dbOps.Course.read(courseId)

    def post(self, orgId, courseId):
        '''
            request.json = {
                "referenceBooks" : "",
                "instructor" : "",
                "gradingScheme" : "",
                "startDate" : DATE,
                "endDate" : DATE,
                "slotId" : {
                    "slotCode" : "Code", #If this exists in the db look no further
                    "1" : { #Monday
                        "start" : "2:30",
                        "end" : "4:00"
                    },
                    "2" : { #Tuesday
                        "start" : "4:00",
                        "end" : "5:30"
                    }
                },
                "previousOfferingId": null
            }
        '''
        reqBody = request.get_json()
        if type(reqBody['slotId']) != int:
            slotId = dbOps.getSlotIdByCode(
                orgId, reqBody['slotId']['slotCode'])
            if slotId <= 0:
                slotId, status = dbOps.makeSlot(orgId, reqBody['slotId'])
                print(
                    f'Slot indexed at : {slotId}, schedule status : {status}')
            reqBody['slotId'] = slotId
        return f'{dbOps.Offering.create(courseId, **reqBody)}'


class Offering(Resource):
    def get(self, orgId, courseId, offeringId):
        return dbOps.Offering.read(offeringId)

# TODO


class Rating(Resource):
    def get(self, orgId, courseId, offeringId):
        return jsonify({"lite": 5})

    def post(self, orgId, courseId, offeringId):
        # parameters and values
        return jsonify(request.json)


class ListResources(Resource):
    def get(self, orgId, courseId, offeringId):
        return dbOps.ListResources.read(offeringId)

    def post(self, orgId, courseId, offeringId):
        """
            request.json = {
                "type" : "",
                "link" : "",
                "about" : ""
            }
        """
        reqBody = request.get_json()
        reqBody['offeringId'] = offeringId
        reqBody['userId'] = 1  # testValue, get this from cookie later
        return dbOps.Resource.create(**reqBody)


orgs_api.add_resource(ListOrgs, '/')
orgs_api.add_resource(ListCourses, '/<int:orgId>/courses')
orgs_api.add_resource(ListSlots, '/<int:orgId>/slots')
orgs_api.add_resource(Course, '/<int:orgId>/<int:courseId>')
orgs_api.add_resource(Offering, '/<int:orgId>/<int:courseId>/<int:offeringId>')
orgs_api.add_resource(
    Rating, '/<int:orgId>/<int:courseId>/<int:offeringId>/rating')
orgs_api.add_resource(
    ListResources, '/<int:orgId>/<int:courseId>/<int:offeringId>/resource')
