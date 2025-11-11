import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter import filedialog
# Não precisamos mais importar 'tk' ou 'ttk'

class AutomatonView:
    """
    Esta é a classe "View" (a Interface Gráfica), agora usando ttkbootstrap.
    """
    
    def __init__(self, root: tb.Window):
        """
        Inicializa a interface principal.
        """
        self.root = root
        self.root.title("Simulador de Autômatos")
        self.root.geometry("700x600") 
        
        self.controller = None 

        # --- Frame para o Seletor de Tema ---
        theme_frame = tb.Frame(self.root, padding=(0, 0, 10, 10))
        theme_frame.pack(fill=X)
        
        self.lbl_theme = tb.Label(theme_frame, text="Tema:")
        self.lbl_theme.pack(side=LEFT, padx=(10, 5))
        
        # --- CORREÇÃO DO BOTÃO DE TEMA (Parte 1) ---
        # Cria a variável ANTES de usá-la
        self.theme_var = tb.StringVar(value="1") # 1 = Dark mode (superhero)
        
        self.theme_toggle = tb.Checkbutton(
            theme_frame, 
            text="Dark", 
            bootstyle="info,round-toggle",
            command=self.toggle_theme,
            variable=self.theme_var,  # Linka a variável
            onvalue="1",              # Define o valor "ligado"
            offvalue="0"              # Define o valor "desligado"
        )
        self.theme_toggle.pack(side=LEFT)

        # --- Cria o sistema de Abas (Notebook) ---
        self.notebook = tb.Notebook(root, bootstyle="info")
        
        # --- Cria as 3 Abas (agora tb.Frame) ---
        self.tab_test = tb.Frame(self.notebook, padding=10)
        self.tab_create = tb.Frame(self.notebook, padding=10)
        self.tab_history = tb.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_test, text="Executar Teste")
        self.notebook.add(self.tab_create, text="Criar Autômato")
        self.notebook.add(self.tab_history, text="Histórico")
        
        self.notebook.pack(expand=True, fill='both')
        
        # --- "Desenha" o conteúdo de cada aba ---
        self._create_test_tab()
        self._create_create_tab()
        self._create_history_tab()

    def toggle_theme(self):
        """Troca o tema entre claro e escuro."""
        # --- CORREÇÃO DO BOTÃO DE TEMA (Parte 2) ---
        # Lê a variável self.theme_var
        if self.theme_var.get() == "1": # '1' é 'On'
            self.root.style.theme_use("vapor")
            self.theme_toggle.config(text="Dark")
        else: # '0' é 'Off'
            self.root.style.theme_use("cosmo")
            self.theme_toggle.config(text="Light")

    # (Dentro da classe AutomatonView)

    def set_controller(self, controller):
        """Vincula os comandos dos botões ao Controller."""
        self.controller = controller
        self.btn_run_test.config(command=self.controller.on_run_test_click)
        self.btn_save_automaton.config(command=self.controller.on_save_automaton_click)
        self.btn_refresh_history.config(command=self.controller.on_refresh_history_click)
        # --- NOVA LINHA ---
        self.btn_clear_history.config(command=self.controller.on_clear_history_click)
        self.btn_load_file.config(command=self.controller.on_load_file_click)

    # (Dentro da classe AutomatonView, na seção de 'GETTERS')

    def get_filepath_to_load(self):
        """Abre a caixa de diálogo para selecionar um arquivo .txt."""
        filepath = filedialog.askopenfilename(
            title="Selecionar arquivo de definição de autômato",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        # Retorna o caminho do arquivo (ex: "C:/.../meu_automato.txt") ou "" se o usuário cancelar
        return filepath

    # --- Métodos Privados para criar cada aba ---

    def _create_test_tab(self):
        """Cria os widgets para a aba "Executar Teste"."""
        frame = self.tab_test
        frame.columnconfigure(1, weight=1)

        # --- Widgets (tb.*) ---
        tb.Label(frame, text="Selecione o Autômato:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.combo_automata = tb.Combobox(frame, state="readonly", bootstyle="info")
        self.combo_automata.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tb.Label(frame, text="Palavra de Entrada:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_word = tb.Entry(frame, bootstyle="info")
        self.entry_word.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.btn_run_test = tb.Button(frame, text="Testar Palavra", bootstyle="info-outline")
        self.btn_run_test.grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        # --- Quadro de Resultado ---
        # --- CORREÇÃO DO LABELFRAME ---
        # (Era 'LabelFrame', mudou para 'Labelframe')
        result_frame = tb.Labelframe(frame, text="Resultado", padding=10, bootstyle="info")
        result_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')
        result_frame.columnconfigure(0, weight=1)
        
        self.lbl_result = tb.Label(result_frame, text="---", font=("Helvetica", 20, "bold"), anchor="center")
        self.lbl_result.grid(row=0, column=0, padx=5, pady=10, sticky='ew')
        
        self.lbl_path = tb.Label(result_frame, text="Caminho: ---", anchor="center", bootstyle="secondary")
        self.lbl_path.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

    def _create_create_tab(self):
        """Cria os widgets para a aba "Criar Autômato"."""
        frame = self.tab_create
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(7, weight=1) # Onde o tb.Text está

        # --- Widgets (Formulário) ---
        tb.Label(frame, text="Nome do Autômato:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_new_name = tb.Entry(frame)
        self.entry_new_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tb.Label(frame, text="Alfabeto (ex: 0,1):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_new_alphabet = tb.Entry(frame)
        self.entry_new_alphabet.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        tb.Label(frame, text="Estados (ex: q0,q1):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_new_states = tb.Entry(frame)
        self.entry_new_states.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        tb.Label(frame, text="Estado Inicial:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.entry_new_initial = tb.Entry(frame)
        self.entry_new_initial.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        tb.Label(frame, text="Estados Finais (ex: q1):").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.entry_new_final = tb.Entry(frame)
        self.entry_new_final.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        
        tb.Label(frame, text="Transições:").grid(row=5, column=0, padx=5, pady=5, sticky='nw')
        
        # --- O TEXTO DE AJUDA ---
        help_text = (
            "Digite uma transição por linha no formato: estado, simbolo -> destino\n"
            "Exemplo: q0, 0 -> q1"
        )
        tb.Label(frame, text=help_text, bootstyle="secondary", justify="left").grid(row=6, column=1, padx=5, pady=(0, 5), sticky='w')

        # --- Caixa de Texto Grande (tb.Text) ---
        self.text_new_transitions = tb.Text(frame, height=10, width=50)
        self.text_new_transitions.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # --- CORREÇÃO ESTÁ AQUI ---
        # Substitui o btn_save_automaton.grid(...) por este bloco
        
        # --- Frame para os botões (Salvar e Carregar) ---
        # Define o 'button_frame' ANTES de usá-lo
        button_frame = tb.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky='ew')
        
        # Configura o frame para que os botões se expandam
        button_frame.columnconfigure(0, weight=1) 
        button_frame.columnconfigure(1, weight=1)

        # Agora o btn_save_automaton usa o button_frame
        self.btn_save_automaton = tb.Button(button_frame, text="Salvar Autômato", bootstyle="success")
        self.btn_save_automaton.grid(row=0, column=0, padx=(0, 5), sticky='ew')

        # E o btn_load_file também usa o button_frame
        self.btn_load_file = tb.Button(button_frame, text="Carregar de Arquivo (.txt)", bootstyle="secondary-outline")
        self.btn_load_file.grid(row=0, column=1, padx=(5, 0), sticky='ew')

    # (Dentro da classe AutomatonView)

    def _create_history_tab(self):
        """Cria os widgets para a aba "Histórico"."""
        frame = self.tab_history
        
        # Configura o grid para expandir
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1) # A tabela ficará na linha 1

        # --- Frame para os botões (na linha 0) ---
        button_frame = tb.Frame(frame)
        button_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=10, sticky='w')

        self.btn_refresh_history = tb.Button(button_frame, text="Atualizar Histórico", bootstyle="info-outline")
        self.btn_refresh_history.pack(side=LEFT, padx=(0, 10))
        
        # --- NOVO BOTÃO ---
        self.btn_clear_history = tb.Button(button_frame, text="Limpar Histórico", bootstyle="danger-outline")
        self.btn_clear_history.pack(side=LEFT)
        
        # --- Tabela (Treeview) (na linha 1) ---
        cols = ("Data/Hora", "Autômato", "Palavra", "Resultado")
        self.tree_history = tb.Treeview(frame, columns=cols, show="headings", height=15, bootstyle="info")
        
        for col in cols:
            self.tree_history.heading(col, text=col)
            self.tree_history.column(col, width=150, anchor='center')
        
        scrollbar = tb.Scrollbar(frame, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scrollbar.set)
        
        self.tree_history.grid(row=1, column=0, padx=5, pady=5, sticky='nsew') # Na linha 1
        scrollbar.grid(row=1, column=1, padx=5, pady=5, sticky='ns') # Na linha 1

    # --- Métodos Públicos (GETTERS) ---
    
    def get_test_data(self):
        """Retorna os dados da aba 'Executar Teste'."""
        return { "automaton_name": self.combo_automata.get(), "word": self.entry_word.get() }
        
    def get_new_automaton_data(self):
        """Retorna todos os dados brutos do formulário 'Criar Autômato'."""
        return {
            "nome": self.entry_new_name.get(),
            "alfabeto_str": self.entry_new_alphabet.get(),
            "estados_str": self.entry_new_states.get(),
            "inicial_str": self.entry_new_initial.get(),
            "finais_str": self.entry_new_final.get(),
            "transicoes_str": self.text_new_transitions.get("1.0", "end-1c")
        }
        
    # --- Métodos Públicos (SETTERS/UPDATERS) ---

    def populate_automata_list(self, names_list):
        """Atualiza a lista do dropdown na aba 'Executar Teste'."""
        self.combo_automata['values'] = names_list
        if names_list:
            self.combo_automata.current(0) 
        else:
            self.combo_automata.set("") 

    def show_test_result(self, is_accepted, path_list):
        """Exibe o resultado 'Aceita' ou 'Rejeitada'."""
        path_str = " -> ".join(path_list)
        self.lbl_path.config(text=f"Caminho: {path_str}")
        
        if is_accepted:
            self.lbl_result.config(text="ACEITA", bootstyle="success")
        else:
            self.lbl_result.config(text="REJEITADA", bootstyle="danger")
            
    def populate_history_table(self, history_data_rows):
        """Limpa e preenche a tabela de histórico."""
        for row in self.tree_history.get_children():
            self.tree_history.delete(row)
        for row_data in history_data_rows:
            self.tree_history.insert("", END, values=row_data)
            
    def clear_create_form(self):
        """Limpa todos os campos do formulário 'Criar Autômato'."""
        self.entry_new_name.delete(0, END)
        self.entry_new_alphabet.delete(0, END)
        self.entry_new_states.delete(0, END)
        self.entry_new_initial.delete(0, END)
        self.entry_new_final.delete(0, END)
        self.text_new_transitions.delete("1.0", END)
        
    def show_message(self, title, message, type="info"):
        """Exibe um pop-up de mensagem."""
        if type == "error":
            messagebox.showerror(title, message)
        elif type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)

    # (Dentro da classe AutomatonView, no final)

    def show_confirmation_dialog(self, title, message):
        """Exibe um pop-up 'Sim/Não' e retorna True/False."""
        return messagebox.askyesno(title, message)