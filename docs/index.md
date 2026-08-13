# Intern Manager Pro

[![Release](https://img.shields.io/badge/Release-v2.1.0-005A9E?style=flat-square)](https://github.com/mellornm/Intern-Manager/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows_|_macOS-gray?style=flat-square)](https://github.com/mellornm/Intern-Manager)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](https://github.com/mellornm/Intern-Manager/blob/main/LICENSE)

---

**Sistema de gestão acadêmica focado no acompanhamento de estágios supervisionados.**

O **Intern Manager Pro** foi desenvolvido para solucionar a fragmentação de dados no acompanhamento de discentes. A aplicação centraliza cadastros, documentos obrigatórios e auditorias de campo, garantindo a integridade do histórico acadêmico desde a matrícula até a geração do relatório final.

![Visão Geral do Dashboard](assets/screenshots/dashboard_hero.png){ align=center style="border: 1px solid #e1e4e8; border-radius: 6px; margin-top: 20px; margin-bottom: 20px; width: 100%" }

## Funcionalidades do Sistema

### 1. Gestão de Discentes
Módulo central para cadastro e acompanhamento da jornada acadêmica dos estagiários.

* **Indicadores de Prazo:** Alertas visuais para contratos próximos do vencimento e barra de progresso temporal (% de conclusão do estágio).
* **Comunicação Direta:** Atalhos integrados para WhatsApp e E-mail, facilitando o contato rápido com o discente.
* **Interface Otimizada:** Barra de ações inteligente com menus de contexto para registro rápido de notas, reuniões e observações.

### 2. Módulo de Visitas e Supervisão
Ferramenta de auditoria e planejamento para supervisores de campo.

* **Calendário de Supervisão:** Visão mensal integrada de reuniões e visitas técnicas agendadas.
* **Registro de Evidências:** Upload e armazenamento seguro de fotos com sanitização automática de arquivos para padrão ISO.
* **Backup e Exportação:** Ferramenta de exportação em lote das evidências colhidas em campo.

### 3. Controle Documental
Gestão de conformidade e monitoramento do status de entrega de documentos obrigatórios.

* **Operações em Massa:** Aprovação coletiva de documentos para agilizar fluxos de trabalho repetitivos.
* **Dashboard Interativo:** Cards de KPI clicáveis com função de *drill-down* para filtragem instantânea da lista de alunos.

### 4. Geração de Relatórios
Compilação automatizada de dados para formalização do estágio e auditoria.

* **Exportação em Massa (Batch Export):** Geração simultânea de múltiplos relatórios PDF para alunos selecionados.
* **Padronização:** Relatórios formatados e prontos para impressão, garantindo a integridade dos dados semestrais.

---

## Instalação e Execução

O sistema é distribuído como uma aplicação *standalone*, não necessitando de instalação de dependências externas (como Python ou servidores de banco de dados) na máquina do usuário final.

### Requisitos Mínimos
* **Windows:** 10 ou 11 (64-bits).
* **macOS:** Catalina (10.15) ou superior.
* **Espaço em Disco:** 200 MB livres.

### Procedimento
1. Acesse a [Página de Download](https://github.com/mellornm/Intern-Manager/releases) no GitHub.
2.  Faça o download do arquivo compactado compatível com seu sistema operacional.
3.  Descompacte o arquivo e execute o binário `InternManager`.

> **Nota:** O banco de dados SQLite será criado automaticamente no diretório de dados do usuário na primeira execução.

---

## Stack Tecnológico

A aplicação foi construída utilizando tecnologias modernas e robustas para garantir performance e manutenibilidade a longo prazo.

| Componente     | Tecnologia   | Função                               |
| :------------- | :----------- | :----------------------------------- |
| **Linguagem**  | Python 3.12  | Core da aplicação.                   |
| **Interface**  | PySide6 (Qt) | GUI nativa e responsiva.             |
| **Database**   | SQLite 3     | Armazenamento local e relacional.    |
| **Relatórios** | ReportLab    | Engine de geração de PDF.            |
| **Análise**    | Matplotlib   | Renderização de gráficos e métricas. |

---

<p align="center">
  <small>&copy; 2026 Rodrigo Noronha de Mello - Documentação Oficial</small>
</p>