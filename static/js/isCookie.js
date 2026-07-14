

isAuthenticated()
function isAuthenticated() {
    const tokenCookie = document.cookie.split('; ').find(row => row.startsWith('token-user='));

    // Se o cookie não existir, redireciona para o login
    if (!tokenCookie) {
        window.location.href = "/";
        return;
    }

    // Pega o valor do token após o '='
    const token = tokenCookie.split('=')[1];

    // Se o token estiver ausente, redireciona para o login
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const decoded = jwt_decode(token);
        const now = Date.now() / 1000;
        if (decoded.exp > now) {
            return true;
        }
    } catch (err) {
        return false;
    }
}
