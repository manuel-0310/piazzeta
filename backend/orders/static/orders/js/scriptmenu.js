// scriptmenu.js

document.addEventListener("DOMContentLoaded", () => {
    // Mapeo de categorías a los contenedores de tu HTML
    const categorias = {
        "Entradas": document.getElementById("menu-entradas"),
        "Pizzas":   document.getElementById("menu-Pizzas"),
        "Bebidas":  document.getElementById("menu-Bebidas"),
        "Postres":  document.getElementById("menu-Postres")
    };

    // Elementos del carrito
    const listaCarrito     = document.querySelector(".lista-carrito");
    const precioElemento   = document.querySelector(".precio");
    const impuestoElemento = document.querySelector(".impuesto");
    const totalElemento    = document.querySelector(".total");
    const taxSection       = document.querySelector(".tax-section");

    // Recuperar carrito guardado (o inicializar vacío)
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    // 1. Cargar platos desde la API Django
    fetch("/api/dishes/")
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(dishes => {
            dishes.forEach(dish => {
                // ── transforma la URL de imagen como en tu JS antiguo ──
                let imgSrc = "";
                if (dish.image_url) {
                    imgSrc = dish.image_url.trim();
                    if (imgSrc.includes("imgur.com")) {
                        imgSrc = imgSrc
                            .replace("https://imgur.com/", "https://i.imgur.com/")
                            .replace("http://imgur.com/",  "https://i.imgur.com/");
                        if (!imgSrc.match(/\.(png|jpe?g|gif)$/i)) {
                            imgSrc += ".png";
                        }
                    }
                }

                // Construir la tarjeta del plato
                const card = document.createElement("section");
                card.className = "menu-item";
                card.innerHTML = `
                    <div class="image-container">
                        <img
                          src="${imgSrc}"
                          alt="${dish.name}"
                          loading="lazy"
                          onerror="this.src='{% static 'orders/img/placeholder.png' %}'"
                        >
                    </div>
                    <h3>${dish.name}</h3>
                    <p class="description">${dish.description}</p>
                    <p class="price">$${parseFloat(dish.price).toFixed(2)}</p>
                    <button
                      class="add-to-cart"
                      data-id="${dish.id}"
                      data-nombre="${dish.name}"
                      data-precio="${parseFloat(dish.price)}"
                    >+</button>
                `;

                // Insertar en la categoría correspondiente
                if (categorias[dish.category]) {
                    categorias[dish.category].appendChild(card);
                }
            });

            // Después de renderizar, enganchar los listeners de "Agregar"
            document.querySelectorAll(".add-to-cart").forEach(button => {
                button.addEventListener("click", () => {
                    const id     = button.dataset.id;
                    const nombre = button.dataset.nombre;
                    const precio = parseFloat(button.dataset.precio);

                    const existente = carrito.find(item => item.id === id);
                    if (existente) {
                        existente.cantidad++;
                    } else {
                        carrito.unshift({ id, nombre, precio, cantidad: 1 });
                    }
                    actualizarCarrito();
                });
            });
        })
        .catch(err => {
            console.error("Error cargando menú:", err);
            // Mostrar mensaje de error en cada sección
            Object.values(categorias).forEach(container => {
                container.innerHTML = "<p>Error al cargar el menú. Intenta más tarde.</p>";
            });
        });

    // 2. Botón de procesar compra
    document.querySelector(".buy").addEventListener("click", event => {
        if (carrito.length === 0) {
            event.preventDefault();
            alert("Debes agregar al menos un producto antes de enviar el pedido.");
        } else {
            taxSection.classList.remove("hidden");
            enviarPedido();
        }
    });

    // 3. Botón de limpiar carrito
    document.querySelector(".delate").addEventListener("click", () => {
        carrito = [];
        taxSection.classList.add("hidden");
        actualizarCarrito();
    });

    // Función para actualizar la UI del carrito
    function actualizarCarrito() {
        listaCarrito.innerHTML = "";
        let precioTotal = 0;

        carrito.forEach((item, index) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span class="nombre-producto">${item.nombre} ($${item.precio.toFixed(2)})</span>
                <span class="cantidad">x${item.cantidad}</span>
                <button class="eliminar-item" data-index="${index}">🗑️</button>
            `;
            listaCarrito.appendChild(li);
            precioTotal += item.precio * item.cantidad;
        });

        const tax   = (precioTotal * 0.035).toFixed(2);
        const total = (precioTotal + parseFloat(tax)).toFixed(2);

        precioElemento.textContent   = `$${precioTotal.toFixed(2)}`;
        impuestoElemento.textContent = `$${tax}`;
        totalElemento.textContent    = `$${total}`;

        // Guardar en localStorage
        localStorage.setItem("carrito", JSON.stringify(carrito));

        // Enganchar evento para eliminar cada ítem
        document.querySelectorAll(".eliminar-item").forEach(button => {
            button.addEventListener("click", () => {
                const idx = parseInt(button.dataset.index, 10);
                carrito.splice(idx, 1);
                actualizarCarrito();
            });
        });
    }

    // Función para preparar el pedido y pasar parámetros a la vista de pago
    function enviarPedido() {
        const params = new URLSearchParams();
        carrito.forEach((item, i) => {
            params.append(`producto${i}`, `${item.nombre}(${item.cantidad})`);
        });
        params.append("total", totalElemento.textContent);
        window.history.pushState({}, "", `?${params.toString()}`);
    }

    // Inicializar carrito al cargar la página
    actualizarCarrito();
});
