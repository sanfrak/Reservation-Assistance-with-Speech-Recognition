import urllib2
import json
import pymysql.cursors
import math
import dateutil.parser
import datetime
import time
import os
import logging
import urllib2
import json

# query_rds function queries the database for informations at snotDataPa4.sql.
# This .sql is exported from http://drsinus.martyhumphrey.info/phpmyadmin/ as an .sql filedump,
# and imported to AWS RDS using AWS CLI. This database is open to public,
# and the credentials are shown as follows
def query_rds(snot_day):
    # Database Connection Credentials
    rds_host = "sqlpa3part4test.cduxv3jn1joh.us-east-1.rds.amazonaws.com"
    user_name = "admin"
    password = "cellflue"
    db_name = "SQLPA3Part4Test"
    connection = pymysql.connect(rds_host, user_name, password, db_name, charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor)
    #print ("successfully connect to snotDataPa4.sql!!")

    try:
        with connection.cursor() as cursor:
            # SQL query based on the input (day)
            sql = "SELECT snot22_total FROM snotDataPa4 WHERE day = %s"
            # Execute query.
            cursor.execute(sql, (snot_day,)) 
            # Print ("cursor.description: ", cursor.description)
            # Store the value of queried data (snot22_total) in output_score
            data = cursor.fetchone()
            output_score = data['snot22_total']
    
    except pymysql.Error as error:
        return 0;
    
    finally:
        # Close connection.
        connection.close()
        return output_score

def insert_rds(snot_day, snot_total):
    # Database Connection Credentials
    rds_host = "sqlpa3part4test.cduxv3jn1joh.us-east-1.rds.amazonaws.com"
    user_name = "admin"
    password = "cellflue"
    db_name = "SQLPA3Part4Test"
    connection = pymysql.connect(rds_host, user_name, password, db_name, charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor)
    #print ("successfully connect to snotDataPa4.sql!!")
    flag = 0

    try:
        with connection.cursor() as cursor:
            # Execute query.
            sql = "INSERT INTO snotDataPa4 (day, snot22_total) VALUES (%s, %s)"
            cursor.execute(sql, (snot_day, snot_total))
            # Print ("cursor.description: ", cursor.description)
            flag = 1
        connection.commit()

    except pymysql.Error as error:
        return flag

    finally:
        # Close connection.
        connection.close()
        return flag

def delete_rds(snot_day):
    # Database Connection Credentials
    rds_host = "sqlpa3part4test.cduxv3jn1joh.us-east-1.rds.amazonaws.com"
    user_name = "admin"
    password = "cellflue"
    db_name = "SQLPA3Part4Test"
    connection = pymysql.connect(rds_host, user_name, password, db_name, charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor)
    #print ("successfully connect to snotDataPa4.sql!!")
    flag = 0

    try:
        with connection.cursor() as cursor:
            # SQL query based on the input (day)
            sql = "DELETE FROM snotDataPa4 WHERE day = %s"
            # Execute deletion.
            cursor.execute(sql, (snot_day,))
            flag = 1
            # Print ("cursor.description: ", cursor.description)
            connection.commit()

    except pymysql.Error as error:
        return cursor.rowcount

    finally:
        # Close connection.
        connection.close()
        return cursor.rowcount



def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.502b7271-6f41-4834-95fc-45e93fc0414f"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "SQLQuery":
        return perform_sql_query(intent)
    elif intent_name == "SQLInsert":
        return perform_sql_insert(intent)
    elif intent_name == "SQLDelete":
        return perform_sql_delete(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "BART - Thanks"
    speech_output = "Thank you for using the demo skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "BART"
    speech_output = "Welcome to the Alexa PA4 demo skill. " \
                    "You can query the total of any day, or " \
                    "ask me to make or cancel a reservation for you."
    reprompt_text = "Please ask me for reservations "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def perform_sql_query(intent):
    session_attributes = {}
    card_title = "BART Elevator Status"
    reprompt_text = ""
    should_end_session = False

    if "Snot_Day" in intent["slots"]:
        snot1_day = intent["slots"]["Snot_Day"]["value"]
        score_flag = query_rds(int(snot1_day))
        if score_flag == 0:
            speech_output = "It seems there's no reservation on day" + snot1_day + \
                            " yet, please choose another day."
        else:
            s22_out = str(score_flag)
            speech_output = "The total score on day " + snot1_day + " is " + s22_out
    else:
        speech_output = "in get_elevator_status, but else!"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def perform_sql_insert(intent):
    session_attributes = {}
    card_title = "BART Elevator Status Add"
    reprompt_text = ""
    should_end_session = False

    if "Snot_Day" in intent["slots"]:
        snot1_day = intent["slots"]["Snot_Day"]["value"]
        if "Snot_Total" in intent["slots"]:
            snot22_total = intent["slots"]["Snot_Total"]["value"]
            flag = insert_rds(int(snot1_day), int(snot22_total))
            if flag == 1:
                speech_output = "Congratuations! your reservation has been made on " \
                                "day " + snot1_day + " with the total of " + snot22_total
            else:
                speech_output = "Sorry, your reservation failed. Day" + snot1_day + " is" \
                                " currently unavailable, please choose another day."
    else:
        speech_output = "in get_elevator_add, but else!"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def perform_sql_delete(intent):
    session_attributes = {}
    card_title = "BART Elevator Status Delete"
    reprompt_text = ""
    should_end_session = False

    if "Snot_Day" in intent["slots"]:
        snot1_day = intent["slots"]["Snot_Day"]["value"]
        flag = delete_rds(int(snot1_day))
        if flag == 1:
            speech_output = "You have successfully canceled your reservation" \
                            " on day " + snot1_day
        else:
            speech_output = "Sorry, there's no reservation on day " + snot1_day + \
                            " ,please choose another day."
    else:
        speech_output = "in get_elevator_delete, but else!"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }