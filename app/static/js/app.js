document.addEventListener('DOMContentLoaded', () => {
    console.log("Script loaded and DOM is ready");
    setTimeout(() => {
        console.log("DOM is ready and fully loaded");

    const contentContainer = document.getElementById('vm-content');
    const loadingSkeleton = document.getElementById('loading-skeleton');

    // Check if the data has been loaded
    if (contentContainer.querySelectorAll('*').length > 0) {
        // Data is loaded, hide the skeleton loader
            loadingSkeleton.classList.add('hidden');
            contentContainer.classList.remove('hidden');

        // setTimeout(() => {
        // }, );
    } else {
        // Data is not loaded yet, show the skeleton loader
        loadingSkeleton.classList.remove('hidden');
        contentContainer.classList.add('hidden');

    }}   , 2000);

});