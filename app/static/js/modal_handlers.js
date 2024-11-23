
    // TODO: Add function to close modal on overlay click
function closeModalOnOverlayClick(event) {
    // Check if click was on the overlay itself (not its children)
    if (event.target === event.currentTarget) {
        closeModal();
    }
}
// Function to close modal
function closeModal() {
    const modal = document.getElementById('vmInfoModal');
    modal.classList.add('hidden');
}

 // Add escape key to close
document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });


function openCreateModal() {
    document.getElementById('createVMModal').classList.remove('hidden');
}

function closeCreateModal() {
    document.getElementById('createVMModal').classList.add('hidden');
}
