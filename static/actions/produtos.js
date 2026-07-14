// /actions/produtos.js
import api from "./axiosconf.js";
let paginaAtual = 0; // Variável para controlar a página atual
const limitePorPagina = 10; // Número de produtos por página

export function proximaPagina() {
  paginaAtual++;
  listarProdutos();
}

// Para página anterior
export function paginaAnterior() {
  if (paginaAtual > 0) {
    paginaAtual--;
    listarProdutos();
  }
}



export async function listarProdutos() {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try {
    const response = await api.get("/products", {
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
    
export async function cadastrarProduto(produto) {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try {
    const response= await api.post("/products", produto, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });
    if (response.status === 201) {
      console.log("Produto cadastrado com sucesso:", response.data);
      return response.data; // Retorna o produto cadastrado
    } else {
     // console.error("Deu ruim:", response.data.error);
      throw new Error("Erro ao cadastrar produto", response.data.erro);
    }
}catch (error) {
   // console.error("Erro:", error);
    throw new Error(error.response?.data?.erro || "Erro ao cadastrar produto");
  }

}


export async function deletarProduto(id) {
  const token= document.cookie.split('; ').find(row => row.startsWith('token-user=')).split('=')[1];
  try{
    const response= await api.delete(`/products/${id}`, {
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });
    if (response.status === 200) {
      console.log("Produto deletado com sucesso:", response.data);
      return response.data; // Retorna o produto deletado
    } else {
      console.error("Erro ao deletar produto:", response.data.error);
      throw new Error("Erro ao deletar produto:", response.data.erro);
    }

  }
  catch (error) {
    console.error("Erro:", error);
    throw new Error(error.response?.data?.erro || "Erro ao deletar produto");
  }  
  
}