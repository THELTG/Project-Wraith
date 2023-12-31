from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from sqlalchemy import text

db = SQLAlchemy()

def register_extensions(app):
    db.init_app(app)


def register_blueprints(app):
    module = import_module('apps.home.routes')
    app.register_blueprint(module.blueprint)

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
            query = "SELECT COUNT(*) FROM operation_details;" # check if data exists already
            result = db.session.execute(text(query)).scalar()
            if result == 0: 
                # details for all operations, modify accordingly if there are more added later.
                insert_statement = """
                INSERT INTO operation_details (operationName, genericDetail, detailTrue, detailFalse)
                VALUES
                    ('AMSI Bypass', 'AMSI Bypasses involve techniques to evade detection by the Antimalware Scan Interface (AMSI), a feature in Windows Defender and other antivirus engines. Attackers use various methods, such as obfuscation and encryption, to bypass AMSI checks and execute malicious code without detection. The AMSI Bypass method in Wraith takes advantage of the Memory Patching method (https://rastamouse.me/memory-patching-amsi-bypass/).', 'AMSI was successfully bypassed using the AMSI Bypass Operation in Wraith. No alerts or warnings were triggered by the antimalware system. To mitigate such attacks, it is recommended that the machine''s Windows Defender is constantly updated to the latest version so that AMSI can detect the latest signatures for AMSI Bypass attempts.', 'The attempt to bypass AMSI using the AMSI Bypass Operation failed, due to the detection and prevention of the malicious activity by Windows Defender. For more accurate results, it is recommended that multiple AMSI Bypass levels are used to test the resilience of the system against different mutations of the AMSI Bypass technique used. For additional information, please refer to the documentation.'),
                    ('Reflective PE Injection', 'Reflective PE Injection is a sophisticated method of injecting PE (Portable Executable) files directly into the memory space of another process. This technique is commonly used by malware to avoid detection and enhance persistence by executing code without writing the payload to disk. Common payloads that are injected using this method are credential-stealing tools like Mimikatz, and powerful reverse-shell tools like Metasploit's Meterpreter.', 'This operation successfully injected a PE file reflectively into the target machine, avoiding detection by traditional security mechanisms.', 'The attempt to perform Reflective PE Injection failed, resulting in detection and prevention of the malicious injection by security measures. If it has not been tried yet, it is recommended that the AMSI Bypass operation is executed first before executing the Reflective PE Injection operation for greater chances of success.'),
                    ('Kernel Driver Check', 'This operation scans for vulnerable drivers in the target system by checking the drivers present in the system against a list of known vulnerable drivers found in LOLdrivers (https://www.loldrivers.io/). Detected vulnerabilities require prompt action, as it could indicate the presence of a malicious driver or a driver that can be taken advantage of to carry out exploitations like Privilege Escalation ; no vulnerabilities found indicates a secure system.', 'Vulnerable drivers were detected in the target system. Please run the operation again to view the full list.', 'No vulnerable drivers were found. System is secure.');
                    """
                db.session.execute(text(insert_statement))
                db.session.commit()

        except Exception as e:
            print('> Error: DBMS Exception: ' + str(e) )

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
