import os

import requests
from flask import Blueprint, render_template, request, jsonify, flash, url_for
# from flask_login import login_required
from app.vms.service import VirtualMachineService
from app.vms.config import VMConfig

vm_bp = Blueprint('vms', __name__)

HOST_SERVICE_URL = os.getenv('HOST_SERVICE_URL', 'http://localhost:5001')


@vm_bp.route('/<uuid>/edit')
def edit_vm(uuid):
    vm = get_vm(uuid)  # Your function to get VM details
    return render_template('pages/edit_vm.html', vm=vm)


@vm_bp.route('/<uuid>', methods=['PUT'])
def update_vm(uuid):
    try:
        # Update VM settings
        vm_service = VirtualMachineService()
        success, message = vm_service.edit_vm(uuid, request.form)
        if not success:
            flash(f'Error updating VM: {message}', 'error')
            return jsonify({
                'success': success,
                'message': message
            })

        flash('VM configuration updated successfully', 'success')
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        flash(f'Error updating VM: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})


# @vm_bp.route('/create', methods=['GET', 'POST'])
# def create_vm():
#     if request.method == 'POST':
#         data = request.get_json()
#
#         config = VMConfig(
#             name=data.get('name'),
#             memory=int(data.get('memory', 2048)),
#             os_type=data.get('os_type')
#         )
#         vm_service = VirtualMachineService(config)
#         success, message = vm_service.create_vm()
#         return jsonify({'success': success, 'message': message})
#
#     return render_template('vms/create.html')


@vm_bp.route('/<uuid>', methods=['GET'])
def get_vm(uuid):
    vm_service = VirtualMachineService()
    success, result = vm_service.get_vm_by_uuid(uuid)
    if not success:
        flash(f'Error updating VM: {result}', 'error')
    return render_template('pages/edit_vm.html', vm=result)


@vm_bp.route('/<uuid>', methods=['DELETE'])
def delete_vm(uuid):
    delete_files = request.args.get('delete_files')

    if delete_files == 'true':
        delete_files = True

    vm_service = VirtualMachineService()
    success, message = vm_service.delete_vm(uuid, delete_files=delete_files)
    return jsonify({'success': success, 'message': message})


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


# @vm_bp.route('/list_vms', methods=['GET'])
# def list_vms():
#     vm_service = VirtualMachineService()  # No config needed for listing VMs
#     success, result = vm_service.get_all_vms()
#     print(result)
#     # time.sleep(10)
#     if success:
#         running_vms = []
#         stopped_vms = []
#         for vm in result:
#             print(vm)
#             status = vm.get('VMState')
#             vm['status'] = status
#             if status == 'running':
#                 running_vms.append(vm)
#             elif status == 'poweroff':
#                 stopped_vms.append(vm)
#
#         print(result)
#         print(stopped_vms)
#         print(running_vms)
#
#         return render_template('pages/list_vms.html', vms=result, stopped_vms=stopped_vms, running_vms=running_vms)
#     else:
#         # Handle error case
#         return render_template('pages/list_vms.html',
#                                error=result,
#                                running_vms=[],
#                                stopped_vms=[],
#                                vms=[])

@vm_bp.route('/list_vms', methods=['GET'])
def list_vms():
    try:
        # Call host service
        print('HOST_SERVICE_URL', HOST_SERVICE_URL)
        print('url', f'{HOST_SERVICE_URL}/api/vms/list')
        response = requests.get(f'{HOST_SERVICE_URL}/api/vms/list')
        data = response.json()

        if data['success']:
            running_vms = []
            stopped_vms = []
            for vm in data['vms']:
                status = vm.get('VMState')
                vm['status'] = status
                if status == 'running':
                    running_vms.append(vm)
                elif status == 'poweroff':
                    stopped_vms.append(vm)

            return render_template('pages/list_vms.html',
                                   vms=data['vms'],
                                   stopped_vms=stopped_vms,
                                   running_vms=running_vms)
        else:
            return jsonify({'success': False, 'message': data['message']})

    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'message': f"Failed to communicate with host service: {str(e)}"
        })


@vm_bp.route('/list_running_vms', methods=['GET'])
def list_running_vms():
    # Initialize loading state
    try:
        vm_service = VirtualMachineService()
        success, result = vm_service.get_all_running_vms()
        print(result)

        if success:
            return render_template('vms/list_running_vms.html',
                                   running_vms=result)
        else:
            return render_template('vms/list_running_vms.html',
                                   error=result,
                                   running_vms=[])

    except Exception as e:
        return render_template('vms/list_running_vms.html',
                               error=str(e),
                               running_vms=[])


@vm_bp.route('/<uuid>/screenshot', methods=['POST'])
def take_screenshot(uuid):
    try:
        vm_service = VirtualMachineService()
        success, result = vm_service.take_screenshot(uuid)

        if success:
            # Return the screenshot path
            return jsonify({
                'success': True,
                'screenshot_url': url_for('static', filename=f'screenshots/{os.path.basename(result)}')
            })
        else:
            return jsonify({
                'success': False,
                'message': result
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@vm_bp.route('/create', methods=['GET', 'POST'])
def create_vm():
    print(HOST_SERVICE_URL)
    if request.method == 'POST':
        try:
            data = request.get_json()
            response = requests.post(
                f'{HOST_SERVICE_URL}/api/vms/create',
                json=data
            )
            return response.json()
        except requests.RequestException as e:
            return jsonify({
                'success': False,
                'message': f"Failed to communicate with host service: {str(e)}"
            })

    return render_template('vms/create.html')

    # @vm_bp.route('/create', methods=['GET', 'POST'])
    # def create_vm():
    #     if request.method == 'POST':
    #         data = request.get_json()
    #
    #         config = VMConfig(
    #             name=data.get('name'),
    #             memory=int(data.get('memory', 2048)),
    #             os_type=data.get('os_type')
    #         )
    #         vm_service = VirtualMachineService(config)
    #         success, message = vm_service.create_vm()
    #         return jsonify({'success': success, 'message': message})
    #
    #     return render_template('vms/create.html')
