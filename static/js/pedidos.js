import { listarPedidos,cadastrarPedido, deletarPedido,paginaAnterior,proximaPagina } from "../actions/pedidos.js";
import{ listarProdutos } from "../actions/produtos.js";
import { listarClientes } from "../actions/clientes.js";

carregarClientes();
carregarProdutos();
carregarPedidos();

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
  const deletarPedidoBtn = document.querySelectorAll(".deletarPedido");
  deletarPedidoBtn.forEach((btn) => {
          btn.addEventListener("click", async (e) => {
            const id = e.target.closest("tr").querySelector("td").innerText;
            try {
              await deletarPedido(id);
              await Swal.fire({
                title: 'Sucesso!',
                text: 'Pedido deletado com sucesso.',
                icon: 'success',
                confirmButtonText: 'OK'
              });
              await carregarPedidos(); // Recarrega a página para atualizar a tabela
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
      await carregarPedidos();
    }
    
    async function paginaAnt() {
      paginaAnterior();
      await carregarPedidos();
    }
    async function carregarPedidos() {
      const lista = document.getElementById("tabela-pedidos");
      lista.innerHTML = "";
     try{
        const res = await listarPedidos();
        if (res.length === 0) {
          lista.innerHTML = "<tr><td colspan='6'>Nenhum pedido encontrado.</td></tr>";
          return;
        }
        res.forEach((p) => {
          lista.innerHTML += `
            <tr>
              <td class="d-none">${p.id}</td>
              <td>${p.order_client}</td>
              <td>${p.order_product}</td>
              <td>${p.client_name}</td>
              <td>${p.product_name}</td>
              <td>${p.quantity}</td>
              <td>${p.description || "Detalhes não disponíveis"}</td>
              <td>${p.order_date}</td>
              <td>
                <button class="deletarPedido btn btn-sm btn-outline-danger">
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
      }
      catch (error) {
          console.error("Erro ao carregar pedidos:", error);
          Swal.fire({
            title: 'Erro!',
            text: getMensagemDeErro(error),
            icon: 'error',
            confirmButtonText: 'OK'
          });
        }
      
      
    
    }
document.getElementById("formPedido").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const clienteId = document.getElementById("cliente").value;
  const produtoId = document.getElementById("produto").value;
  const quantidade = Number(document.getElementById("quantidade").value);

  try {
    console.log("enviando pedido", clienteId, produtoId, quantidade);
    await cadastrarPedido({
      client_id: clienteId,
      product_id: produtoId,
      quantity: quantidade,});

    Swal.fire("Sucesso", "Pedido cadastrado com sucesso!", "success");
    e.target.reset();
     
    await carregarPedidos();
  } catch (error) {
    console.error("Erro ao cadastrar pedido:", error);
    Swal.fire({
      title: 'Erro!',
      text: getMensagemDeErro(error),
      icon: 'error',
      confirmButtonText: 'OK'
    });
  }
});

async function carregarClientes() {
  const select = document.getElementById("cliente");
  try{
    const res = await listarClientes();
    if (res.length === 0) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "Nenhum cliente disponível";
      select.appendChild(opt);
      return;
    }
    res.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.name;
    select.appendChild(opt);
  });
  }
  catch (error) {
    console.error("Erro ao carregar clientes:", error);
    Swal.fire("Erro", "Não foi possível carregar os clientes.", "error");
  }
  
  
}

async function carregarProdutos() {
  const select = document.getElementById("produto");
  try{
    const res = await listarProdutos();
    if (res.length === 0) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "Nenhum produto disponível";
      select.appendChild(opt);
      return;
    }
    res.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.name ;
      select.appendChild(opt);
    });
  }
  catch (error) {
    console.error("Erro ao carregar produtos:", error);
    Swal.fire({
      title: 'Erro!',
      text: getMensagemDeErro(error),
      icon: 'error',
      confirmButtonText: 'OK'
    });
  }
}


