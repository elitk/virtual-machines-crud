from flask import Flask, jsonify, request
from app.vms.service import VirtualMachineService
from app.vms.config import VMConfig

app = Flask(__name__)


@app.route('/api/vms/create', methods=['POST'])
def create_vm():
    try:
        data = request.get_json()
        config = VMConfig(
            name=data.get('name'),
            memory=int(data.get('memory', 2048)),
            os_type=data.get('os_type')
        )
        vm_service = VirtualMachineService(config)
        success, message = vm_service.create_vm()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/api/vms/list', methods=['GET'])
def list_vms():
    try:
        vm_service = VirtualMachineService()
        success, vms = vm_service.get_all_vms()
        return jsonify({
            'success': success,
            'vms': vms if success else [],
            'message': 'Failed to get VMs' if not success else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'vms': [],
            'message': str(e)
        })


if __name__ == '__main__':
    print('server running')
    app.run(port=5001)

