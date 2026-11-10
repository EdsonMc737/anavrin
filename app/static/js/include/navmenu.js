document.addEventListener("DOMContentLoaded", function () {

    const botao = document.querySelector("#navbarToggle");
    const menu = document.querySelector("#navbarMenu");

    if (!botao || !menu) {
        console.error("ANAVRIN: Navbar não encontrada!");
        return;
    }

    function toggleMenu() {
        const aberto = menu.classList.toggle("active");

        botao.classList.toggle("active", aberto);

        botao.setAttribute("aria-expanded", aberto);
        botao.setAttribute(
            "aria-label",
            aberto ? "Fechar menu" : "Abrir menu"
        );
    }

    function fecharMenu() {
        menu.classList.remove("active");
        botao.classList.remove("active");

        botao.setAttribute("aria-expanded", "false");
        botao.setAttribute("aria-label", "Abrir menu");
    }

    // Abrir e fechar pelo botão
    botao.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();

        toggleMenu();
    });

    // Fechar ao clicar em algum link
    menu.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", fecharMenu);
    });

    // Fechar ao clicar fora
    document.addEventListener("click", function (event) {

        if (
            menu.classList.contains("active") &&
            !menu.contains(event.target) &&
            !botao.contains(event.target)
        ) {
            fecharMenu();
        }

    });

    // Fechar com ESC
    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            fecharMenu();
        }

    });

});