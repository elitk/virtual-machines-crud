# import subprocess
# import re
# import time
# from flask import Flask, render_template, jsonify
#
# app = Flask(__name__)
#
#
# def run_vboxmanage_command(command):
#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         return e.stderr
#
#
# @app.route("/")
# def hello_world():
#     return render_template("index.html")
#
#
# @app.route('/', endpoint='index')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/create', methods=['GET', 'POST'], endpoint='create')
# def create():
#     return render_template('create.html')
#
#
# def parse_vm_info(vm_line):
#     # Parse VM line which typically looks like: "VM Name" {uuid}
#     match = re.match(r'"([^"]+)"\s+{([^}]+)}', vm_line)
#     print({vm_line})
#     if match:
#         return {
#             'name': match.group(1),
#             'uuid': match.group(2),
#             'status': 'Powered Off'  # Default status, you can get actual status with another vboxmanage command
#         }
#     return None
#
#
# def get_vm_status(uuid):
#     """Get the status of a VM using its UUID."""
#     command = ['vboxmanage', 'showvminfo', uuid, '--machinereadable']
#     output = run_vboxmanage_command(command)
#
#     # Parse the output to find the line that contains the VM state
#     for line in output.splitlines():
#         if line.startswith('VMState='):
#             return line.split('=')[1].strip('"')
#
#     return 'unknown'
#
#
# def get_all_vm_statuses(uuids):
#     return [get_vm_status(uuid) for uuid in uuids]
#
#
# @app.route('/list_vms', methods=['GET'])
# def list_vms():
#
#     command = ['vboxmanage', 'list', 'vms']
#     output = run_vboxmanage_command(command)
#     vms = [parse_vm_info(line) for line in output.splitlines() if parse_vm_info(line)]
#     uuids = [vm['uuid'] for vm in vms]
#     statuses = get_all_vm_statuses(uuids)
#
#     for index, vm in enumerate(vms):
#         vm['status'] = statuses[index]
#
#     running_vms = sum(1 for vm in vms if vm['status'] == 'running')
#     stopped_vms = sum(1 for vm in vms if vm['status'] == 'poweroff')
#     print(vms)
#
#     # time.sleep(3)
#     return render_template('list_vms.html', vms=vms, running_vms=running_vms, stopped_vms=stopped_vms)
#
#
#
# @app.route('/list_running_vms', methods=['GET'])
# def list_running_vms():
#     command = ['vboxmanage', 'list', 'runningvms']
#     output = run_vboxmanage_command(command)
#     running_vms = [parse_vm_info(line) for line in output.splitlines() if parse_vm_info(line)]
#     return render_template('list_running_vms.html', running_vms=running_vms)
#
#
# app.run(debug=True)
from app import create_app  # Import the create_app function

app = create_app()  # Create the app instance

if __name__ == '__main__':
    app.run(debug=True)
