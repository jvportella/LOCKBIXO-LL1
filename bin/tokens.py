from dataclasses import dataclass


@dataclass
class Token:
    kind: str
    lexeme: str
    line: int
    col: int


# Terminologias mapeadas para SEUS nomes de token
TERMS = [
    # Delimitadores
    'DELIM_DOISP','DELIM_PONTOVIR','DELIM_ABREP','DELIM_FECHAP','DELIM_P',
    'DELIM_VIRG','DELIM_ABRECHAVE','DELIM_FECHACHAVE','DELIM_ABRECOL','DELIM_FECHACOL',
    # Operadores aritméticos/relacionais/atribuição
    'OP_SOMA','OP_SUB','OP_MULTI','OP_DIV','OP_PERCENT',
    'OP_DIFERENCA','OP_IGUALDADE','OP_MAIOR','OP_MENOR','OP_MAIORIGUAL','OP_MENORIGUAL','OP_ATRIB',
    # Literais
    'STRING','INT_LIT','FLOAT_LIT','BOOLEAN_LIT','CHAR_LIT',
    # Lógicos
    'OP_E','OP_OU','OP_NAO',
    # Tipos e palavras-chave usadas pelo parser
    'Data_Type','VAZIO', # VAZIO = 'void' (do seu léxico)
    'SE','SENAO','ENQUANTO','PARA','FACA','RETORNA','ESCREVA',
    # Identificador + EOF
    'ID','EOF'
]