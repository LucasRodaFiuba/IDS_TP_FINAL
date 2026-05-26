function cambiarPaso(actual, siguiente) {
    if (siguiente > actual) {
        const bloqueActual = document.getElementById(`bloque-${actual}`);
        const campos = bloqueActual.querySelectorAll('input, select');
        
        for (let campo of campos) {
            if (!campo.checkValidity()) {
                campo.reportValidity();
                return;
            }
        }
    }

    document.getElementById(`bloque-${actual}`).classList.remove('activo');
    document.getElementById(`bloque-${siguiente}`).classList.add('activo');

    for (let i = 1; i <= 4; i++) {
        const nodo = document.getElementById(`nodo-${i}`);
        if (nodo) {
            if (i <= siguiente) {
                nodo.classList.add('activo');
            } else {
                nodo.classList.remove('activo');
            }
        }
    }
}