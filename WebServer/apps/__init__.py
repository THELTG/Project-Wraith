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
                INSERT INTO operation_details (operationName, genericDetail, detailTrue, detailFalse, detailMitigation)
                VALUES
                    ('AMSI Bypass', 'AMSI Bypasses involve techniques to evade detection by the Antimalware Scan Interface (AMSI), a feature in Windows Defender and other antivirus engines. Attackers use various methods, such as obfuscation and encryption, to bypass AMSI checks and execute malicious code without detection. The AMSI Bypass method in Wraith takes advantage of the Memory Patching method (https://rastamouse.me/memory-patching-amsi-bypass/).', 'AMSI was successfully bypassed using the AMSI Bypass Operation in Wraith. No alerts or warnings were triggered by the antimalware system.', 'The attempt to bypass AMSI using the AMSI Bypass Operation failed, due to the detection and prevention of the malicious activity by Windows Defender. For more accurate results, it is recommended that multiple AMSI Bypass levels are used to test the resilience of the system against different mutations of the AMSI Bypass technique used. For additional information, please refer to the documentation.','Protecting against AMSI Bypass, as a regular user, involves staying vigilant and ensuring that Windows Defender, your built-in antivirus protection, is consistently updated. AMSI Bypass techniques are often used by attackers to evade detection by security software, like Windows Defender. To enhance your defense, regularly check for and install Windows Defender updates to ensure that the latest threat signatures and detection methods are in place. Additionally, be cautious when clicking on links or downloading files from unfamiliar sources, as these may be potential vectors for AMSI Bypass attempts. Keep your operating system and applications updated to benefit from the latest security patches.'),
                    ('Reflective PE Injection', 'Reflective PE Injection is a sophisticated method of injecting PE (Portable Executable) files directly into the memory space of another process. This technique is commonly used by malware to avoid detection and enhance persistence by executing code without writing the payload to disk. Common payloads that are injected using this method are credential-stealing tools like Mimikatz, and powerful reverse-shell tools like Metasploit''s Meterpreter.', 'This operation successfully injected a PE file reflectively into the target machine, avoiding detection by traditional security mechanisms.', 'The attempt to perform Reflective PE Injection failed, resulting in detection and prevention of the malicious injection by security measures. If it has not been tried yet, it is recommended that the AMSI Bypass operation is executed first before executing the Reflective PE Injection operation for greater chances of success.','Mitigating Reflective PE Injection involves adopting proactive measures to safeguard your system. Regularly update your operating system and applications to patch vulnerabilities that could be exploited by attackers using this technique. Exercise caution when downloading and executing files, especially from untrusted sources. Employ a robust antivirus solution that includes behavioral analysis to detect and prevent Reflective PE Injections. Monitoring network traffic and employing intrusion detection systems can provide additional layers of defense. Implementing the principle of least privilege can limit the impact of successful injections, preventing potential unauthorized access.'),
                    ('Kernel Driver Check', 'This operation scans for vulnerable drivers in the target system by checking the drivers present in the system against a list of known vulnerable drivers found in LOLdrivers (https://www.loldrivers.io/). Detected vulnerabilities require prompt action, as it could indicate the presence of a malicious driver or a driver that can be taken advantage of to carry out exploitations like Privilege Escalation ; no vulnerabilities found indicates a secure system.', 'Vulnerable drivers were detected in the target system. Please refer to the information below to see the output of the operation.', 'No vulnerable drivers were found in the target system.','To mitigate the risks associated with vulnerable kernel drivers, regular system maintenance is crucial. Keep your operating system up to date with the latest security patches to address vulnerabilities in kernel drivers. Periodically check for driver updates from trusted sources and apply them promptly. Be cautious when installing third-party drivers, ensuring they come from reputable vendors. Consider the use of endpoint protection solutions that can identify and block malicious activities related to vulnerable kernel drivers. Regularly monitor security advisories for information on known vulnerabilities and follow best practices for securing your system against potential exploits.'),
                    ('RCE and Privilege Escalation Check', 'This operation serves as a tool that can identify possible/common vectors for Remote Code Execution and Privilege Escalation on a target Windows system. The operation was inspired by the tool Seatbelt (https://github.com/GhostPack/Seatbelt), and was created as a more light-weight version of the tool written in pure Powershell. It conducts five main checks : Operating System information, TCP Connections, Installed Applications, Processes, and Services.', 'The operation was able to run successfully and collect information from the target system. Please refer to the Operation Output below to view the information gathered.', '',''),
                    ('NetNTLMv2 Hijack', 'This operation steals the Net NTLMv2 hash of the currently logged in user and attempts to obtain the corresponding plaintext password using a bruteforce/dictionary attack. A successful password crack might indicate that the password being used by the user on the target system is very weak.', 'The operation was able to run successfully and crack the password of the logged on user on the target system.', 'The operation was unsuccessful in cracking the password of the user in the target system.','Mitigating the risk associated with the operation targeting NetNTLMv2 hashes revolves around enforcing robust password policies. Users should prioritize creating strong passwords by incorporating a combination of uppercase and lowercase letters, numbers, and symbols. Employing unique and complex passwords for individual accounts is paramount to thwarting dictionary attacks. Regular password updates contribute to ongoing security, preventing adversaries from exploiting outdated credentials. Encouraging users to refrain from using easily guessable information, such as common words or phrases, bolsters the effectiveness of password defenses. Users can also implement account lockout policies, temporarily locking user accounts after a certain number of unsuccessful login attempts, to mitigate the impact of brute-force attacks.');
                    """
                # add a row for lat movement later (jiwoo)
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
