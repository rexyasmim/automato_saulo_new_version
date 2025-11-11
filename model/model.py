import json
import sys
from .banco import DatabaseManager 
from .dfa import DFA               

class AutomatonModel:
    """
    Esta é a classe "Cérebro" (Model).
    Ela gerencia a lógica de negócios, usa o DatabaseManager para 
    persistência e o DFA para execução.
    
    Ela NÃO sabe nada sobre a interface gráfica (tkinter).
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializa o Model.
        
        :param db_manager: Uma instância já conectada do DatabaseManager.
                           Isso é chamado de "Injeção de Dependência".
        """
        self.db = db_manager
        
        # Cache para guardar instâncias de DFA já criadas e definições do DB.
        # Isso evita consultas desnecessárias ao DB.
        self._automata_definitions = {} # Cache de definições
        self._automata_cache = {}       # Cache de instâncias de DFA
        
        # Garante que as tabelas existam ao iniciar
        self.db.create_tables() 
        
        # Carrega as definições existentes do DB para o cache
        self.load_definitions_from_db()

    # (Dentro da classe AutomatonModel)

    def clear_test_history(self):
        """
        Pede ao DatabaseManager para limpar todo o histórico de testes.
        """
        try:
            self.db.clear_all_history()
            print("Modelo requisitou limpeza de histórico.")
        except Exception as e:
            print(f"Erro no modelo ao limpar histórico: {e}", file=sys.stderr)
            # Propaga o erro para o Controller
            raise ValueError(f"Erro ao limpar o banco de dados: {e}")

    def load_definitions_from_db(self):
        """
        Limpa os caches e recarrega todas as definições do banco de dados.
        """
        self._automata_definitions = {}
        self._automata_cache = {}
        
        definitions = self.db.get_all_automaton_definitions()
        for definicao in definitions:
            self._automata_definitions[definicao['nome']] = definicao
        
        print(f"Model carregou {len(self._automata_definitions)} definições.")

    def get_available_automata_names(self):
        """
        Retorna uma lista de nomes dos autômatos disponíveis.
        A View (interface) usará isso para popular o dropdown.
        """
        return sorted(list(self._automata_definitions.keys()))

    def _parse_transitions(self, transicoes_str):
        """
        Analisa a string de transições (do campo de texto do tkinter)
        e a transforma em um dicionário aninhado.
        
        Este é o código que definimos anteriormente.
        """
        transicoes_dict = {}
        linhas = transicoes_str.strip().split('\n')

        for numero_linha, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha: continue

            if '->' not in linha:
                raise ValueError(f"Formato inválido na linha {numero_linha}: Falta '->'. Linha: '{linha}'")
            partes = linha.split('->')
            if len(partes) != 2:
                raise ValueError(f"Formato inválido na linha {numero_linha}: Múltiplos '->'. Linha: '{linha}'")

            lado_esquerdo = partes[0].strip()
            lado_direito = partes[1].strip()

            if ',' not in lado_esquerdo:
                raise ValueError(f"Formato inválido na linha {numero_linha}: Falta ',' (vírgula). Linha: '{linha}'")
            partes_esquerda = lado_esquerdo.split(',')
            if len(partes_esquerda) != 2:
                raise ValueError(f"Formato inválido na linha {numero_linha}: Deve ser 'estado, simbolo'. Linha: '{linha}'")

            estado_origem = partes_esquerda[0].strip()
            simbolo = partes_esquerda[1].strip()
            estado_destino = lado_direito

            if estado_origem not in transicoes_dict:
                transicoes_dict[estado_origem] = {}

            if simbolo in transicoes_dict[estado_origem]:
                raise ValueError(
                    f"Erro de Não-Determinismo na linha {numero_linha}: "
                    f"O estado '{estado_origem}' já possui uma transição para o símbolo '{simbolo}'."
                )
            
            transicoes_dict[estado_origem][simbolo] = estado_destino
            
        return transicoes_dict

    def create_new_automaton(self, nome, estados_str, alfabeto_str, 
                             inicial_str, finais_str, transicoes_str):
        """
        Recebe os dados brutos (strings) da interface, valida-os,
        cria uma definição de autômato e a salva no banco de dados.
        """
        try:
            # --- PASSO 1: "PARSEAR" (Analisar) as strings ---
            if not nome.strip():
                raise ValueError("O nome do autômato não pode estar vazio.")
                
            nome = nome.strip()
            
            if nome in self._automata_definitions:
                raise ValueError(f"Um autômato com o nome '{nome}' já existe.")

            estados_set = set(s.strip() for s in estados_str.split(',') if s.strip())
            alfabeto_set = set(s.strip() for s in alfabeto_str.split(',') if s.strip())
            finais_set = set(s.strip() for s in finais_str.split(',') if s.strip())
            estado_inicial = inicial_str.strip()

            transicoes_dict = self._parse_transitions(transicoes_str)
            
            # --- PASSO 2: VALIDAR a lógica do Autômato ---
            # Nós usamos seu motor 'DFA' universal para validar!
            DFA(
                estados=estados_set,
                alfabeto=alfabeto_set,
                transicoes=transicoes_dict,
                estado_inicial=estado_inicial,
                estados_finais=finais_set
            )
            # Se o __init__ do DFA não disparar um erro, a definição é válida.

        except ValueError as e:
            # Se qualquer passo da validação/parse falhar, propaga o erro.
            # O Controller irá capturar este erro e mostrá-lo na View.
            print(f"Erro de validação: {e}", file=sys.stderr)
            raise e # Propaga o erro

        # --- PASSO 3: SALVAR no Banco de Dados ---
        # Se chegamos aqui, a definição é válida.
        try:
            self.db.save_automaton_definition(
                nome=nome,
                estados=estados_set,
                alfabeto=alfabeto_set,
                estado_inicial=estado_inicial,
                estados_finais=finais_set,
                transicoes_dict=transicoes_dict
            )
            
            # Atualiza o cache interno para que o novo autômato apareça
            self.load_definitions_from_db()
            print(f"SUCESSO: Autômato '{nome}' validado e salvo.")
            
        except Exception as e:
            print(f"Erro ao salvar no DB: {e}", file=sys.stderr)
            raise ValueError(f"Erro ao salvar no banco de dados: {e}")
        
    # (Dentro da classe AutomatonModel, pode ser depois de create_new_automaton)

    def create_automaton_from_file_content(self, file_content_string):
        """
        Analisa o conteúdo de um arquivo .txt, extrai as 6 strings
        (nome, alfabeto, etc.) e chama a função 'create_new_automaton'
        para fazer a validação e o salvamento.
        """
        print("Model processando conteúdo de arquivo...")
        
        parsed_data = {}
        transition_lines = []
        parsing_transitions = False

        for line in file_content_string.splitlines():
            line = line.strip()
            if not line: # Ignora linhas em branco
                continue

            # Checa se entramos na seção de transições
            if line.lower().startswith("transicoes:"):
                parsing_transitions = True
                continue
            
            if parsing_transitions:
                # Adiciona a linha à lista de transições
                transition_lines.append(line)
            else:
                # Se não, é uma linha "chave: valor"
                if ":" not in line:
                    raise ValueError(f"Formato de linha inválido (esperado 'chave: valor'): {line}")
                
                # Divide a linha no primeiro ":"
                key, value = line.split(":", 1) 
                parsed_data[key.strip().lower()] = value.strip()

        # --- Fim da leitura ---
        
        # Verifica se todas as chaves necessárias foram encontradas
        required_keys = ['nome', 'alfabeto', 'estados', 'inicial', 'finais']
        if not all(key in parsed_data for key in required_keys):
            missing = [key for key in required_keys if key not in parsed_data]
            raise ValueError(f"Arquivo .txt incompleto. Faltando chaves: {', '.join(missing)}")
            
        # Junta todas as linhas de transição de volta em uma única string
        transicoes_str = "\n".join(transition_lines)
        if not transicoes_str:
            raise ValueError("Arquivo .txt não contém nenhuma regra de transição após 'transicoes:'.")

        # --- MÁGICA DA REUTILIZAÇÃO! ---
        # Chama a função que já existe para fazer todo o trabalho
        # de validação, criação do DFA e salvamento no DB.
        print(f"Arquivo parseado. Tentando criar autômato: {parsed_data['nome']}")
        self.create_new_automaton(
            nome=parsed_data['nome'],
            alfabeto_str=parsed_data['alfabeto'],
            estados_str=parsed_data['estados'],
            inicial_str=parsed_data['inicial'],
            finais_str=parsed_data['finais'],
            transicoes_str=transicoes_str
        )

    def _get_automaton_instance(self, nome):
        """
        Método privado para carregar (ou pegar do cache) uma instância 
        do motor DFA pronta para uso.
        """
        # Se já instanciamos esse DFA antes, reutiliza
        if nome in self._automata_cache:
            return self._automata_cache[nome]
        
        # Se não, busca a definição no cache de definições
        if nome not in self._automata_definitions:
            raise ValueError(f"Nenhum autômato com o nome '{nome}' foi definido.")
            
        definicao = self._automata_definitions[nome]
        
        # Cria a instância universal do DFA
        dfa_instance = DFA(
            estados=definicao["estados"],
            alfabeto=definicao["alfabeto"],
            transicoes=definicao["transicoes"],
            estado_inicial=definicao["estado_inicial"],
            estados_finais=definicao["estados_finais"]
        )
        
        # Guarda no cache e retorna
        self._automata_cache[nome] = dfa_instance
        return dfa_instance

    def run_test(self, automaton_name, input_word):
        """
        Ponto de entrada principal para a lógica de teste.
        Recebe o nome do autômato e a palavra, retorna o resultado.
        
        :return: (tuple) (bool de aceitação, list de passos)
        """
        try:
            # 1. Pega o motor DFA correto
            dfa_engine = self._get_automaton_instance(automaton_name)
            
            # 2. Executa o motor universal com a palavra
            aceita, caminho = dfa_engine.run(input_word)
            
            # 3. Salva o resultado no histórico
            self.db.save_test_result(automaton_name, input_word, aceita)
            
            return aceita, caminho
            
        except Exception as e:
            print(f"Erro ao executar o teste: {e}", file=sys.stderr)
            # Retorna um resultado de falha que a interface possa entender
            raise e # Propaga o erro

    def get_test_history(self):
        """
        Busca o histórico de testes no banco de dados.
        """
        return self.db.get_test_history()