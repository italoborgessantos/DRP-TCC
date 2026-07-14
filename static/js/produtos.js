import { listarProdutos,cadastrarProduto, deletarProduto, proximaPagina, paginaAnterior } from "../actions/produtos.js";
function getMensagemDeErro(error) {
  if (error.response) {
    return error.response.data.erro || "Erro desconhecido";
  } else if (error.request) {
    return "Erro de conexão com o servidor";
  } else {
    return error.message || "Erro inesperado";
  }
}
async function renderizarTabela() {
  const tabela = document.getElementById("tabela-produtos");
  if (tabela) {
    try {
      const produtos = await listarProdutos();
      tabela.innerHTML = "";

      if (!produtos || produtos.length === 0) {
        tabela.innerHTML = "<tr><td colspan='7'>Nenhum produto encontrado.</td></tr>";
        return;
      }

      produtos.forEach((p) => {
        tabela.innerHTML += `
          <tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.category}</td>
            <td>${p.description}</td>
            <td>R$ ${p.price}</td>
            <td>${p.stock}</td>
            <td>
              <button class="deletarProduto btn btn-sm btn-outline-danger">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        `;
      });

      const paginacao = document.getElementById("paginacao");
      paginacao.innerHTML = `
        <button id="btnAnterior" class="mb-0"><i class="bi bi-arrow-left-square"></i> Anterior</button>
        <button id="btnProxima" class="ml-auto"><i class="bi bi-arrow-right-square"></i> Próxima</button>
      `;

      document.getElementById("btnAnterior").addEventListener("click", paginaAnt);
      document.getElementById("btnProxima").addEventListener("click", proxPagina);

      await addEventosDeletar();

    } catch (error) {
      console.error("Erro ao listar produtos :", error);
    }
  }
}


async function proxPagina() {
  proximaPagina();
  await renderizarTabela();
}


async function paginaAnt() {
  paginaAnterior();
  await renderizarTabela();
}


async function addEventosDeletar() {
  const deletarProdutosBtn = document.querySelectorAll(".deletarProduto");
  deletarProdutosBtn.forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const id = e.target.closest("tr").querySelector("td").innerText;
      try {
        await deletarProduto(id);
        await Swal.fire({
          title: 'Sucesso!',
          text: 'Produto deletado com sucesso.',
          icon: 'success',
          confirmButtonText: 'OK'
        });
        await renderizarTabela(); 
      } catch (error) {
        console.error(error);
        Swal.fire({
          title: 'Erro!',
          text: getMensagemDeErro(error),
          icon: 'error',
          confirmButtonText: 'OK'
        });
      }
    });
  });
}
document.addEventListener("DOMContentLoaded", async () => {
  
  const form = document.querySelector('#formProduto');

  
  await renderizarTabela();

    if (form) {
      
           form.addEventListener('submit', async (e) => {
             e.preventDefault(); // evita recarregar a página
       
             const produto = {
                name: document.getElementById('produto').value,
                category: document.getElementById('categoria').value,
                description: document.getElementById('descricao').value,
                price : document.getElementById('preco').value,
                stock : document.getElementById('estoque').value
               
             };
             try {
               //console.log('Enviando produto:', produto);
               await cadastrarProduto(produto);
               form.reset();
               Swal.fire({
                title: 'Sucesso!',
                text: 'Produto cadastrado com sucesso.',
                icon: 'success',
                confirmButtonText: 'OK'
              });
              
             } catch (error) {
               console.error(error);
               Swal.fire({
                title: 'Erro!',
                text: getMensagemDeErro(error),
                icon: 'error',
                confirmButtonText: 'OK'
              });
             }
         });

     
    }
   
               
});
