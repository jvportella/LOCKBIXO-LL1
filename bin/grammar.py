# executaveis/grammar.py — MESMA GRAMÁTICA, AGORA COM MARCAÇÕES DIDÁTICAS
from collections import defaultdict

EPS = 'ε'
START_SYMBOL = 'Program'

NONTERMS = [
    'Program','StmtList','Statement','Block',
    'DeclOrFunc','DeclOrFuncTail','FunctionDeclVoid','VarDeclTail',
    'IdStmt','IdStmtTail',                 # <-- [FATORAÇÃO] prefixo comum "ID ..."
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

# ---------------------------------------------------------------------------------
# PROGRAMA
# ---------------------------------------------------------------------------------
# Program -> StmtList EOF
G['Program'].append(['StmtList','EOF'])

# StmtList -> Statement StmtList | ε
G['StmtList'].append(['Statement','StmtList'])
G['StmtList'].append([EPS])

# ---------------------------------------------------------------------------------
# STATEMENT SET (ordem importa; sem ambiguidade de prefixos)
# ---------------------------------------------------------------------------------
G['Statement'].extend([
    ['DeclOrFunc'],         # Data_Type ID ...  (pode ser decl ou função)  [FATORAÇÃO]
    ['FunctionDeclVoid'],   # void ID (...) { ... }
    ['IdStmt'],             # ID ...  (atribuição OU chamada)              [FATORAÇÃO]
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

# ---------------------------------------------------------------------------------
# [FATORAÇÃO 1] "Data_Type ID ..." → Declaração ou Função com tipo
# - Resolve ambiguidade de prefixo comum (Data_Type ID)
# - 1 token de lookahead depois de ID decide: '(' → função | '='/';' → declaração
# ---------------------------------------------------------------------------------
# DeclOrFunc -> Data_Type ID DeclOrFuncTail
G['DeclOrFunc'].append(['Data_Type','ID','DeclOrFuncTail'])

# DeclOrFuncTail -> ( ParamListOpt ) Block  |  VarDeclTail ;
G['DeclOrFuncTail'].append(['DELIM_ABREP','ParamListOpt','DELIM_FECHAP','Block'])     # '(' → função
G['DeclOrFuncTail'].append(['VarDeclTail','DELIM_PONTOVIR'])                           # '=' ou ';' → var

# VarDeclTail -> = Expr | ε
G['VarDeclTail'].append(['OP_ATRIB','Expr'])
G['VarDeclTail'].append([EPS])

# Função void explícita (sem conflito com DeclOrFunc)
G['FunctionDeclVoid'].append(['VAZIO','ID','DELIM_ABREP','ParamListOpt','DELIM_FECHAP','Block'])

# ---------------------------------------------------------------------------------
# [FATORAÇÃO 2] Tudo que começa com "ID" dentro de Statement
# - Resolve ambiguidade chamada vs atribuição usando lookahead '=' ou '('
# ---------------------------------------------------------------------------------
# IdStmt -> ID IdStmtTail
G['IdStmt'].append(['ID','IdStmtTail'])

# IdStmtTail -> = Expr ;    (Assignment)
#            | ( ArgListOpt ) ;  (FunctionCall)
G['IdStmtTail'].append(['OP_ATRIB','Expr','DELIM_PONTOVIR'])
G['IdStmtTail'].append(['DELIM_ABREP','ArgListOpt','DELIM_FECHAP','DELIM_PONTOVIR'])

# Reuso (for/update)
G['Assignment'].append(['ID','OP_ATRIB','Expr','DELIM_PONTOVIR'])
G['ForAssign'].append(['ID','OP_ATRIB','Expr'])

# ---------------------------------------------------------------------------------
# IF / WHILE / DO-WHILE (sem ambiguidade; FIRST distintos)
# ---------------------------------------------------------------------------------
G['IfStmt'].append(['SE','DELIM_ABREP','Expr','DELIM_FECHAP','Statement','IfElseOpt'])
G['IfElseOpt'].append([EPS])
G['IfElseOpt'].append(['SENAO','Statement'])

G['WhileStmt'].append(['ENQUANTO','DELIM_ABREP','Expr','DELIM_FECHAP','Statement'])

G['DoWhileStmt'].append(['FACA','Statement','ENQUANTO','DELIM_ABREP','Expr','DELIM_FECHAP','DELIM_PONTOVIR'])

# ---------------------------------------------------------------------------------
# FOR estilo C: for ( [init] ; [cond] ; [update] ) Statement
# - Fatorações locais via *_Opt para permitir vazio (ε) nos 3 campos
# ---------------------------------------------------------------------------------
G['ForInit'].append(['Data_Type','ID','OP_ATRIB','Expr'])   # int i = 0
G['ForInit'].append(['ID','OP_ATRIB','Expr'])               # i = 0
G['ForInitOpt'].append(['ForInit'])
G['ForInitOpt'].append([EPS])

G['ExprOpt'].append(['Expr'])
G['ExprOpt'].append([EPS])

G['ForAssignOpt'].append(['ForAssign'])
G['ForAssignOpt'].append([EPS])

G['ForStmt'].append([
    'PARA','DELIM_ABREP',
    'ForInitOpt','DELIM_PONTOVIR',
    'ExprOpt','DELIM_PONTOVIR',
    'ForAssignOpt','DELIM_FECHAP',
    'Statement'
])

# ---------------------------------------------------------------------------------
# PARÂMETROS E CHAMADAS (apenas quando usados nas formas acima)
# ---------------------------------------------------------------------------------
G['ParamListOpt'].append(['ParamList'])
G['ParamListOpt'].append([EPS])

G['ParamList'].append(['Data_Type','ID','ParamListTail'])
G['ParamListTail'].append(['DELIM_VIRG','Data_Type','ID','ParamListTail'])
G['ParamListTail'].append([EPS])

# FunctionCall (não entra direto em Statement; é via IdStmtTail)
G['FunctionCall'].append(['ID','DELIM_ABREP','ArgListOpt','DELIM_FECHAP','DELIM_PONTOVIR'])

G['ArgListOpt'].append(['ArgList'])
G['ArgListOpt'].append([EPS])

G['ArgList'].append(['Expr','ArgListTail'])
G['ArgListTail'].append(['DELIM_VIRG','Expr','ArgListTail'])
G['ArgListTail'].append([EPS])

# ---------------------------------------------------------------------------------
# I/O e retorno
# ---------------------------------------------------------------------------------
G['WriteStmt'].append(['ESCREVA','DELIM_ABREP','ArgListOpt','DELIM_FECHAP','DELIM_PONTOVIR'])

G['ReturnStmt'].append(['RETORNA','ReturnExprOpt','DELIM_PONTOVIR'])
G['ReturnExprOpt'].append(['Expr'])
G['ReturnExprOpt'].append([EPS])

# ---------------------------------------------------------------------------------
# EXPRESSÕES — HIERARQUIA DE PRECEDÊNCIA (sem recursão à esquerda)
# - Esta “escadinha” substitui A → A op B (recursão à esquerda) por pares (N, NTail)
# - Garante associatividade à esquerda e remove recursão à esquerda direta
#   Ordem:  ||  >  &&  >  ==/!=  >  rel  >  +,-  >  *,/,%  >  unário  >  primário
# ---------------------------------------------------------------------------------
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

G['UnaryExpr'].append(['OP_NAO','UnaryExpr'])  # !x (associativo à direita)
G['UnaryExpr'].append(['Primary'])

G['Primary'].append(['DELIM_ABREP','Expr','DELIM_FECHAP'])  # (expr)
G['Primary'].append(['ID'])
G['Primary'].append(['INT_LIT'])
G['Primary'].append(['FLOAT_LIT'])
G['Primary'].append(['BOOLEAN_LIT'])
G['Primary'].append(['CHAR_LIT'])
G['Primary'].append(['STRING'])
