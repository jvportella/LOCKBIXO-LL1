# executaveis/lexer.py
# Scanner por regex alinhado aos tokens esperados pelo parser.
# Ajustes principais:
#  - STRING aceita escapes: r'"([^"\\]|\\.)*"'
#  - Ordem: operadores de 2 chars antes dos de 1 char
#  - WS inclui \r (Windows)
#  - Comentário de bloco com DOTALL

import re
from .tokens import Token  # Token(kind, lexeme, line, col)

# A ordem é importante!
TOKEN_SPECS = [
    # Espaços e comentários
    ('WS',              r'[ \t\r\n]+'),
    ('COMENTARIO',      r'//[^\n]*'),
    ('BLOQCOMENTARIO',  r'/\*.*?\*/'),

    # Delimitadores
    ('DELIM_ABRECHAVE',  r'\{'),
    ('DELIM_FECHACHAVE', r'\}'),
    ('DELIM_ABREP',      r'\('),
    ('DELIM_FECHAP',     r'\)'),
    ('DELIM_ABRECOL',    r'\['),
    ('DELIM_FECHACOL',   r'\]'),
    ('DELIM_PONTOVIR',   r';'),
    ('DELIM_VIRG',       r','),

    # Operadores compostos (2 caracteres) – SEMPRE antes dos de 1 caractere
    ('OP_MAIORIGUAL', r'>='),
    ('OP_MENORIGUAL', r'<='),
    ('OP_IGUALDADE',  r'=='),
    ('OP_DIFERENCA',  r'!='),
    ('OP_E',          r'&&'),
    ('OP_OU',         r'\|\|'),

    # Operadores simples (1 caractere)
    ('OP_ATRIB',   r'='),
    ('OP_MAIOR',   r'>'),
    ('OP_MENOR',   r'<'),
    ('OP_NAO',     r'!'),
    ('OP_SOMA',    r'\+'),
    ('OP_SUB',     r'-'),
    ('OP_MULTI',   r'\*'),
    ('OP_DIV',     r'/'),
    ('OP_PERCENT', r'%'),

    # Literais
    # Aceita qualquer char que não seja aspas nem backslash, OU uma sequência de escape \.
    ('STRING',     r'"([^"\\]|\\.)*"'),
    ('FLOAT_LIT',  r'[0-9]+\.[0-9]+'),
    ('INT_LIT',    r'[0-9]+'),
    ('CHAR_LIT',   r"'[^\\\n]'"),

    # Palavras-chave (ajuste para casar com os terminais da sua gramática)
    ('Data_Type',   r'String|int|real|boolean|char|double'),
    ('VAZIO',       r'void'),
    ('SE',          r'if'),
    ('SENAO',       r'else'),
    ('ENQUANTO',    r'while'),
    ('PARA',        r'for'),
    ('FACA',        r'do'),
    ('RETORNA',     r'return'),
    ('ESCREVA',     r'write'),
    ('BOOLEAN_LIT', r'true|false'),

    # Identificadores (por último, para não capturar keywords)
    ('ID',          r'[A-Za-z_][A-Za-z0-9_]*'),
]

# DOTALL permite que o comentário de bloco atravesse linhas
MASTER_RE = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPECS), re.DOTALL)

class Lexer:
    def __init__(self, text: str):
        self.text = text

    def tokens(self):
        text = self.text
        pos = 0
        line = 1
        col = 1

        while pos < len(text):
            m = MASTER_RE.match(text, pos)
            if not m:
                snippet = text[pos:pos+20].replace('\n', '\\n')
                raise SyntaxError(f"Caractere inválido em {line}:{col} perto de '{snippet}'")

            kind = m.lastgroup
            lexeme = m.group()
            start_line, start_col = line, col

            # atualiza line/col
            lines = lexeme.split('\n')
            if len(lines) == 1:
                col += len(lexeme)
            else:
                line += len(lines) - 1
                col = len(lines[-1]) + 1

            pos = m.end()

            # ignora espaços/comentários
            if kind in ('WS', 'COMENTARIO', 'BLOQCOMENTARIO'):
                continue

            yield Token(kind, lexeme, start_line, start_col)

        yield Token('EOF', '', line, col)
