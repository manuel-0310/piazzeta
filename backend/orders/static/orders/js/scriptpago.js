document.addEventListener("DOMContentLoaded", () => {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    let listaCarrito = document.getElementById("lista-carrito");
    let precioElemento = document.getElementById("precio");
    let impuestoElemento = document.getElementById("impuesto");
    let totalElemento = document.getElementById("total");

    let subtotal = 0;
    listaCarrito.innerHTML = "";

    carrito.forEach(item => {
        let precio = parseFloat(item.precio) || 0;
        let cantidad = parseInt(item.cantidad) || 0;
        let li = document.createElement("li");
        li.textContent = `* ${item.nombre} (${cantidad}) - $${precio.toFixed(2)}`;
        listaCarrito.appendChild(li);
        subtotal += precio * cantidad;
    });

    let impuesto = subtotal * 0.035;
    let total = subtotal + impuesto;

    precioElemento.textContent = `$${subtotal.toFixed(2)}`;
    impuestoElemento.textContent = `$${impuesto.toFixed(2)}`;
    totalElemento.textContent = `$${total.toFixed(2)}`;
});

function cancelarPedido() {
    window.location.href = "menu.html";
}

document.getElementById("pedido-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const nombre = document.getElementById("nombre").value.trim();
    const telefono = document.getElementById("telefono").value.trim();
    const direccion = document.getElementById("direccion").value.trim();

    if (!/^\d+$/.test(telefono)) {
        alert("El número de teléfono solo debe contener dígitos.");
        return;
    }
    
    if (!nombre || !telefono || !direccion) {
        alert("Por favor completa todos los campos.");
        return;
    }

    const carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    const productos = carrito.map(item => ({
        id: item.id,
        nombre: item.nombre,
        precio: parseFloat(item.precio) || 0,
        cantidad: parseInt(item.cantidad) || 1
    }));

    const subtotal = productos.reduce((acc, p) => acc + (p.precio * p.cantidad), 0);
    const impuesto = subtotal * 0.035;
    const total = subtotal + impuesto;

    const pedido = {
        Fecha: new Date().toLocaleString(), 
        Cliente: nombre,
        Teléfono: telefono,
        Dirección: direccion,
        Productos: JSON.stringify(productos), 
        Total: parseFloat(total.toFixed(2))
    };

    // Enviar datos a Sheet.best
    fetch("https://api.sheetbest.com/sheets/f42c6560-2895-4daf-ab04-aeeb6b109672", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(pedido)
    })
    .then(res => res.json())
    .then(data => {
        alert("¡Pedido enviado con éxito!");
        localStorage.removeItem("carrito");
        window.location.href = "menu.html";
    })
    .catch(err => {
        console.error("Error al enviar pedido:", err);
        alert("Hubo un problema al enviar el pedido.");
    });
});

