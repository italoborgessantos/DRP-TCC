// /actions/produtos.js
import api from "./axiosconf.js";

let paginaAtual = 0; // Variável para controlar a página atual
const limitePorPagina = 10; // Número de clientes por página

export function proximaPagina() {
  paginaAtual++;
  listarClientes();
}

// Para página anterior
export function paginaAnterior() {
  if (paginaAtual > 0) {
    paginaAtual--;
    listarClientes();
  }
}


export async function listarClientes() {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try {
    const response = await api.get("/clients", {
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      params: {
        limit: limitePorPagina,
        offset: paginaAtual * limitePorPagina,
      },
    });
    if (response.status === 200) {
       console.log(response.data)
       return response.data; // Retorna os produtos
       
    }
    else {
     // console.error("Erro ao listar produtos :", response);
      throw new Error("Erro ao listar produtos");
    }
    
  } catch (error) {
   // console.error("Erro ao listar produtos :", error);
   throw new Error(error.response?.data?.erro || "Erro ao cadastrar produto"); // Repropaga o erro para tratamento posterior
  }
}
    

export async function cadastrarCliente(cliente) {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try {
    const response= await api.post("/clients", cliente, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });
    if (response.status === 201) {
      console.log("Cliente cadastrado com sucesso:", response.data);
      return response.data; // Retorna o produto cadastrado
    } else {
     // console.error("Deu ruim:", response.data.error);
      throw new Error("Erro ao cadastrar cliente", response.data.erro);
    }
}catch (error) {
   // console.error("Erro:", error);
    throw new Error(error.response?.data?.erro || "Erro ao cadastrar cliente");
  }

}

export async function deletarCliente(id) {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try{
    const response= await api.delete(`/clients/${id}`, {
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });
    if (response.status === 200) {
      console.log("Cliente deletado com sucesso:", response.data);
      return response.data; // Retorna o produto deletado
    } else {
      console.error("Erro ao deletar cliente:", response.data.error);
      throw new Error("Erro ao deletar cliente", response.data.erro);
    }

  }
  catch (error) {
    console.error("Erro:", error);
    throw new Error(error.response?.data?.erro || "Erro ao deletar cliente");
  }  
  
}
