# 🤖 Simulador de Autômatos Finitos (DFA)

Este projeto é uma aplicação de desktop completa para a criação, simulação e gerenciamento de Autômatos Finitos Determinísticos (DFAs), desenvolvida em Python com foco na separação de responsabilidades usando o padrão MVC.

## 📝 Descrição do Projeto

O Simulador de Autômatos permite que um usuário defina, salve e teste DFAs de forma visual e intuitiva. Em vez de depender de código, o usuário pode criar um autômato (sua 5-tupla) através de um formulário gráfico ou importá-lo de um arquivo de texto.

Todas as definições de autômatos são persistidas em um banco de dados **SQLite**, permitindo que o usuário construa uma biblioteca de autômatos ao longo do tempo. O aplicativo também armazena um histórico de todos os testes executados.



## ✨ Funcionalidades

* **Criação de Autômatos:** Formulário gráfico para definir a 5-tupla (estados, alfabeto, transições, estado inicial, estados finais).
* **Persistência de Dados:** Autômatos criados são salvos em um banco de dados `automata.db` (SQLite) e recarregados ao iniciar o app.
* **Motor de Simulação:** Um "motor" de DFA universal que processa qualquer palavra de entrada e determina a aceitação/rejeição, mostrando o caminho percorrido.
* **Carregar de Arquivo:** Importe definições de autômatos de um arquivo `.txt` formatado, facilitando a criação de autômatos complexos.
* **Histórico de Testes:** Visualize todos os testes já executados (autômato, palavra, resultado, data) e limpe o histórico.
* **Interface Moderna:** Construído com `ttkbootstrap`, o aplicativo possui uma interface moderna com temas, incluindo um seletor Light/Dark (Temas "Vapor" 💜 e "Litera").

---

## 🛠️ Bibliotecas Utilizadas

* **[Python 3](https://www.python.org/)**: Linguagem principal do projeto.
* **[Tkinter](https://docs.python.org/3/library/tkinter.html)**: Biblioteca padrão do Python para criação de interfaces gráficas (GUI).
* **[ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/)**: A única dependência externa. Uma biblioteca que moderniza o `tkinter` com temas, estilos (como Bootstrap) e widgets avançados.
* **[SQLite 3](https://docs.python.org/3/library/sqlite3.html)**: (Biblioteca padrão) Usado para o banco de dados local que armazena as definições e o histórico.
* **[JSON](https://docs.python.org/3/library/json.html)**: (Biblioteca padrão) Usado para serializar o dicionário de transições para armazenamento no banco de dados.

---

## 🚀 Passo a Passo para Utilização

Siga estes passos para clonar e executar o projeto localmente.

### 1. Pré-requisitos

* Ter o [Python 3](https://www.python.org/downloads/) instalado em sua máquina.

### 2. Instalação

**1. Clone o repositório:**
```bash
git clone [https://github.com/rexyasmim/automato_saulo_new_version.git](https://github.com/rexyasmim/automato_saulo_new_version.git)
```
### 3. Responsáveis
* Yasmim Fernandes e João Pedro de Jesus Miranda
