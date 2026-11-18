"""Recompute public statistics from verified, non-secret hardware receipts."""
import argparse,json,math
from pathlib import Path
from scripts.biohydrogen_patent_model import circuit,observe


def analyze(journal,local):
    rows=[];receipts={}
    for reading in ['text_cnot','figure_cz']:
        for stage in ['initial','optimized']:
            prefix=f'biohydrogen-{reading}-{stage}'
            z=journal['jobs'][prefix+'-Z']['receipt'];x=journal['jobs'][prefix+'-X']['receipt']
            def moment(receipt,fn):
                counts=receipt['counts_q0_first'];n=sum(counts.values())
                m=sum(v*fn(k) for k,v in counts.items())/n
                variance=sum(v*(fn(k)-m)**2 for k,v in counts.items())/(n-1)/n
                return m,variance
            zm,zv=moment(z,lambda b:(-1)**(int(b[1])+int(b[2])))
            xm,xv=moment(x,lambda b:(-1)**int(b[1])+(-1)**int(b[2]))
            n=sum(z['counts_q0_first'].values());ph=z['counts_q0_first'].get('111',0)/n
            zz=1.959963984540054;den=1+zz**2/n
            center=(ph+zz**2/(2*n))/den
            half=zz*math.sqrt(ph*(1-ph)/n+zz**2/(4*n*n))/den
            theta=None if stage=='initial' else local['interpretations'][reading]['best']['theta']
            ideal=observe(circuit(theta=theta,interpretation=reading))
            row={'reading':reading,'stage':stage,'energy_dimensionless':zm+xm,
                 'standard_error':math.sqrt(zv+xv),'p111':ph,'p111_wilson95':[center-half,center+half],
                 'ideal_energy_dimensionless':ideal['energy_dimensionless'],'ideal_p111':ideal['p111'],
                 'energy_error_vs_local':zm+xm-ideal['energy_dimensionless'],
                 'shots_per_basis':[z['shots_returned'],x['shots_returned']],
                 'task_ids':[z['task_id'],x['task_id']]}
            tv=[]
            for basis,receipt in [('Z',z),('X',x)]:
                if receipt['mode']!='cloud_hardware' or receipt['status']!='Finished' or receipt['backend']!='Baihua':
                    raise ValueError('Missing genuine finished Baihua receipt')
                c=circuit(theta=theta,interpretation=reading)
                if basis=='X':c.h(1).h(2)
                idealp=observe(c)['probabilities_q0_first'];cnt=receipt['counts_q0_first'];nn=sum(cnt.values())
                if nn!=receipt['shots_returned']:raise ValueError('Counts do not reconcile')
                tv.append(sum(abs(idealp[b]-cnt.get(b,0)/nn) for b in idealp)/2)
                receipts[prefix+'-'+basis]=receipt
            row['total_variation_per_basis']=tv;rows.append(row)
    return {'schema':'qb-biohydrogen-hardware-evidence-v1','target':'Baihua','sdk':journal['sdk'],
      'verified_tasks':len(receipts),'submitted_tasks':len(journal['jobs']),'mode':'cloud_hardware',
      'note':'Classically optimized angles evaluated on hardware; not hardware-in-the-loop VQE. No biological hydrogen experiment.',
      'energy_statistics':'ZZ from Z basis; XI+IX evaluated per shared X shot, including covariance. Distinct bases assumed independent. SE captures sampling, not calibration bias or hardware drift.',
      'rows':rows,'receipts':receipts}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--journal',required=True);p.add_argument('--local',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=analyze(json.loads(Path(a.journal).read_text()),json.loads(Path(a.local).read_text()))
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'verified_tasks':result['verified_tasks'],'rows':result['rows']},indent=2))
