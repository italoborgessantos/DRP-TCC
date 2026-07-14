import api from './axiosconf.js';


export async function createUser(user) {
  try {
    const response = await api.post('auth', user, {
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
      },
    });
    if (response.status === 201) {
      const token = response.data.token;
      
      document.cookie = `token-user=${token}; path=/; max-age=3600`;
  
      // Redirecionar para o dashboard
      window.location.href = '/dashboard';
  } else {
      console.error("Erro ao obter o token:", response);
  }
    

    // Redirecionar
    
  } catch (error) {
    console.error("Erro ao criar usuário:", error);
    if(error.response.data.error){
      alert(error.response.data.error);
    }
    if (error.response && error.response.status === 403) {
      alert(error.response.data.error);
    } else {
      alert(error);
    }
  }
  
}

export async function logout() {
  // Limpa o cookie do token
  document.cookie = "token-user=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
  
  // Redireciona para a tela de login
  window.location.href = "/"; // ou o caminho que quiser
}

export async function loginUser(user) {
    try {
        const response = await api.post('auth/login', user, {
        headers: {
            'Content-Type': 'application/json; charset=UTF-8',
            
        },
        });
        if(response.status === 200) {

        const token = response.data.token;
        console.log(token);
    
        // Salvar token em cookie (válido por 1 hora, por exemplo)
        document.cookie = `token-user=${token}; path=/; max-age=3600`;
    
        // Redirecionar
        window.location.href = '/dashboard';
        }
        else {
            console.error("Erro ao obter o token:", response);
        }
    } catch (error) {
       console.log(error.response.data.error);
        if (error.response && error.response.status === 403) {
           alert(error.response.data.error);
        } else {
           alert('Erro ao fazer login. Tente novamente.');
        }
    }
}