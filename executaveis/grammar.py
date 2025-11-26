# executaveis/grammar.py
# Gramática LL(1) corrigida:
#  - Fatoração de Data_Type ID (...) vs var: DeclOrFunc / DeclOrFuncTail
#  - Fatoração de statements que começam com ID: IdStmt -> ID IdStmtTail
#  - Removido conflito com ExpressionStmt (não inicia mais com ID)
from collections import defaultdict

EPS = 'ε'
START_SYMBOL = 'Program'

NONTERMS = [
    'Program','StmtList','Statement','Block',
    'DeclOrFunc','DeclOrFuncTail','FunctionDeclVoid','VarDeclTail',
    'IdStmt','IdStmtTail',                 # <-- novo
    'Assignment','ForAssign',
    'IfStmt','IfElseOpt','WhileStmt','DoWhileStmt',
    'ForStmt','ForInit','ForInitOpt','ExprOpt','ForAssignOpt',
    'FunctionCall','ArgList','ArgListOpt','ArgListTail',
    'ParamList','ParamListOpt','ParamListTail',
    'WriteStmt','ReturnStmt','ReturnExprOpt',
    'Expr','OrExpr','OrTail','AndExpr','AndTail','EqExpr','EqTail',
    'RelExpr','RelTail','AddExpr','AddTail','MulExpr','MulTail','UnaryExpr','Primary'
]

G = defaultdict(list)

# Program -> StmtList EOF
G['Program'].append(['StmtList','EOF'])

# StmtList -> Statement StmtList | ε
G['StmtList'].append(['Statement','StmtList'])
G['StmtList'].append([EPS])

# Statement (ordem importa, e sem ExpressionStmt começando com ID)
G['Statement'].extend([
    ['DeclOrFunc'],         # Data_Type ID ...
    ['FunctionDeclVoid'],   # void ID ...
    ['IdStmt'],             # ID ...  (atribuição OU chamada)
    ['IfStmt'],
    ['WhileStmt'],
    ['DoWhileStmt'],
    ['ForStmt'],
    ['Block'],
    ['WriteStmt'],
    ['ReturnStmt']
])

# Block -> { StmtList }
G['Block'].append(['DELIM_ABRECHAVE','StmtList','DELIM_FECHACHAVE'])

# --- FATORAÇÃO: Data_Type ID ... (var OU função com tipo) ---
# DeclOrFunc -> Data_Type ID DeclOrFuncTail
G['DeclOrFunc'].append(['Data_Type','ID','DeclOrFuncTail'])
# DeclOrFuncTail -> ( ParamList? ) Block | VarDeclTail ;
G['DeclOrFuncTail'].append(['DELIM_ABREP','ParamListOpt','DELIM_FECHAP','Block'])
G['DeclOrFuncTail'].append(['VarDeclTail','DELIM_PONTOVIR'])
# VarDeclTail -> = Expr | ε
G['VarDeclTail'].append(['OP_ATRIB','Expr'])
G['VarDeclTail'].append([EPS])

# FunctionDeclVoid -> VAZIO ID ( ParamList? ) Block
G['FunctionDeclVoid'].append(['VAZIO','ID','DELIM_ABREP','ParamListOpt','DELIM_FECHAP','Block'])

# --- FATORAÇÃO: tudo que começa com ID dentro de Statement ---
# IdStmt -> ID IdStmtTail
# IdStmtTail -> = Expr ;            (Assignment)
#            | ( ArgList? ) ;       (FunctionCall)
G['IdStmt'].append(['ID','IdStmtTail'])
G['IdStmtTail'].append(['OP_ATRIB','Expr','DELIM_PONTOVIR'])
G['IdStmtTail'].append(['DELIM_ABREP','ArgListOpt','DELIM_FECHAP','DELIM_PONTOVIR'])

# Mantemos estas para reuso (ForAssign usa padrão de Assignment):
# Assignment -> ID = Expr ;
G['Assignment'].append(['ID','OP_ATRIB','Expr','DELIM_PONTOVIR'])
# ForAssign -> ID = Expr
G['ForAssign'].append(['ID','OP_ATRIB','Expr'])

# If/While/Do-While
G['IfStmt'].append(['SE','DELIM_ABREP','Expr','DELIM_FECHAP','Statement','IfElseOpt'])
G['IfElseOpt'].append([EPS])
G['IfElseOpt'].append(['SENAO','Statement'])


G['WhileStmt'].append(['ENQUANTO','DELIM_ABREP','Expr','DELIM_FECHAP','Statement'])

