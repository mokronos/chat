document.addEventListener('DOMContentLoaded', function() {

    document.body.addEventListener('htmx:beforeSwap', function(evt) {
        // Allow 422 and 400 responses to swap
        // We treat these as form validation errors
        if (evt.detail.xhr.status === 400 ||
            evt.detail.xhr.status === 401 ||
            evt.detail.xhr.status === 409 ||
            evt.detail.xhr.status === 422) {

            evt.detail.shouldSwap = true;
            evt.detail.isError = false;
        }
    });
});
