
from apps.home import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db
from apps.home.db import allAgents
import sqlite3
# from exploit import attacker

@blueprint.route('/')
def index():
    agents = allAgents.query.all()
    return render_template('home/index.html', segment='index', agents=agents) 

@blueprint.route('/operations.html')
def operations():
    agents = allAgents.query.all()
    return render_template('home/operations.html', agents=agents)

@blueprint.route('/execute_operation', methods=['POST'])
def execute_script():
    arg = request.form.to_dict()
    agent = arg['agent_select']
    operation = arg['operation']
    result = attacker.amsi_execute()
    return jsonify(result=result)


@blueprint.route('/agents.html', methods=["GET"])
def agents_info():
    agents = allAgents.query.all()
    return render_template('home/agents.html', agents=agents)


@blueprint.route('/<template>')
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None






#update

@blueprint.route('/updateStatus', methods=['PUT'])
def udpateStatus():
    data = request.get_json()
    button_id = data.get('id')
    id = button_id.split("button-")[1]
    conn = sqlite3.connect('./apps/db.sqlite3')
    print(button_id)
    print(id)
    conn.execute("UPDATE all_agents SET status='Dead' WHERE id=?", id)
    conn.commit()
    # agents = allAgents.query.all()
    conn.close()
    # return render_template('home/agents.html', agents=agents)\
    return jsonify({"Message":"Data Status Updated"}) , render_template('home/agents.html')