G['DoWhileStmt'].append(['FACA','Statement','ENQUANTO','DELIM_ABREP','Expr','DELIM_FECHAP','DELIM_PONTOVIR'])

# For estilo C: for ( [init] ; [cond] ; [update] ) Statement
G['ForInit'].append(['Data_Type','ID','OP_ATRIB','Expr'])
G['ForInit'].append(['ID','OP_ATRIB','Expr'])
G['ForInitOpt'].append(['ForInit'])
G['ForInitOpt'].append([EPS])
G['ExprOpt'].append(['Expr'])
G['ExprOpt'].append([EPS])
G['ForAssignOpt'].append(['ForAssign'])
G['ForAssignOpt'].append([EPS])
G['ForStmt'].append(['PARA','DELIM_ABREP','ForInitOpt','DELIM_PONTOVIR','ExprOpt','DELIM_PONTOVIR','ForAssignOpt','DELIM_FECHAP','Statement'])

# Parâmetros e chamadas
G['ParamListOpt'].append(['ParamList'])
G['ParamListOpt'].append([EPS])

G['ParamList'].append(['Data_Type','ID','ParamListTail'])
G['ParamListTail'].append(['DELIM_VIRG','Data_Type','ID','ParamListTail'])
G['ParamListTail'].append([EPS])

# FunctionCall (mantida como não-terminal, mas em Statement usamos via IdStmt)
G['FunctionCall'].append(['ID','DELIM_ABREP','ArgListOpt','DELIM_FECHAP','DELIM_PONTOVIR'])

G['ArgListOpt'].append(['ArgList'])
G['ArgListOpt'].append([EPS])

G['ArgList'].append(['Expr','ArgListTail'])
G['ArgListTail'].append(['DELIM_VIRG','Expr','ArgListTail'])
G['ArgListTail'].append([EPS])

# I/O e retorno
G['WriteStmt'].append(['ESCREVA','DELIM_ABREP','ArgListOpt','DELIM_FECHAP','DELIM_PONTOVIR'])

G['ReturnStmt'].append(['RETORNA','ReturnExprOpt','DELIM_PONTOVIR'])
G['ReturnExprOpt'].append(['Expr'])
G['ReturnExprOpt'].append([EPS])

# EXPRESSÕES (precedência e associatividade à esquerda)
G['Expr'].append(['OrExpr'])

G['OrExpr'].append(['AndExpr','OrTail'])
G['OrTail'].append(['OP_OU','AndExpr','OrTail'])
G['OrTail'].append([EPS])

G['AndExpr'].append(['EqExpr','AndTail'])
G['AndTail'].append(['OP_E','EqExpr','AndTail'])
G['AndTail'].append([EPS])

G['EqExpr'].append(['RelExpr','EqTail'])
G['EqTail'].append(['OP_IGUALDADE','RelExpr','EqTail'])
G['EqTail'].append(['OP_DIFERENCA','RelExpr','EqTail'])
G['EqTail'].append([EPS])

G['RelExpr'].append(['AddExpr','RelTail'])
G['RelTail'].append(['OP_MAIOR','AddExpr','RelTail'])
G['RelTail'].append(['OP_MENOR','AddExpr','RelTail'])
G['RelTail'].append(['OP_MAIORIGUAL','AddExpr','RelTail'])
G['RelTail'].append(['OP_MENORIGUAL','AddExpr','RelTail'])
G['RelTail'].append([EPS])

G['AddExpr'].append(['MulExpr','AddTail'])
G['AddTail'].append(['OP_SOMA','MulExpr','AddTail'])
G['AddTail'].append(['OP_SUB','MulExpr','AddTail'])
G['AddTail'].append([EPS])

G['MulExpr'].append(['UnaryExpr','MulTail'])
G['MulTail'].append(['OP_MULTI','UnaryExpr','MulTail'])
G['MulTail'].append(['OP_DIV','UnaryExpr','MulTail'])
G['MulTail'].append(['OP_PERCENT','UnaryExpr','MulTail'])
G['MulTail'].append([EPS])

G['UnaryExpr'].append(['OP_NAO','UnaryExpr'])
G['UnaryExpr'].append(['Primary'])

G['Primary'].append(['DELIM_ABREP','Expr','DELIM_FECHAP'])
G['Primary'].append(['ID'])
G['Primary'].append(['INT_LIT'])
G['Primary'].append(['FLOAT_LIT'])
G['Primary'].append(['BOOLEAN_LIT'])
G['Primary'].append(['CHAR_LIT'])
G['Primary'].append(['STRING'])
