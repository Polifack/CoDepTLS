# COMMON CONSTANTS

EOS = "-EOS-"
BOS = "-BOS-"

F_CONSTITUENT = "CONST"
F_DEPENDENCY = "DEPS"

OP_ENC = "ENC"
OP_DEC = "DEC"

# CONSTITUENT ENCODINGS

C_ABSOLUTE_ENCODING = 'ABS'
C_RELATIVE_ENCODING = 'REL'
C_DYNAMIC_ENCODING = 'DYN'
C_GAPS_ENCODING = 'GAP'
C_TETRA_ENCODING = '4EC'
C_JUXTAPOSED_ENCODING = 'JUX'

C_STRAT_FIRST="strat_first"
C_STRAT_LAST="strat_last"
C_STRAT_MAX="strat_max"
C_STRAT_NONE="strat_none"

# CONSTITUENT MISC

C_NONE_LABEL = "-NONE-"
C_NO_POSTAG_LABEL = "-NOPOS-"
C_ROOT_LABEL = "-ROOT-"
C_END_LABEL = "-END-"
C_START_LABEL = "-START-"
C_CONFLICT_SEPARATOR = "-||-"
C_DUMMY_END = "DUMMY_END"

# DEPENDENCIY ENCODINGS

D_NONE_LABEL = "-NONE-"

D_ABSOLUTE_ENCODING = 'ABS'
D_RELATIVE_ENCODING = 'REL'
D_POS_ENCODING = 'POS'
D_BRACKET_ENCODING = 'BRK'
D_BRACKET_ENCODING_2P = 'BRK_2P'
D_BRK_4B_ENCODING = 'BRK_4B'
D_BRK_7B_ENCODING = 'BRK_7B'

D_2P_GREED = 'GREED'
D_2P_PROP = 'PROPAGATE'

# DEPENDENCY MISC

D_EMPTYREL = "-NOREL-"
D_POSROOT = "-ROOT-"
D_NULLHEAD = "-NULL-"

D_ROOT_HEAD = "strat_gethead"
D_ROOT_REL = "strat_getrel"
