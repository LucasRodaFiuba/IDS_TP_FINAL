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
    for (let i = 1; i <= 5; i++) {
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

function buscarHorarios() {
    const inputFecha = document.getElementById('fecha_reserva');
    const inputComensales = document.getElementById('cantidad_personas');

    const fechaElegida = inputFecha.value;
    const comensales = inputComensales.value;

    window.location.href = `/reservas?fecha=${fechaElegida}&comensales=${comensales}`;
}