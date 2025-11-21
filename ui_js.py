# ui_js.py

DRAG_DROP_SCRIPT = """
<script>
(function() {
    // Esta función se engancha al DOM padre de Streamlit
    function attachDragListeners() {
        try {
            const parentDoc = window.parent.document;
            if (!parentDoc) return;

            const dropzones = parentDoc.querySelectorAll('div[data-testid="stFileDropzone"]');
            if (!dropzones || dropzones.length === 0) {
                return;
            }

            dropzones.forEach(function(dz) {
                if (dz.getAttribute("data-drag-listener") === "true") {
                    return;
                }
                dz.setAttribute("data-drag-listener", "true");

                dz.addEventListener("dragenter", function(e) {
                    dz.classList.add("drag-active");
                });

                dz.addEventListener("dragover", function(e) {
                    e.preventDefault();
                    dz.classList.add("drag-active");
                });

                dz.addEventListener("dragleave", function(e) {
                    dz.classList.remove("drag-active");
                });

                dz.addEventListener("drop", function(e) {
                    dz.classList.remove("drag-active");
                });
            });
        } catch (err) {
            console.error("Error attaching drag listeners:", err);
        }
    }

    // Ejecutar una vez
    attachDragListeners();

    // Observar cambios en el DOM de Streamlit (por rerenders)
    try {
        const parentDoc = window.parent.document;
        const observer = new MutationObserver(function() {
            attachDragListeners();
        });
        observer.observe(parentDoc.body, { childList: true, subtree: true });
    } catch (err) {
        console.error("Error creating MutationObserver:", err);
    }
})();
</script>
"""
