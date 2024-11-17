import time

from flask import Blueprint, render_template, request, jsonify
# from flask_login import login_required
from app.vms.service import VirtualMachineService
from app.vms.config import VMConfig

vm_bp = Blueprint('vms', __name__)


@vm_bp.route('/create', methods=['GET', 'POST'])
def create_vm():
    if request.method == 'POST':
        data = request.get_json()

        config = VMConfig(
            name=data.get('name'),
            memory=int(data.get('memory', 2048)),
            os_type=data.get('os_type')
        )
        vm_service = VirtualMachineService(config)
        success, message = vm_service.create_vm()
        return jsonify({'success': success, 'message': message})

    return render_template('vms/create.html')


@vm_bp.route('/<uuid>', methods=['DELETE'])
def delete_vm(uuid):
    delete_files = request.args.get('delete_files')

    if delete_files == 'true':
        delete_files = True

    vm_service = VirtualMachineService()
    success, message = vm_service.delete_vm(uuid, delete_files=delete_files)
    return jsonify({'success': success, 'message': message})

    return render_template('vms/create.html')


@vm_bp.route('/<uuid>/start', methods=['POST'])
def start_vm(uuid):
    vm_service = VirtualMachineService()
    success, message = vm_service.start_vm(uuid)
    return jsonify({'success': success, 'message': message})


@vm_bp.route('/<uuid>/stop', methods=['POST'])
def stop_vm(uuid):
    vm_service = VirtualMachineService()
    success, message = vm_service.stop_vm(uuid)
    return jsonify({'success': success, 'message': message})


@vm_bp.route('/list_vms', methods=['GET'])
def list_vms():
    vm_service = VirtualMachineService()  # No config needed for listing VMs
    success, result = vm_service.get_all_vms()
    print(result)
    # time.sleep(10)
    if success:
        running_vms = []
        stopped_vms = []
        for vm in result:
            status = vm['state']
            if status == 'running':
                running_vms.append(vm)
            elif status == 'poweroff':
                stopped_vms.append(vm)

        return render_template('vms/list_vms.html', vms=result, stopped_vms=stopped_vms, running_vms=running_vms)
    else:
        # Handle error case
        return render_template('vms/list_vms.html',
                               error=result,
                               running_vms=[],
                               stopped_vms=[],
                               vms=[])


@vm_bp.route('/list_running_vms', methods=['GET'])
def list_running_vms():
    # Initialize loading state
    loading = True

    try:
        vm_service = VirtualMachineService()
        success, result = vm_service.get_all_running_vms()
        print(result)

        if success:
            return render_template('vms/list_running_vms.html',
                                   is_loading=False,  # Operation complete, not loading
                                   running_vms=result)
        else:
            return render_template('vms/list_running_vms.html',
                                   is_loading=False,  # Operation complete, not loading
                                   error=result,
                                   running_vms=[])

    except Exception as e:
        return render_template('vms/list_running_vms.html',
                               is_loading=False,  # Operation complete, not loading
                               error=str(e),
                               running_vms=[])

# def list_running_vms():
#     command = ['vboxmanage', 'list', 'runningvms']
#     output = run_vboxmanage_command(command)
#     running_vms = [parse_vm_info(line) for line in output.splitlines() if parse_vm_info(line)]
#     return render_template('list_running_vms.html', running_vms=running_vms)
