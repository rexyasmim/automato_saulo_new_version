
from model.model import AutomatonModel
from view.view import AutomatonView
import sys

class AutomatonController:
    
    def __init__(self, model: AutomatonModel, view: AutomatonView):
        """
        Inicializa o Controller.
        
        :param model: A instância do Cérebro (Model)
        :param view: A instância da Interface (View)
        """
        self.model = model
        self.view = view
        
        # --- "Injeta" este controller na View ---
        # Isso permite que a View vincule seus botões a estes métodos
        self.view.set_controller(self)
        
        # --- Configuração Inicial ---
        # Popula a interface com dados assim que o app inicia
        self._initial_app_setup()

    def _initial_app_setup(self):
        """
        Funções a serem executadas quando o aplicativo é iniciado.
        """
        print("Controlador iniciando setup inicial...")
        self._load_automata_list()
        self.on_refresh_history_click()
        print("Setup inicial do controlador concluído.")

    def _load_automata_list(self):
        """
        Busca a lista de nomes de autômatos do Model
        e manda a View exibi-la no dropdown.
        """
        try:
            names = self.model.get_available_automata_names()
            self.view.populate_automata_list(names)
        except Exception as e:
            self.view.show_message(
                "Erro ao Carregar", 
                f"Não foi possível carregar a lista de autômatos: {e}", 
                type="error"
            )

    # --- Métodos de Manipulação de Eventos (Event Handlers) ---
    # Estes métodos são chamados pelos botões da View

    def on_run_test_click(self):
        """
        Chamado quando o botão "Testar Palavra" é clicado.
        """
        try:
            # 1. Pega os dados da View
            data = self.view.get_test_data()
            automaton_name = data["automaton_name"]
            word = data["word"]
            
            if not automaton_name:
                self.view.show_message("Atenção", "Por favor, selecione um autômato.", type="warning")
                return

            # 2. Manda o Model executar a lógica
            aceita, caminho = self.model.run_test(automaton_name, word)
            
            # 3. Manda a View exibir o resultado
            self.view.show_test_result(aceita, caminho)
            
            # 4. (Bônus) Atualiza o histórico, já que um novo teste foi salvo
            self.on_refresh_history_click()
            
        except Exception as e:
            print(f"Erro no teste: {e}", file=sys.stderr)
            self.view.show_message("Erro no Teste", f"Ocorreu um erro: {e}", type="error")

    def on_save_automaton_click(self):
        """
        Chamado quando o botão "Salvar Autômato" é clicado.
        """
        try:
            # 1. Pega todos os dados brutos (strings) do formulário na View
            data = self.view.get_new_automaton_data()
            
            # 2. Manda o Model tentar criar (parsear, validar e salvar)
            self.model.create_new_automaton(
                nome=data["nome"],
                estados_str=data["estados_str"],
                alfabeto_str=data["alfabeto_str"],
                inicial_str=data["inicial_str"],
                finais_str=data["finais_str"],
                transicoes_str=data["transicoes_str"]
            )
            
            # 3. Se o Model NÃO deu erro, foi um sucesso
            self.view.show_message("Sucesso", f"Autômato '{data['nome']}' salvo com sucesso!")
            
            # 4. Limpa o formulário na View
            self.view.clear_create_form()
            
            # 5. Atualiza a lista de autômatos na Aba 1
            self._load_automata_list()
            
        except ValueError as e:
            # Erro de validação (ex: nome duplicado, formato inválido)
            print(f"Erro de validação ao salvar: {e}", file=sys.stderr)
            self.view.show_message("Erro de Validação", str(e), type="error")
        except Exception as e:
            # Outro erro inesperado (ex: DB falhou)
            print(f"Erro inesperado ao salvar: {e}", file=sys.stderr)
            self.view.show_message("Erro Inesperado", f"Ocorreu um erro: {e}", type="error")

    def on_refresh_history_click(self):
        """
        Chamado quando o botão "Atualizar Histórico" é clicado
        (ou após um novo teste ser executado).
        """
        try:
            # 1. Pega os dados do histórico do Model
            history_rows = self.model.get_test_history()
            
            # 2. Manda a View popular a tabela
            self.view.populate_history_table(history_rows)
            
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}", file=sys.stderr)
            self.view.show_message(
                "Erro de Histórico", 
                f"Não foi possível carregar o histórico: {e}", 
                type="error"
            )

    # (Dentro da classe AutomatonController)

    def on_clear_history_click(self):
        """
        Chamado quando o botão "Limpar Histórico" é clicado.
        Pede confirmação antes de apagar.
        """
        # 1. Pedir confirmação (usando a View)
        confirmed = self.view.show_confirmation_dialog(
            "Confirmar Exclusão", 
            "Você tem certeza que deseja apagar TODO o histórico de testes?\n\nEsta ação não pode ser desfeita."
        )
        
        if not confirmed:
            print("Limpeza de histórico cancelada pelo usuário.")
            return

        # 2. Se confirmado, manda o Model apagar
        try:
            self.model.clear_test_history()
            
            # 3. Informa a View do sucesso
            self.view.show_message("Sucesso", "Histórico de testes foi limpo.", type="info")
            
            # 4. Atualiza a tabela (que agora estará vazia)
            self.on_refresh_history_click()
            
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}", file=sys.stderr)
            self.view.show_message("Erro", f"Não foi possível limpar o histórico: {e}", type="error")

    # (Dentro da classe AutomatonController)

    def on_load_file_click(self):
        """
        Chamado quando o botão "Carregar de Arquivo" é clicado.
        Pede o arquivo à View, lê o conteúdo e manda o Model processar.
        """
        print("Controller: Botão 'Carregar de Arquivo' clicado.")
        
        # 1. Pede à View para abrir a caixa de diálogo
        filepath = self.view.get_filepath_to_load()
        
        if not filepath:
            print("Carregamento de arquivo cancelado pelo usuário.")
            return

        # 2. Se um arquivo foi pego, tenta lê-lo
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            self.view.show_message("Erro de Leitura", f"Não foi possível ler o arquivo '{filepath}'.\nErro: {e}", "error")
            return
            
        # 3. Manda o Model processar o conteúdo do arquivo
        try:
            # Esta é a nova função que criamos no Model
            self.model.create_automaton_from_file_content(file_content)
            
            # 4. Sucesso!
            self.view.show_message("Sucesso", "Autômato carregado do arquivo e salvo com sucesso!")
            
            # 5. Atualiza o dropdown na Aba 1
            self._load_automata_list()
            
            # 6. Limpa o formulário (pois os dados foram carregados)
            self.view.clear_create_form()

        except (ValueError, Exception) as e:
            # Pega erros de formato do arquivo (do Model)
            self.view.show_message("Erro de Formato", f"O arquivo está mal formatado ou a definição é inválida.\n\nErro: {e}", "error")