import json
from collections import defaultdict
def load(nome):
    d=json.load(open(f'ext/pam_{nome}.json'))
    t=defaultdict(dict)
    for r in d[1:]:
        v=r['V']
        try: v=float(v)
        except: v=None
        t[int(r['D3N'])][{'112':'rend','214':'qtd','215':'valor','216':'area_col','8331':'area_plant'}[r['D2C']]]=v
    return dict(t)
