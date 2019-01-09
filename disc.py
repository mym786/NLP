#coding:utf-8  
# Compare the Similar Terms between Vocabase and Comp_list
import sys, os

pwd = sys.path[0]

# DISC Personality Expanded Vocabase
with open('C:/xampp/htdocs/eduai_jobot/module/NLP/Expansion_for_DISC/DVocabase_Expand.txt', encoding="utf-8") as f:
    dvocabase = f.read().splitlines()

with open('C:/xampp/htdocs/eduai_jobot/module/NLP/Expansion_for_DISC/EVocabase_Expand.txt', encoding="utf-8") as f:
    evocabase = f.read().splitlines()

with open('C:/xampp/htdocs/eduai_jobot/module/NLP/Expansion_for_DISC/PVocabase_Expand.txt', encoding="utf-8") as f:
    pvocabase = f.read().splitlines()

with open('C:/xampp/htdocs/eduai_jobot/module/NLP/Expansion_for_DISC/CVocabase_Expand.txt', encoding="utf-8") as f:
    cvocabase = f.read().splitlines()

def vocabase_score(compare):
    # Vocabase_Expand (Weight*1)
    ddiff = set(dvocabase).symmetric_difference(compare)
    dequ = list(set(dvocabase) - set(ddiff))
    dlen = len(dequ)

    ediff = set(evocabase).symmetric_difference(compare)
    eequ = list(set(evocabase) - set(ediff))
    elen = len(eequ)

    pdiff = set(pvocabase).symmetric_difference(compare)
    pequ = list(set(pvocabase) - set(pdiff))
    plen = len(pequ)

    cdiff = set(cvocabase).symmetric_difference(compare)
    cequ = list(set(cvocabase) - set(cdiff))
    clen = len(cequ)

    total = (dlen + elen + plen + clen)
    if(total != 0):
               
        dnorm = round((dlen ) / total * 100, 2)
        enorm = round((elen ) / total * 100, 2)
        pnorm = round((plen ) / total * 100, 2)
        cnorm = round((clen ) / total * 100, 2)
        
        score = [dnorm, enorm, pnorm, cnorm]
        return score
    else:
        return [25.0, 25.0, 25.0, 25.0]

if __name__ == "__main__":
    vocabase_score()
