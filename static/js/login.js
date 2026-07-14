import { loginUser } from "../actions/auth.js";

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#formLogin');
    
    form.addEventListener('submit', async (e) => {
      e.preventDefault(); // evita recarregar a página
  
      const user = {
        email: document.getElementById('email').value,
        password: document.getElementById('senha').value,
      };
  
      try {
        await loginUser(user);
        
      } catch (error) {
        document.querySelector('#mensagem').innerText = 'Erro ao fazer login. Tente novamente.';
        console.error(error);
      }
    });
  });
