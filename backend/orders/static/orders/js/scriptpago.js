// scriptpago.js

// Función para leer la cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
            }
        });
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = getCookie('csrftoken');

    // 1. Cargar y mostrar resumen del carrito
    const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    const listaCarrito     = document.getElementById("lista-carrito");
    const precioElemento   = document.getElementById("precio");
    const impuestoElemento = document.getElementById("impuesto");
    const totalElemento    = document.getElementById("total");

    let subtotal = 0;
    listaCarrito.innerHTML = "";

    carrito.forEach(item => {
        const precio   = parseFloat(item.precio) || 0;
        const cantidad = parseInt(item.cantidad) || 0;
        const li = document.createElement("li");
        li.textContent = `* ${item.nombre} (x${cantidad}) – $${precio.toFixed(2)}`;
        listaCarrito.appendChild(li);
        subtotal += precio * cantidad;
    });

    const impuesto = subtotal * 0.035;
    const total    = subtotal + impuesto;

    precioElemento.textContent   = `$${subtotal.toFixed(2)}`;
    impuestoElemento.textContent = `$${impuesto.toFixed(2)}`;
    totalElemento.textContent    = `$${total.toFixed(2)}`;

    // 2. Capturar envío del formulario
    const form = document.getElementById("pedido-form");
    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const nombre    = document.getElementById("nombre").value.trim();
        const telefono  = document.getElementById("telefono").value.trim();
        const direccion = document.getElementById("direccion").value.trim();

        // Validaciones
        if (!nombre || !telefono || !direccion) {
            alert("Por favor completa todos los campos.");
            return;
        }
        if (!/^\d+$/.test(telefono)) {
            alert("El número de teléfono solo debe contener dígitos.");
            return;
        }

        // Preparar el payload para la API
        const items = carrito.map(item => ({
            dish:       parseInt(item.id, 10),
            quantity:   parseInt(item.cantidad, 10),
            unit_price: parseFloat(item.precio)
        }));

        const payload = {
            customer_name: nombre,
            phone:         telefono,
            address:       direccion,
            items:         items
        };

        // Llamada a la API Django con credenciales y CSRF
        fetch("/api/orders/", {
            method:  "POST",
            credentials: "same-origin",       // envía cookies de sesión
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken":  csrftoken    // token CSRF
            },
            body:    JSON.stringify(payload)
        })
        .then(res => {
            if (!res.ok) throw new Error(`Error ${res.status}`);
            return res.json();
        })
        .then(order => {
            alert(`¡Pedido #${order.id} registrado con éxito!`);
            localStorage.removeItem("carrito");
            window.location.href = "/mis-pedidos/";
        })
        .catch(err => {
            console.error("Error al enviar pedido:", err);
            alert("Hubo un problema al procesar tu pedido. Inténtalo de nuevo.");
        });
    });
});

// Función de cancelación
function cancelarPedido() {
    window.location.href = "/menu/";
}
