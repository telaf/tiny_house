#!/usr/bin/env python3

# import http.server
# import socketserver
# import threading
# import handler
import datetime
import json
from flask import Flask, jsonify, render_template, request
from flask.ext.mysqldb import MySQL
import MySQLdb
from MySQLdb.cursors import DictCursor
from db_credentials import *

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_HOST'] = DB_HOST
app.config['MYSQL_USER'] = DB_USER
app.config['MYSQL_PASSWORD'] = DB_PASS
app.config['MYSQL_DB'] = DB_NAME
mysql.init_app(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/sensors")
def all():
    json = []

    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT * FROM `t_sensor_info`''')
    si = dict_cursor.fetchall()

    values_si = []
    for s_item in si:
        json.append(sensor_parser(s_item, dict_cursor))

    dict_cursor.close()
    return jsonify(all=json)

@app.route("/api/sensors/<int:s_id>", methods=['GET'])
def sensor_spec(s_id):
    #app.logger.info(s_id)
    json = []

    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT * FROM `t_sensor_info` WHERE id=''' + str(s_id))
    s_item = dict_cursor.fetchone()
    if s_item:
        sensor_object = sensor_parser(s_item, dict_cursor)
    else:
        sensor_object = None

    return jsonify(sensor=sensor_object)

def sensor_parser(s_item, dict_cursor):
    equipment_id = s_item['equipment_id']
    sensor_id = s_item['id']
    # app.logger.info(s_item)
    # app.logger.info(equipment_id)
    query_eq = '''SELECT * FROM `t_equipment` WHERE id=''' + str(equipment_id)
    dict_cursor.execute(query_eq)
    eq = dict_cursor.fetchone()
    # app.logger.info(query_eq)
    # app.logger.info(eq)
    query_ai = '''SELECT * FROM `t_actuator_info` WHERE sensor_id=''' + str(sensor_id)
    dict_cursor.execute(query_ai)
    ai = dict_cursor.fetchone()
    # app.logger.info(query_ai)
    # app.logger.info(ai)

    values_ai = []
    if ai:
        query_data_ai = '''SELECT * FROM `t_data` WHERE actuator_id=''' + str(ai['id']) + ''' ORDER BY timestamp ASC'''
        dict_cursor.execute(query_data_ai)
        # app.logger.info(query_data_ai)

        for val in dict_cursor.fetchall():
            values_ai.append([int(val['timestamp'].strftime("%s"))*1000, val['value']])

    values_si = []
    query_data_si = '''SELECT * FROM `t_data` WHERE sensor_id=''' + str(sensor_id) + ''' ORDER BY timestamp ASC'''
    dict_cursor.execute(query_data_si)
    # app.logger.info(query_data_si)

    for val in dict_cursor.fetchall():
        values_si.append([int(val['timestamp'].strftime("%s"))*1000, val['value']])

    # app.logger.info(values_si)
    values_dict = {"sensor": values_si, "actuator": values_ai}

    query_data_status = '''SELECT * FROM `t_data` WHERE sensor_id=''' + str(sensor_id) + ''' ORDER BY timestamp DESC LIMIT 0, 1'''
    dict_cursor.execute(query_data_status)
    status = dict_cursor.fetchone()
    app.logger.info(status)
    status_dict = {}
    if status is None or status['value'] == 9999:
        status_dict = {"status": 0}
    else:
        status_dict = {"status": 1}

    s_item.update(status_dict)

    _dict={"equipment": eq, "sensor_info": s_item, "actuator_info": ai, "values": values_dict}
    return _dict

@app.route("/api/actuators")
def all_actuators():
    json = []

    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT * FROM `t_actuator_info`''')
    ai = dict_cursor.fetchall()

    for at_item in ai:
        json.append(actuator_parser(at_item, dict_cursor))

    dict_cursor.close()
    return jsonify(all=json)

@app.route("/api/actuators/<int:a_id>", methods=['GET'])
def actuator_spec(a_id):
    #app.logger.info(s_id)
    json = []

    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT * FROM `t_actuator_info` WHERE id=''' + str(a_id))
    a_item = dict_cursor.fetchone()
    if a_item:
        actuator_object = actuator_parser(a_item, dict_cursor)
    else:
        actuator_object = None

    return jsonify(actuator=actuator_object)

