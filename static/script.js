// Função interativa: Altera os detalhes do card lateral na aba "Tarefas"
function selecionarTarefa(titulo, descricao, prazo) {
  document.getElementById("detalheTitulo").innerText = titulo;
  document.getElementById("detalheDescricao").innerText = descricao;
  document.getElementById("detalhePrazo").innerText = prazo;
}

// Função interativa: Altera as informações ao clicar nos dias do calendário
function verData(dia) {
  const diaLabel = document.getElementById("calendarioDiaLabel");
  const eventoTexto = document.getElementById("calendarioEventoTexto");

  if (diaLabel) {
    diaLabel.innerText = "Dia " + dia;
  }
  
  if (eventoTexto) {
    if (dia === 10) {
      eventoTexto.innerText = "Reunião Geral de Alinhamento com José Gota às 14:00h.";
    } else if (dia === 18) {
      eventoTexto.innerText = "Apresentação de resultados para a diretoria às 10:30h.";
    } else if (dia === 25) {
      eventoTexto.innerText = "Entrega da versão final do protótipo de design.";
    } else {
      eventoTexto.innerText = "Nenhuma reunião ou evento agendado para este dia.";
    }
  }
}

// Seleção interativa dos dias do Calendário (mantém o círculo roxo no dia clicado)
document.addEventListener("DOMContentLoaded", () => {
  const dias = document.querySelectorAll(".calendario-grade .dia-ativo");
  dias.forEach((diaElement) => {
    diaElement.addEventListener("click", function () {
      dias.forEach((d) => d.classList.remove("selecionado"));
      this.classList.add("selecionado");

      const diaNumero = parseInt(this.innerText.trim(), 10);
      if (!isNaN(diaNumero)) {
        verData(diaNumero);
      }
    });
  });
});