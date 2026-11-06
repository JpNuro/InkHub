// Define quais propriedades de cada resposta aparecem nas tabelas do painel.
const COLUNAS = {
  usuarios: [
    { chave: "id", titulo: "ID" },
    { chave: "nome", titulo: "Nome" },
    { chave: "email", titulo: "E-mail" },
  ],
  obras: [
    { chave: "id", titulo: "ID" },
    { chave: "titulo", titulo: "Título" },
    { chave: "autor", titulo: "Autor" },
    { chave: "categoria", titulo: "Categoria" },
    { chave: "ano", titulo: "Ano" },
    { chave: "editora", titulo: "Editora" },
  ],
  capitulos: [
    { chave: "id", titulo: "ID" },
    { chave: "titulo", titulo: "Título" },
    { chave: "numero", titulo: "Número" },
    { chave: "obra_id", titulo: "ID da Obra" },
  ],
};

// Textos dos títulos usados ao alternar entre as áreas administrativas.
const TITULOS = {
  usuarios: { lista: "Usuários", form: "Novo usuário" },
  obras: { lista: "Obras", form: "Nova obra" },
  capitulos: { lista: "Capítulos", form: "Novo capítulo" },
};

// Campos que serão montados dinamicamente para cada tipo de cadastro.
const CAMPOS = {
  usuarios: [
    { nome: "nome", rotulo: "Nome", obrigatorio: true },
    { nome: "email", rotulo: "E-mail", tipo: "email" },
  ],
  obras: [
    { nome: "titulo_obra", rotulo: "Título", obrigatorio: true },
    { nome: "autor_id", rotulo: "Autor", tipo: "select", origem: "usuarios", obrigatorio: true },
    { nome: "categoria", rotulo: "Categoria" },
    { nome: "ano", rotulo: "Ano", tipo: "number" },
    { nome: "editora", rotulo: "Editora" },
  ],
  capitulos: [
    { nome: "titulo_capitulo", rotulo: "Título do Capítulo", obrigatorio: true },
    { nome: "numero_capitulo", rotulo: "Número", tipo: "number", obrigatorio: true },
    {
      nome: "obra_id", rotulo: "Obra", tipo: "select",
      origem: "obras", obrigatorio: true
    },
  ],
};

// Referências aos elementos do painel, reutilizadas pelas funções abaixo.
const elementoStatus = document.getElementById("status");
const elementoTituloLista = document.getElementById("titulo-lista");
const elementoTituloFormulario = document.getElementById("titulo-formulario");
const elementoCabecalho = document.getElementById("cabecalho");
const elementoCorpo = document.getElementById("corpo");
const elementoCampos = document.getElementById("campos");
const formulario = document.getElementById("formulario");
const mensagemFormulario = document.getElementById("mensagem-formulario");
const botaoRecarregar = document.getElementById("botao-recarregar");
const abas = document.querySelectorAll(".aba");

let tipoAtual = "usuarios";

// Consulta a API para um recurso e transforma respostas HTTP inválidas em erro.
async function buscar(tipo) {
  const resposta = await fetch(`/api/${tipo}`);
  if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
  return resposta.json();
}

async function carregar(tipo) {
  // Atualiza o contexto da tela antes de solicitar os dados ao servidor.
  tipoAtual = tipo;
  elementoTituloLista.textContent = TITULOS[tipo].lista;
  elementoTituloFormulario.textContent = TITULOS[tipo].form;
  limparMensagem();

  await renderizarFormulario(tipo);
  renderizarCabecalho(tipo);
  elementoCorpo.innerHTML = "";

  elementoStatus.classList.remove("erro");
  elementoStatus.textContent = "Carregando...";

  try {
    // Busca os registros e atualiza tabela e indicador de carregamento.
    const dados = await buscar(tipo);
    renderizarLinhas(tipo, dados);
    elementoStatus.textContent = `${dados.length} registro(s) carregado(s).`;
  } catch (erro) {
    elementoStatus.textContent = `Falha ao carregar: ${erro.message}`;
    elementoStatus.classList.add("erro");
  }
}

function renderizarCabecalho(tipo) {
  // Cria os cabeçalhos conforme as colunas configuradas para o recurso.
  elementoCabecalho.innerHTML = "";
  for (const coluna of COLUNAS[tipo]) {
    const th = document.createElement("th");
    th.textContent = coluna.titulo;
    elementoCabecalho.appendChild(th);
  }
}

