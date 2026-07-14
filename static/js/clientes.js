import { listarClientes, cadastrarCliente, deletarCliente,proximaPagina,paginaAnterior } from "../actions/clientes.js";
function getMensagemDeErro(error) {
  if (error.response) {
    return error.response.data.erro || "Erro desconhecido";
  } else if (error.request) {
    return "Erro de conexão com o servidor";
  } else {
    return error.message || "Erro inesperado";
  }
}

async function addEventosDeletar(){
  const deletarClienteBtn = document.querySelectorAll(".deletarCliente");
  deletarClienteBtn.forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.closest("tr").querySelector("td").innerText;
        try {
          await deletarCliente(id);
          await Swal.fire({
            title: 'Sucesso!',
            text: 'Cliente deletado com sucesso.',
            icon: 'success',
            confirmButtonText: 'OK'
          });
          location.reload(); // Recarrega a página para atualizar a tabela
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
  async function proxPagina() {
    proximaPagina();
    await renderizarTabela();
  }
  
  
  async function paginaAnt() {
    paginaAnterior();
    await renderizarTabela();
  }
  async function renderizarTabela() {
    const tabela = document.getElementById("tabela-clientes");
  
    if (tabela) {
      try{
        const response=await listarClientes()
        const clientes = response;
        tabela.innerHTML = "";
        if(clientes===undefined || clientes.length === 0  ){ 
          tabela.innerHTML = "<tr><td colspan='6'>Nenhum cliente encontrado.</td></tr>";
          return;
        }
        clientes.forEach((c, i) => {
        tabela.innerHTML += `
              <tr>
                <td>${c.id}</td>
                <td>${c.name}</td>
                <td>${c.phone}</td>
                <td>${c.address}</td>
                <td>${c.email}</td>
                <td>${c.registered_on}</td>
                <td>
                  <!--<button class="btn btn-sm btn-outline-primary" data-id="${c.id,c.name}" data-action="editar">-->
                  <!-- <i class="bi bi-pencil"></i></button>-->
                  <button class="deletarCliente btn btn-sm btn-outline-danger">
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

      }catch (error) {
          console.error("Erro ao listar clientes:", error);
        }

      }
    }

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.querySelector('#formCliente');
    await renderizarTabela();
    if (form) {
      
           form.addEventListener('submit', async (e) => {
             e.preventDefault(); // evita recarregar a página
       
             const cliente = {
                name: document.getElementById('nome').value,
                email: document.getElementById('email').value,
                address: document.getElementById('endereco').value,
                phone : document.getElementById('telefone').value,
               
             };
             try {
               console.log('Enviando cliente:', cliente);
               await cadastrarCliente(cliente);
               form.reset();
               Swal.fire({
                title: 'Sucesso!',
                text: 'Cliente cadastrado com sucesso.',
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