
__author__ = 'thopaz'
__version__ = '0.0.2'

import http.client
import json


class CospaceAPI(object):

    def __init__(self, user, passwd):
        self.user = user
        self.password = passwd

        # get session information on api.cospace.de
        initial_connection = http.client.HTTPSConnection("api.cospace.de")
        initial_connection.request("GET", "/api/session")

        # result is JSON encoded
        response = json.loads(initial_connection.getresponse().read())

        # print response
        print("session response: " + str(response))

        # cut "https://" prefix (8 characters) from server returned in JSON
        apiServer = response["server"][8:]

        # remember the session id
        self.session_id = response["sid"]

        # create the connection for the following API requests
        self.apiConnection = http.client.HTTPSConnection(apiServer)

        #
        # Authenticate the session
        #

        # post credentials into session
        request = {
            "email": self.user,
            "password": self.password
        }
        self.apiConnection.request("POST", "/api/session?sid=" + self.session_id, json.dumps(request))
        response = json.loads(self.apiConnection.getresponse().read())
        print("login response: " + str(response))
        if response['status'] == 'wrong-credentials':
            raise WrongCredentialsError('Provided credentials not accepted by cospace.')

    def __del__(self):
        #
        # Delete session
        #

        self.apiConnection.request("DELETE", "/api/session?sid=" + self.session_id)
        response = json.loads(self.apiConnection.getresponse().read())
        print("session deleted status: " + str(response["status"]))

    def user_info(self):
        self.apiConnection.request("GET", "/api/user?sid=" + self.session_id)
        response = json.loads(self.apiConnection.getresponse().read())
        # print("user info response:" + str(response))
        return response["user"]

    def sensor_info(self, sens_uuid):
        # Create msg url
        msg_url = "/api/sensor/" + sens_uuid + "?sid=" + self.session_id

        # Get sensor info
        self.apiConnection.request("GET", msg_url)
        response = json.loads(self.apiConnection.getresponse().read())
        # print('sensor info response: ' + str(response))

        return response['sensor']

    def sensor_data(self, sens_uuid, from_epoch, to_epoch, count):
        # Create msg url
        msg_url = "/api/sensor/" + sens_uuid + "/data?sid=" + self.session_id
        msg_url = msg_url + "&from=" + from_epoch + "&to=" + to_epoch + "&count=" + str(count) + "&order=asc"
        # print("URL is" + msg_url)

        # Get requested data point(s)
        self.apiConnection.request("GET", msg_url)
        response = json.loads(self.apiConnection.getresponse().read())
        # print("sensor data response: " + str(response))

        return response['data']

    def sensor_list_all(self):

        user_information = self.user_info()
        tag_all = user_information['tag_all']

        msg_url = "/api/tag/" + tag_all + "/object?filter=sensor&sid=" + self.session_id + "&count=500"

        # Get list of sensors
        self.apiConnection.request("GET", msg_url)
        response = json.loads(self.apiConnection.getresponse().read())
        print("sensor list response: " + str(response))

        return response['object']


class WrongCredentialsError(Exception):
    """Exception raised for errors in the login.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
