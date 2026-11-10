
document.addEventListener("DOMContentLoaded", function () {

    const fotos = Array.from(
        document.querySelectorAll(".editorial-photo")
    );

    const modal = document.getElementById("anavrinLightbox");

    // Sem modal ou fotografias, mantém a galeria funcionando normalmente.
    if (!modal || fotos.length === 0) {
        console.warn("Lightbox: modal ou fotografias não encontrados.");
        return;
    }

    const imagemModal = document.getElementById("lightboxImage");
    const descricaoModal = document.getElementById("lightboxDescription");
    const contadorModal = document.getElementById("lightboxCounter");

    const botaoFechar = document.getElementById("lightboxClose");
    const botaoAnterior = document.getElementById("lightboxPrev");
    const botaoProximo = document.getElementById("lightboxNext");

    // Verifica se todos os elementos necessários existem.
    if (
        !imagemModal ||
        !descricaoModal ||
        !contadorModal ||
        !botaoFechar ||
        !botaoAnterior ||
        !botaoProximo
    ) {
        console.error("Lightbox: faltam elementos no HTML do modal.");
        return;
    }

    let indiceAtual = 0;
    let elementoAnterior = null;

    function atualizarImagem() {
        const foto = fotos[indiceAtual];
        const imagem = foto.querySelector("img");
        const legenda = foto.querySelector("figcaption");

        if (!imagem) return;

        imagemModal.src = imagem.src;
        imagemModal.alt = imagem.alt;

        descricaoModal.textContent = legenda
            ? legenda.textContent.trim()
            : imagem.alt;

        contadorModal.textContent =
            String(indiceAtual + 1).padStart(2, "0") +
            " / " +
            String(fotos.length).padStart(2, "0");
    }

    function abrirModal(indice) {
        elementoAnterior = document.activeElement;
        indiceAtual = indice;

        atualizarImagem();

        modal.classList.add("active");
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";

        botaoFechar.focus();
    }

    function fecharModal() {
        modal.classList.remove("active");
        modal.setAttribute("aria-hidden", "true");

        document.body.style.overflow = "";
        imagemModal.removeAttribute("src");

        if (elementoAnterior) {
            elementoAnterior.focus();
        }
    }

    function proximaFoto() {
        indiceAtual = (indiceAtual + 1) % fotos.length;
        atualizarImagem();
    }

    function fotoAnterior() {
        indiceAtual = (indiceAtual - 1 + fotos.length) % fotos.length;
        atualizarImagem();
    }

    fotos.forEach(function (foto, indice) {
        foto.style.cursor = "zoom-in";
        foto.setAttribute("tabindex", "0");
        foto.setAttribute("role", "button");

        foto.addEventListener("click", function () {
            abrirModal(indice);
        });

        foto.addEventListener("keydown", function (evento) {
            if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                abrirModal(indice);
            }
        });
    });

    botaoFechar.addEventListener("click", fecharModal);
    botaoProximo.addEventListener("click", proximaFoto);
    botaoAnterior.addEventListener("click", fotoAnterior);

    modal.addEventListener("click", function (evento) {
        if (evento.target === modal) {
            fecharModal();
        }
    });

    document.addEventListener("keydown", function (evento) {
        if (!modal.classList.contains("active")) return;

        if (evento.key === "Escape") fecharModal();

        if (evento.key === "ArrowRight") proximaFoto();

        if (evento.key === "ArrowLeft") fotoAnterior();
    });

    let toqueInicialX = 0;

    modal.addEventListener("touchstart", function (evento) {
        toqueInicialX = evento.changedTouches[0].screenX;
    }, { passive: true });

    modal.addEventListener("touchend", function (evento) {
        const toqueFinalX = evento.changedTouches[0].screenX;
        const diferenca = toqueFinalX - toqueInicialX;

        if (Math.abs(diferenca) < 50) return;

        if (diferenca < 0) {
            proximaFoto();
        } else {
            fotoAnterior();
        }
    }, { passive: true });

});