def actuator_parser(a_item, dict_cursor):
    equipment_id = a_item['equipment_id']
    sensor_id = a_item['sensor_id']
    actuator_id = a_item['id']

    query_eq = '''SELECT * FROM `t_equipment` WHERE id=''' + str(equipment_id)
    dict_cursor.execute(query_eq)
    eq = dict_cursor.fetchone()
    # app.logger.info(query_eq)
    # app.logger.info(eq)

    query_si = '''SELECT * FROM `t_sensor_info` WHERE id=''' + str(sensor_id)
    dict_cursor.execute(query_si)
    si = dict_cursor.fetchone()
    # app.logger.info(query_ai)
    # app.logger.info(ai)


    values_si = []
    if si:
        query_data_si = '''SELECT * FROM `t_data` WHERE sensor_id=''' + str(sensor_id) + ''' ORDER BY timestamp ASC'''
        dict_cursor.execute(query_data_si)

        for val in dict_cursor.fetchall():
            values_si.append([int(val['timestamp'].strftime("%s"))*1000, val['value']])

    values_ai = []
    query_data_ai = '''SELECT * FROM `t_data` WHERE actuator_id=''' + str(actuator_id) + ''' ORDER BY timestamp ASC'''
    dict_cursor.execute(query_data_ai)
    # app.logger.info(query_data_si)

    for val in dict_cursor.fetchall():
        values_ai.append([int(val['timestamp'].strftime("%s"))*1000, val['value']])

    # app.logger.info(values_si)
    values_dict = {"sensor": values_si, "actuator": values_ai}

    query_data_status = '''SELECT * FROM `t_data` WHERE sensor_id=''' + str(sensor_id) + ''' ORDER BY timestamp DESC LIMIT 0, 1'''
    dict_cursor.execute(query_data_status)
    status = dict_cursor.fetchone()
    app.logger.info(status)
    status_dict = {}
    if status is None or status['value'] == 9999:
        status_dict = {"status": 0}
    else:
        status_dict = {"status": 1}

        si.update(status_dict)

    _dict={"equipment": eq, "sensor_info": si, "actuator_info": a_item, "values": values_dict}
    return _dict

@app.route("/api/rooms")
def rooms():
    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT * FROM `t_room`''')
    rms = dict_cursor.fetchall()

    for room in rms:
        room.update(room_parser(dict_cursor, room))

    dict_cursor.close()
    return jsonify(rooms=rms)

@app.route("/api/rooms/<int:r_id>", methods=['GET'])
def room(r_id):
    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)
    dict_cursor.execute('''SELECT * FROM `t_room` WHERE id=''' + str(r_id))

    rm = dict_cursor.fetchone()
    if rm:
        rm.update(room_parser(dict_cursor, rm))


    dict_cursor.close()
    return jsonify(room=rm)

def room_parser(dict_cursor, room):
    query_eqrm = '''SELECT * FROM `t_equipment` WHERE room_id=''' + str(room['id'])
    dict_cursor.execute(query_eqrm)
    equipment_rooms = dict_cursor.fetchall()
    # app.logger.info(equipment_rooms)
    sensors = []
    for eqrm in equipment_rooms:
        query_snrm = '''SELECT * FROM `t_sensor_info` WHERE equipment_id=''' + str(eqrm['id'])
        dict_cursor.execute(query_snrm)
        sensors_array = dict_cursor.fetchall()
        for sensor_obj in sensors_array:
            sensors.append(sensor_obj)

    # app.logger.info(sensors)
    return {"sensors": sensors}

@app.route("/api/equipment")
def equipment():
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT * FROM `t_equipment`''')
    eqs = dict_cursor.fetchall()

    for eq in eqs:
        eq.update(eq_parser(dict_cursor, eq))

    dict_cursor.close()
    return jsonify(equipment=eqs)

@app.route("/api/equipment/<int:e_id>", methods=['GET'])
def equipment_spec(e_id):
    cursor = mysql.connection.cursor()
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)
    dict_cursor.execute('''SELECT * FROM `t_equipment` WHERE id=''' + str(e_id))

    eq = dict_cursor.fetchone()
    if eq:
        eq.update(room_parser(dict_cursor, eq))


    dict_cursor.close()
    return jsonify(equipment=eq)

