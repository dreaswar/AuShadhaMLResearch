###############################################
#
# Clubfoot Models
#
###############################################

import pandas as pd

CLUBFOOT_REG_DS = {"ID": [],
                   "Side": [],
                   "Type": [],
                   "Notes": []
                   }

CLUBFOOT_REG_DF = pd.DataFrame([],
                               columns=list(CLUBFOOT_REG_DS.keys()))