function renderizarLinhas(tipo, dados) {
  // Informa quando a consulta não retornou registros para exibir.
  if (!dados.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = COLUNAS[tipo].length;
    td.className = "vazio";
    td.textContent = "Nenhum registro encontrado.";
    tr.appendChild(td);
    elementoCorpo.appendChild(tr);
    return;
  }

  // Adiciona uma linha por registro usando textContent para exibir valores como texto.
  for (const item of dados) {
    const tr = document.createElement("tr");
    for (const coluna of COLUNAS[tipo]) {
      const td = document.createElement("td");
      const valor = item[coluna.chave];
      td.textContent = valor === null || valor === undefined ? "—" : valor;
      tr.appendChild(td);
    }
    elementoCorpo.appendChild(tr);
  }
}

async function renderizarFormulario(tipo) {
  // Reconstrói os controles do formulário de acordo com o cadastro escolhido.
  elementoCampos.innerHTML = "";
  for (const campo of CAMPOS[tipo]) {
    const wrapper = document.createElement("div");
    wrapper.className = "campo";

    const label = document.createElement("label");
    label.htmlFor = `campo-${campo.nome}`;
    label.textContent = campo.rotulo + (campo.obrigatorio ? " *" : "");
    wrapper.appendChild(label);

    if (campo.tipo === "select") {
      // Preenche listas de seleção consultando a origem indicada na configuração.
      const select = document.createElement("select");
      select.id = `campo-${campo.nome}`;
      select.name = campo.nome;
      if (campo.obrigatorio) select.required = true;

      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Selecione...";
      select.appendChild(placeholder);

      try {
        const itens = await buscar(campo.origem);
        for (const item of itens) {
          const option = document.createElement("option");
          option.value = item.id;
          option.textContent = rotuloItem(campo.origem, item);
          select.appendChild(option);
        }
      } catch (erro) {
        const option = document.createElement("option");
        option.disabled = true;
        option.textContent = `Erro ao carregar: ${erro.message}`;
        select.appendChild(option);
      }

      wrapper.appendChild(select);
    } else {
      // Os demais campos são inputs HTML com tipo e validação configuráveis.
      const input = document.createElement("input");
      input.type = campo.tipo || "text";
      input.id = `campo-${campo.nome}`;
      input.name = campo.nome;
      if (campo.obrigatorio) input.required = true;
      wrapper.appendChild(input);
    }

    elementoCampos.appendChild(wrapper);
  }
}

function rotuloItem(origem, item) {
  // Define o texto legível de cada opção dos selects de relacionamento.
  if (origem === "usuarios") return `${item.nome} (id ${item.id})`;
  if (origem === "obras") return `${item.titulo} (id ${item.id})`;
  return `${item.id}`;
}

function limparMensagem() {
  // Limpa mensagem anterior e remove as classes de estado visual.
  mensagemFormulario.textContent = "";
  mensagemFormulario.classList.remove("sucesso", "erro");
}

async function enviarFormulario(evento) {
  // Intercepta o submit para enviar JSON à API sem recarregar a página.
  evento.preventDefault();
  limparMensagem();

  const dados = {};
  // Lê e valida os campos declarados para o tipo de cadastro atual.
  for (const campo of CAMPOS[tipoAtual]) {
    const elemento = formulario.elements[campo.nome];
    const valor = elemento.value.trim();
    if (campo.obrigatorio && !valor) {
      mensagemFormulario.textContent = `Preencha ${campo.rotulo}.`;
      mensagemFormulario.classList.add("erro");
      elemento.focus();
      return;
    }
    if (valor !== "") dados[campo.nome] = valor;
  }

  const botao = formulario.querySelector("button[type=submit]");
  botao.disabled = true;
  try {
    // Envia os valores e interpreta erros retornados pelo backend.
    const resposta = await fetch(`/api/${tipoAtual}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });

    const corpo = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      throw new Error(corpo.erro || `HTTP ${resposta.status}`);
    }

    mensagemFormulario.textContent = "Cadastrado com sucesso.";
    mensagemFormulario.classList.add("sucesso");
    formulario.reset();
    await carregar(tipoAtual);
  } catch (erro) {
    mensagemFormulario.textContent = erro.message;
    mensagemFormulario.classList.add("erro");
  } finally {
    botao.disabled = false;
  }
}

abas.forEach((aba) => {
  // Trocar de aba atualiza o destaque e carrega os registros correspondentes.
  aba.addEventListener("click", () => {
    abas.forEach((a) => a.classList.remove("ativa"));
    aba.classList.add("ativa");
    carregar(aba.dataset.tipo);
  });
});

// Botões e formulário compartilham as funções de recarregar e cadastrar.
botaoRecarregar.addEventListener("click", () => carregar(tipoAtual));
formulario.addEventListener("submit", enviarFormulario);

// Abre o painel com a lista padrão de usuários.
carregar("usuarios");