@app.route("/api/equipment/only/mac_address")
def equipment_only_mac_address():
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT mac_address FROM `t_equipment`''')
    eqs = [item['mac_address'] for item in dict_cursor.fetchall()]

    dict_cursor.close()
    return jsonify(mac_address_equipment=eqs)

def macs_for_post():
    dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)

    dict_cursor.execute('''SELECT mac_address FROM `t_equipment`''')
    eqs = [item['mac_address'] for item in dict_cursor.fetchall()]

    dict_cursor.close()
    return eqs

def eq_parser(dict_cursor, eq):
    sensors = []
    query_snrm = '''SELECT * FROM `t_sensor_info` WHERE equipment_id=''' + str(eq['id'])
    dict_cursor.execute(query_snrm)
    sensors_array = dict_cursor.fetchall()
    for sensor_obj in sensors_array:
        sensors.append(sensor_obj)

    # app.logger.info(sensors)
    return {"sensors": sensors}

@app.route('/api/post/actuator/new_data', methods=['GET', 'POST'])
def new_actuator_data():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)
        post = request.get_json()

        query_ns = '''INSERT INTO `censeps_data`.`t_data` (`id`, `sensor_id`, `actuator_id`, `value`, `timestamp`) VALUES (NULL, NULL, \"''' + str(post['actuator_id']) + '''\",\"''' + str(post['data']) + '''\",\"''' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '''\");'''
        cursor.execute(query_ns)
        mysql.connection.commit()
        return "This is a post call"

@app.route('/api/post/new_sensor', methods=['GET', 'POST'])
def new_sensor():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        dict_cursor = mysql.connection.cursor(cursorclass=DictCursor)
        mac_addrs = macs_for_post()
        post = request.get_json()
        app.logger.info(mac_addrs)

        # Will insert a new piece of equipment if it does not exist
        if str(post['mac_address']) not in mac_addrs:
            query_ns = ''' INSERT INTO `t_equipment` (`id`, `room_id`, `name`, `location`, `info`, `mac_address`) VALUES (NULL, \"''' + str(post['room_id']) + '''\", \"''' + str(post['equipment_name']) + '''\", \"''' + str(post['location']) + '''\", \"''' + str(post['equipment_info']) + '''\" , \"''' + str(post['mac_address']) + '''\");'''
            cursor.execute(query_ns)
            mysql.connection.commit()

        dict_cursor.execute('''SELECT * FROM `t_equipment` WHERE mac_address = \"''' + str(post['mac_address']) + '''\"''')
        eqid = dict_cursor.fetchone()
        app.logger.info(eqid['id'])

        query_ns = ''' INSERT INTO `t_sensor_info` (`id`, `equipment_id`, `name`, `unit`, `longunit`, `info`, `uid`) VALUES (NULL, \"''' + str(eqid['id']) + '''\", \"''' + str(post['sensor_name']) + '''\", \"''' + str(post['unit']) + '''\", \"''' + str(post['longunit']) + '''\" , \"''' + str(post['sensor_info']) + '''\", \"''' + str(post['uid']) + '''\");'''
        cursor.execute(query_ns)
        mysql.connection.commit()

        dict_cursor.execute('''SELECT * FROM `t_sensor_info` WHERE uid = \"''' + str(post['uid']) + '''\" AND equipment_id = \"''' + str(eqid['id']) + '''\"''')
        seid = dict_cursor.fetchone()
        app.logger.info(seid['id'])

        if post['is_actuator']:
            query_ns = ''' INSERT INTO `t_actuator_info` (`id`, `equipment_id`, `sensor_id`, `name`, `info`) VALUES (NULL, \"''' + str(eqid['id']) + '''\", \"''' + str(seid['id']) + '''\", \"''' + str(post['actuator_name']) + '''\" , \"''' + str(post['actuator_info']) + '''\");'''
            cursor.execute(query_ns)
            mysql.connection.commit()

        dict_cursor.close()
        cursor.close()

        # return "query_ns"
        return jsonify(mac_address_equipment=eqid)
    return "This is a post call"

@app.route("/api/rooms/update", methods=['GET', 'POST'])
def room_update():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        post = request.get_json()
        cursor.execute ("""
            UPDATE t_room
            SET name=%s, type=%s, info=%s
            WHERE id=%s
        """, (post['name'], post['type'], post['info'], post['id']))
        mysql.connection.commit()
        return "Success"
    return "This is a post call"

@app.route("/api/equipment/update", methods=['GET', 'POST'])
def equipment_update():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        post = request.get_json()
        cursor.execute ("""
            UPDATE t_equipment
            SET room_id=%s, name=%s, location=%s, info=%s
            WHERE id=%s
        """, (post['room_id'], post['name'], post['location'], post['info'], post['id']))
        mysql.connection.commit()
        return "Success"
    return "This is a post call"

@app.route("/api/sensors/update", methods=['GET', 'POST'])
def sensors_update():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        post = request.get_json()
        cursor.execute ("""
            UPDATE t_sensor_info
            SET name=%s, unit=%s, longunit=%s, info=%s
            WHERE id=%s
        """, (post['name'], post['unit'], post['longunit'], post['info'], post['id']))
        mysql.connection.commit()
        return "Success"
    return "This is a post call"

@app.route("/api/actuators/update", methods=['GET', 'POST'])
def actuators_update():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        post = request.get_json()
        cursor.execute ("""
            UPDATE t_actuator_info
            SET name=%s, info=%s
            WHERE id=%s
        """, (post['name'], post['info'], post['id']))
        mysql.connection.commit()
        return "Success"
    return "This is a post call"


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
