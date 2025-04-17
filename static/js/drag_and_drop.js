document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.querySelector('#drop-zone');
    const logFile = document.querySelector('#uploaded_log');

    dropZone.addEventListener("click", () => { logFile.click(); })

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = "#f0f0f0";
    })

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.backgroundColor = "";
    })

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = "";

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            logFile.files = files;
            dropZone.textContent = `File selected: ${files[0].name}`
        }
    })

    logFile.addEventListener("change", () => {
        const files = logFile.files
        if (files.length > 0) {
            dropZone.textContent = `File selected: ${files[0].name}`
        } else {
            dropZone.textContent = 'Drag & drop log file here or click to choose'
        }
    })
})