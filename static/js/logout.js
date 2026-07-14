import {logout} from "../actions/auth.js";

function getToken() {
    const tokenCookie = document.cookie.split('; ').find(row => row.startsWith('token-user='));
    return tokenCookie ? tokenCookie.split('=')[1] : null;
  }
  
  function getInitials(fullName) {
    const names = fullName.trim().split(" ");
    if (names.length === 1) return names[0].charAt(0).toUpperCase();
    return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
  }

document.addEventListener('DOMContentLoaded', () => { 
    document.getElementById("Logoutbtn").addEventListener("click", async () => {
        try {
        await logout();

        } catch (error) {
        console.error("Erro ao fazer logout:", error);
        }
    });

    const token = getToken();
    if (token) {
        try {
        const decoded = jwt_decode(token);
        console.log(decoded);
        const nome = decoded.name;
        const iniciais = getInitials(nome);
        document.getElementById("iniciaisPerfil").textContent = iniciais;
        } catch (err) {
        console.error("Erro ao decodificar token:", err);
        }
    }
        else {
            console.log("Token não encontrado.");
        }

});




