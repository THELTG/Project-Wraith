from apps.home import blueprint
from flask import render_template, request, jsonify, redirect, url_for, send_from_directory, session, send_file
from apps import db
from apps.home.db import allAgents, operationResults
from c2server.server import *
from apps.exploit.operation import *
from apps.agent.script import *
import os
import socket
import time
import datetime
from apps.pdfgen import pdf_gen

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
    # files = [{'name': file.name} for file in os.scandir(directory) if file.is_file() and file.name.endswith('.exe')] keeping this for now, in case an operation is created that uses custom files (which are non .exe)
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
    directory = './apps/exploit/payload'
    files = [{'name': file.name} for file in os.scandir(directory) if file.is_file() and file.name.endswith('.exe')] # check for .exe only. Payload upload currently only supports .exe, might change in the future
    return render_template('home/payloads.html', segment='payloads', files=files)

@blueprint.route('/upload_payload', methods=["POST"])
def upload_payload():
    directory = './apps/exploit/payload/' 

    file = request.files['file']
    filename = file.filename

    if filename == '':
        return """
        <script>
            window.alert("No file was chosen.");
            window.location.href = document.referrer;
        </script>"""
    elif filename.split('.')[1] != 'exe':
        return """
        <script>
            window.alert("Please upload .exe payloads only.");
            window.location.href = document.referrer;
        </script>"""

    file.save(directory + filename)
    return """
            <script>
                window.alert("File Uploaded Successfully.");
                window.location.href = document.referrer;
            </script>"""

@blueprint.route('/delete_payload', methods=["POST"])
def delete_payload():
    directory = './apps/exploit/payload/' 

    filename = request.form['file_name']
    filepath = os.path.join(directory, filename)
    os.remove(filepath)

    return """
            <script>
                window.alert("Payload deleted successfully.");
                window.location.href = document.referrer;
            </script>"""

@blueprint.route("/generate_agent", methods=['POST'])
def generate_agent():
    arg = request.form.to_dict()
    ipAddr = arg['ipAddr']
    port = int(arg['port'])
    script_generate_agent(ipAddr, port)
    return """
            <script>
                window.alert("Compile Success");
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
            db.execute('PRAGMA foreign_keys = ON') # this goofy line needs to be added every single time we want to work with a foreign key in sqlite3.
            db.execute("DELETE FROM all_agents where identifier=?", [client_id])
            db.commit()
            return redirect(request.referrer)
    except OSError:
        time.sleep(5)

@blueprint.route("/display_results", methods=["POST"])
def display_results():
    global result_data
    data = request.get_json()

    if 'result' in data:
        result_data = data['result']
        print(f"Received result data:\n{result_data}\n")

    return '', 204  # 204 No Content response

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
                            start_time = int(time.time())
                            operation_tested = 'AMSI Bypass'

                            result = amsi_bypass(conn) # either True or False (converted to string later)
                            db.execute("""
                                INSERT INTO operation_results (agent_identifier, operationTested, result, time)
                                VALUES (?, ?, ?, ?)
                            """, (client_id, operation_tested, str(result), start_time))
                            db.commit()

                            time.sleep(1.5) # for the global variable to update
                            return render_template('home/operations.html', result_data=result_data, show_results=True)
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
                            start_time = int(time.time())
                            operation_tested = 'Reflective PE Injection'

                            result = reflectiveInjection(conn)
                            db.execute("""
                                INSERT INTO operation_results (agent_identifier, operationTested, result, time)
                                VALUES (?, ?, ?, ?)
                            """, (client_id, operation_tested, str(result), start_time))
                            db.commit()

                            time.sleep(1.5) # for the global variable to update
                            return render_template('home/operations.html', result_data=result_data, show_results=True)
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
                            start_time = int(time.time())
                            operation_tested = 'Kernel Driver Check'

                            result = driverCheck(conn)
                            db.execute("""
                                INSERT INTO operation_results (agent_identifier, operationTested, result, time)
                                VALUES (?, ?, ?, ?)
                            """, (client_id, operation_tested, str(result), start_time))
                            db.commit()

                            time.sleep(1.5) # for the global variable to update
                            return render_template('home/operations.html', result_data=result_data, show_results=True)
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


@blueprint.route("/generate_pdf/<identifier>", methods=["GET"])
def generate_pdf(identifier):
    hostname = db.execute("SELECT hostname FROM all_agents WHERE identifier=?", (identifier,)).fetchone()
    agentInfo = db.execute("SELECT identifier,username,ipAddress FROM all_agents WHERE identifier=?", (identifier,)).fetchone()

    db.execute('PRAGMA foreign_keys = ON') # enable fk
    # retrieves operation details, sorts by the latest operation result based on the unix timestamp value
    results = db.execute("""
    SELECT
        operation_results.operationTested,
        operation_results.result,
        operation_details.genericDetail,
        CASE
            WHEN operation_results.result = 'True' THEN operation_details.detailTrue
            WHEN operation_results.result = 'False' THEN operation_details.detailFalse
        END AS detail
    FROM
        operation_results
    JOIN
        operation_details ON operation_results.operationTested = operation_details.operationName
    WHERE
        operation_results.agent_identifier=?
    GROUP BY
        operation_results.operationTested
    ORDER BY
        MAX(operation_results.time) DESC
    """, (identifier,)).fetchall()

    if results != "null":
        filename = pdf_gen(results, hostname, agentInfo)
        directory = 'reports'
        if filename is not None:
            return send_from_directory(directory, filename, as_attachment=True)
        else:
            print("error")
            return "Error in PDF generation"

    else:
        return "No Test Conducted"
    


@blueprint.route("/report_rows", methods=["GET"])
def report_rows():
    db.execute('PRAGMA foreign_keys = ON') # enable fk
    rows = db.execute ("SELECT all_agents.identifier, all_agents.hostname, all_agents.operatingSystem, all_agents.ipAddress, MAX(operation_results.time) FROM all_agents JOIN operation_results ON all_agents.identifier = operation_results.agent_identifier;")
    row_list = [
        list(row[:-1]) + [datetime.datetime.fromtimestamp(row[-1]).strftime('%Y-%m-%d %H:%M:%S')] # convert epoch to datetime. used to display the 'last tested' date.
        for row in rows
    ]

    return jsonify({"rows": row_list})
    
    
