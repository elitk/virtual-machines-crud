function startVM(uuid) {
        if (confirm('Are you sure you want to start this VM?')) {
            fetch(`/vms/${uuid}/start`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Failed to start VM');
                    }
                });
        }
    }
function stopVM(uuid) {
                console.log('VM Data:', uuid); // For debugging

        if (confirm('Are you sure you want to stop this VM?')) {
            fetch(`/vms/${uuid}/stop`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('Response Data:', data); // For debugging
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Failed to stop VM');
                    }
                });
        }
    }
function showVMInfo(vm) {
        console.log('VM Data:', vm);

        const { name, status, uuid, memory, cpus, os_type } = vm;
        const modal = document.getElementById('vmInfoModal');
        const modalContent = document.getElementById('modal-content');
        const modalTitle = document.getElementById('modal-title');

        // Update modal title
        modalTitle.textContent = `VM Information: ${name}`;

        // Create content HTML with additional fields
        const contentHtml = `
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div class="space-y-3">
                    <div>
                        <label class="block text-gray-500 text-xs">Name</label>
                        <span class="text-gray-900">${name}</span>
                    </div>
                    <div>
                        <label class="block text-gray-500 text-xs">Status</label>
                        <span class="text-gray-900">${status}</span>
                    </div>
                    <div>
                        <label class="block text-gray-500 text-xs">UUID</label>
                        <span class="text-gray-900 font-mono text-xs break-all">${uuid}</span>
                    </div>
                    <div>
                        <label class="block text-gray-500 text-xs">Memory</label>
                        <span class="text-gray-900">${memory} MB</span>
                    </div>
                    <div>
                        <label class="block text-gray-500 text-xs">CPUs</label>
                        <span class="text-gray-900">${cpus}</span>
                    </div>
                    <div>
                        <label class="block text-gray-500 text-xs">OS Type</label>
                        <span class="text-gray-900">${os_type}</span>
                    </div>
                </div>
            </div>
        `;

        modalContent.innerHTML = contentHtml;
        modal.classList.remove('hidden');

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
function get_vm_status(status){
     const statusStyles = {
            'running': {
                class: 'bg-green-100 text-green-800',
                text: 'Running'
            },
            'poweroff': {
                class: 'bg-red-100 text-red-800',
                text: 'Stopped'
            },
            'paused': {
                class: 'bg-yellow-100 text-yellow-800',
                text: 'Paused'
            },
            'saved': {
                class: 'bg-blue-100 text-blue-800',
                text: 'Saved'
            },
            'aborted': {
                class: 'bg-gray-100 text-gray-800',
                text: 'Aborted'
            },
            'unknown': {
                class: 'bg-gray-100 text-gray-800',
                text: 'Unknown'
            }
        };
     const statusStyle = statusStyles[status?.toLowerCase()] || statusStyles.unknown;

     return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyle.class}">
            ${statusStyle.text}
             </span>`;
}
function deleteVM(uuid) {
        if (confirm('Are you sure you want to delete this VM? This cannot be undone.')) {
            fetch(`/vms/${uuid}?delete_files=true`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Failed to delete VM: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error deleting VM: ' + error);
            });
        }
    }
function submitCreateVM() {
        const form = document.getElementById('createVMForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        fetch('/vms/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeCreateModal();
                window.location.reload();
            } else {
                alert('Failed to create VM: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error creating VM: ' + error);
        });
    }

