import { createUser } from "../actions/auth.js";

document.addEventListener('DOMContentLoaded', () => {
    
    const form = document.querySelector('#formCadastro');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault(); // evita recarregar a página

      const user = {
        name: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('telefone').value,
        password : document.getElementById('senha').value
        
      };

  
      try {
        await createUser(user);
        
      } catch (error) {
        console.error(error);
      }
    });
  });
