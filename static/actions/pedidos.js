import api from "./axiosconf.js";


let paginaAtual = 0; // Variável para controlar a página atual
const limitePorPagina = 10; // Número de clientes por página

export function proximaPagina() {
  paginaAtual++;
  listarPedidos();
}

// Para página anterior
export function paginaAnterior() {
  if (paginaAtual > 0) {
    paginaAtual--;
    listarPedidos();
  }
}


export async function listarPedidos() {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try {
    const response = await api.get("/orders", {
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
       return response.data; // Retorna os pedidos
       
    }
    else {
     // console.error("Erro ao listar produtos :", response);
      throw new Error("Erro ao listar pedidos");
    }
    
  } catch (error) {
   // console.error("Erro ao listar produtos :", error);
   throw new Error(error.response?.data?.erro || "Erro ao cadastrar pedido"); // Repropaga o erro para tratamento posterior
  }
}
    

export async function cadastrarPedido(pedido) {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try {
    const response= await api.post("/orders", pedido, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });
    if (response.status === 201) {
      console.log("Pedido cadastrado com sucesso:", response.data);
      return response.data; // Retorna o produto cadastrado
    } else {
     // console.error("Deu ruim:", response.data.error);
      throw new Error("Erro ao cadastrar pedido", response.data.erro);
    }
}catch (error) {
   // console.error("Erro:", error);
    throw new Error(error.response?.data?.erro || "Erro ao cadastrar pedido");
  }

}


export async function deletarPedido(id) {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try{
    const response= await api.delete(`/orders/${id}`, {
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });
    if (response.status === 200) {
      console.log("Pedido deletado com sucesso:", response.data);
      return response.data; // Retorna o produto deletado
    } else {
      console.error("Erro ao deletar Pedido:", response.data.error);
      throw new Error("Erro ao deletar Pedido:", response.data.erro);
    }

  }
  catch (error) {
    console.error("Erro:", error);
    throw new Error(error.response?.data?.erro || "Erro ao deletar pedido");
  }  
  
}
