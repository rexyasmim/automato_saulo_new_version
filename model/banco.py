import sqlite3
import json
import datetime

class DatabaseManager:
    """
    Classe responsável por toda a comunicação com o banco de dados SQLite.
    Ela não sabe nada sobre DFAs ou tkinter, apenas como salvar e
    ler dados das tabelas.
    """
    
    def __init__(self, db_file="automata.db"):
        """
        Inicializa o gerenciador, especificando o arquivo do banco.
        """
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """
        Cria uma conexão com o banco de dados.
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(f"Conectado ao banco de dados: {self.db_file}")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise # Propaga o erro

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.conn:
            self.conn.close()
            print("Conexão com o banco fechada.")

    def _execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        """
        Método auxiliar privado para executar qualquer query.
        """
        if not self.conn:
            self.connect()
            
        try:
            with self.conn: # 'with' lida automaticamente com commit/rollback
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                if fetch_all:
                    return cursor.fetchall()
                    
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            # Em um app real, talvez queiramos logar isso
            return None
        
    # (Dentro da classe DatabaseManager)

    def clear_all_history(self):
        """Deleta todos os registros da tabela 'historico_testes'."""
        query_delete = "DELETE FROM historico_testes"
        # Opcional: Reseta o contador de ID (autoincrement)
        query_reset_seq = "DELETE FROM sqlite_sequence WHERE name='historico_testes'"
        
        print("Limpando histórico de testes do banco de dados...")
        self._execute_query(query_delete)
        self._execute_query(query_reset_seq) # Executa isso para que os IDs recomecem do 1
        print("Histórico de testes limpo.")

    def create_tables(self):
        """
        Cria as tabelas 'automatos' e 'historico_testes' se elas não existirem.
        """
        query_automatos = """
        CREATE TABLE IF NOT EXISTS automatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            estados TEXT NOT NULL,
            alfabeto TEXT NOT NULL,
            estado_inicial TEXT NOT NULL,
            estados_finais TEXT NOT NULL,
            transicoes TEXT NOT NULL 
        );
        """
        
        query_historico = """
        CREATE TABLE IF NOT EXISTS historico_testes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            automato_nome TEXT NOT NULL,
            palavra_testada TEXT NOT NULL,
            resultado TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        print("Criando tabelas (se não existirem)...")
        self._execute_query(query_automatos)
        self._execute_query(query_historico)
        print("Tabelas prontas.")

    # --- Funções para a Tabela 'automatos' ---

    def save_automaton_definition(self, nome, estados, alfabeto, estado_inicial, estados_finais, transicoes_dict):
        """
        Salva uma nova definição de autômato no banco.
        
        :param estados: (set) {'q0', 'q1'}
        :param alfabeto: (set) {'0', '1'}
        :param transicoes_dict: (dict) {'q0': {'0': 'q1'}, ...}
        """
        query = """
        INSERT INTO automatos (nome, estados, alfabeto, estado_inicial, estados_finais, transicoes)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        # Converte dados complexos (sets e dicts) para strings
        estados_str = ",".join(sorted(list(estados)))
        alfabeto_str = ",".join(sorted(list(alfabeto)))
        finais_str = ",".join(sorted(list(estados_finais)))
        
        # Converte o dicionário de transições para uma string JSON
        transicoes_json = json.dumps(transicoes_dict)
        
        params = (nome, estados_str, alfabeto_str, estado_inicial, finais_str, transicoes_json)
        
        self._execute_query(query, params)
        print(f"Definição do autômato '{nome}' salva.")

    def get_all_automaton_definitions(self):
        """
        Busca todas as definições de autômatos salvas no banco.
        """
        query = "SELECT nome, estados, alfabeto, estado_inicial, estados_finais, transicoes FROM automatos"
        
        rows = self._execute_query(query, fetch_all=True)
        
        # Converte as linhas do DB de volta para o formato que o Model espera
        definitions = []
        if not rows:
            return definitions
            
        for row in rows:
            nome, estados_str, alfabeto_str, inicial, finais_str, transicoes_json = row
            
            definitions.append({
                "nome": nome,
                "estados": set(estados_str.split(',')),
                "alfabeto": set(alfabeto_str.split(',')),
                "estado_inicial": inicial,
                "estados_finais": set(finais_str.split(',')),
                "transicoes": json.loads(transicoes_json) # Converte JSON de volta para dict
            })
            
        print(f"Carregadas {len(definitions)} definições do DB.")
        return definitions

    # --- Funções para a Tabela 'historico_testes' ---
    
    def save_test_result(self, automato_nome, palavra, resultado_bool):
        """
        Salva o resultado de uma execução de teste no histórico.
        """
        query = """
        INSERT INTO historico_testes (automato_nome, palavra_testada, resultado)
        VALUES (?, ?, ?)
        """
        
        resultado_str = "Aceita" if resultado_bool else "Rejeitada"
        params = (automato_nome, palavra, resultado_str)
        
        self._execute_query(query, params)

    def get_test_history(self):
        """
        Retorna todo o histórico de testes, do mais recente para o mais antigo.
        """
        query = "SELECT timestamp, automato_nome, palavra_testada, resultado FROM historico_testes ORDER BY timestamp DESC"
        
        rows = self._execute_query(query, fetch_all=True)
        return rows if rows else []