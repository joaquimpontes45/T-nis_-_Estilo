function confirmLogout() {
    if (confirm("Você confirma que deseja sair?")) {
        window.location.href = "/logout"; // Redirecionamento direto para a rota de logout
    }
}