# from flask import Blueprint, request, redirect, url_for, flash
# from app.services import VirtualMachineService
# from app.config import VMConfig, VMStorageController
# import logging
#
# logger = logging.getLogger(__name__)
# vm_bp = Blueprint('vm', __name__)
#
#
# @vm_bp.route('/create-vm', methods=['POST'])
# def create_vm():
#     try:
#         # Get parameters from form
#         name = request.form.get('name', 'Kali')
#         memory = int(request.form.get('memory', 2048))
#         os_type = request.form.get('os_type', 'Ubuntu')
#
#         config = VMConfig(
#             name=name,
#             memory=memory,
#             os_type=os_type
#         )
#
#         vm_service = VirtualMachineService(config)
#         success, message = vm_service.create_vm()
#
#         if success:
#             flash("Virtual Machine created successfully!", "success")
#             return redirect(url_for('index'))
#         else:
#             flash(f"Failed to create Virtual Machine: {message}", "error")
#             return redirect(url_for('create'))
#
#     except Exception as e:
#         logger.error(f"Unexpected error during VM creation: {str(e)}", exc_info=True)
#         flash(f"An unexpected error occurred: {str(e)}", "error")
#         return redirect(url_for('create'))