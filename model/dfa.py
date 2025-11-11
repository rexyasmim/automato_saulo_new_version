
import sys

class DFA:
    
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_finais):
        """
        Inicializa o motor do DFA.

        :param estados: (set) Um conjunto de todos os estados (ex: {'q0', 'q1'})
        :param alfabeto: (set) Um conjunto de símbolos do alfabeto (ex: {'0', '1'})
        :param transicoes: (dict) Um dicionário aninhado de transições
                          Formato: {estado_origem: {simbolo: estado_destino}}
                          Ex: {'q0': {'0': 'q1', '1': 'q0'}, 'q1': {'0': 'q1', '1': 'q0'}}
        :param estado_inicial: (str) O nome do estado inicial (ex: 'q0')
        :param estados_finais: (set) Um conjunto dos estados de aceitação (ex: {'q1'})
        """
        
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.transicoes = transicoes
        self.estado_inicial = estado_inicial
        self.estados_finais = set(estados_finais)
        
        # Validação para garantir que a definição está correta
        # Esta é a validação lógica que discutimos
        self._validar_definicao()

    def _validar_definicao(self):
        """
        Verifica se a definição do DFA é coerente e logicamente válida.
        Dispara um ValueError se encontrar um problema.
        """
        
        if self.estado_inicial not in self.estados:
            raise ValueError(f"Definição inválida: Estado inicial '{self.estado_inicial}' não pertence ao conjunto de estados.")

        if not self.estados_finais.issubset(self.estados):
            raise ValueError("Definição inválida: Pelo menos um estado final não pertence ao conjunto de estados.")
            
        for estado_origem, caminhos in self.transicoes.items():
            # Verifica se o estado de origem é válido
            if estado_origem not in self.estados:
                raise ValueError(f"Definição inválida: Estado de transição '{estado_origem}' não pertence ao conjunto de estados.")
            
            for simbolo, estado_destino in caminhos.items():
                # Verifica se o símbolo da transição é válido
                if simbolo not in self.alfabeto:
                    raise ValueError(f"Definição inválida: Símbolo '{simbolo}' na transição de '{estado_origem}' não pertence ao alfabeto.")
                
                # Verifica se o estado de destino é válido
                if estado_destino not in self.estados:
                    raise ValueError(f"Definição inválida: Estado de destino '{estado_destino}' na transição de '{estado_origem}' não pertence ao conjunto de estados.")

    def run(self, palavra):
        """
        Processa uma palavra e retorna True (Aceita) ou False (Rejeitada).
        
        :param palavra: (str) A string de entrada a ser testada.
        :return: (tuple) (bool de aceitação, list de passos/caminho)
        """
        
        # --- 1. Validação da Palavra ---
        for simbolo in palavra:
            if simbolo not in self.alfabeto:
                # Rejeita imediatamente se um símbolo não pertencer ao alfabeto
                print(f"Símbolo '{simbolo}' não pertence ao alfabeto {self.alfabeto}", file=sys.stderr)
                return False, [self.estado_inicial] # Retorna Falso e o caminho (parou no início)

        # --- 2. Processamento ---
        estado_atual = self.estado_inicial
        caminho = [estado_atual] # Lista para rastrear os passos

        for simbolo in palavra:
            try:
                # Busca o próximo estado no dicionário de transições
                estado_atual = self.transicoes[estado_atual][simbolo]
                caminho.append(estado_atual)
            
            except KeyError:
                # Transição não definida (DFA incompleto).
                # Em um DFA formal, isso iria para um "estado de erro/morte" implícito.
                # Para esta implementação, podemos simplesmente rejeitar.
                print(f"Transição não definida para o estado '{estado_atual}' com o símbolo '{simbolo}'", file=sys.stderr)
                return False, caminho

        # --- 3. Verificação Final ---
        # A palavra é aceita se, e somente se, o estado em que paramos
        # é um dos estados finais.
        aceita = estado_atual in self.estados_finais
        return aceita, caminho