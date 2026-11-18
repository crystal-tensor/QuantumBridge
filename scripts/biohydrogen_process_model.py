"""Transparent normalized process model for light/oxygen/electron-allocation studies.

This is a mechanism-inspired numerical experiment, not a fitted biological twin.
Every rate constant below is an author-selected dimensionless scenario parameter.
No output carries physical hydrogen-production units or hardware claims.
"""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import argparse
import json
import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class Parameters:
    input_light: float = 1.0
    duty: float = 1.0
    period: float = 2.0
    oxygen_removal: float = 0.2
    electron_allocation: float = 0.65
    excitation: float = 0.8
    hydrogenase_capacity: float = 0.6
    competing_sink: float = 0.25
    recombination: float = 0.08
    oxygen_damage: float = 0.6
    duration: float = 40.0


def simulate(p=Parameters(),dt=0.05,rtol=1e-8,atol=1e-10):
    if not (0<p.duty<=1 and p.period>0 and p.duration>0 and dt>0):
        raise ValueError('Positive duration, period and step; duty in (0,1] required')
    if not 0<=p.electron_allocation<=1:
        raise ValueError('Allocation must be a fraction')
    if any(v<0 for k,v in asdict(p).items()):
        raise ValueError('Negative scenario parameter')
    # e = stored electron equivalents, o = oxygen, a = surviving enzyme fraction,
    # h = cumulative H2 equivalents, q = input electrons, c = competing electrons,
    # r = recombined electrons, removed = cumulative oxygen removed.
    def rhs(light):
        def derivative(t,y):
            e,o,a,h,q,c,r,removed=y
            source=p.excitation*light*max(0,1-e)
            f_h=p.hydrogenase_capacity*p.electron_allocation*max(0,a)*max(0,e)
            f_c=p.competing_sink*(1-p.electron_allocation)*max(0,e)
            f_r=p.recombination*max(0,e)
            f_out=p.oxygen_removal*max(0,o)
            return [source-f_h-f_c-f_r,source/4-f_out,
                    -p.oxygen_damage*max(0,o)*max(0,a),f_h/2,source,f_c,f_r,f_out]
        return derivative
    # Explicit integration intervals at each light discontinuity prevent a solver
    # from skipping short pulses. Mean incident photon budget is held constant.
    edges={0.0,p.duration}
    if p.duty<1:
        for start in np.arange(0,p.duration,p.period):
            edges.update([float(start),min(float(start+p.period*p.duty),p.duration),min(float(start+p.period),p.duration)])
    edges=sorted(edges); state=np.array([0,0,1,0,0,0,0,0],float)
    times=[0.0];states=[state.copy()]
    for start,end in zip(edges[:-1],edges[1:]):
        phase=((start+end)/2)%p.period
        light=p.input_light/p.duty if p.duty==1 or phase<p.period*p.duty else 0
        grid=np.arange(start+dt,end,dt);grid=np.append(grid,end)
        sol=solve_ivp(rhs(light),(start,end),state,t_eval=grid,rtol=rtol,atol=atol,max_step=min(dt,p.period*p.duty/4))
        if not sol.success:raise RuntimeError(sol.message)
        times.extend(sol.t.tolist());states.extend(sol.y.T.tolist());state=sol.y[:,-1]
    a=np.asarray(states);t=np.asarray(times)
    electron_residual=a[:,4]-a[:,0]-2*a[:,3]-a[:,5]-a[:,6]
    oxygen_residual=a[:,4]/4-a[:,1]-a[:,7]
    return {'parameters':asdict(p),'units':'dimensionless normalized scenario',
            'parameter_origin':'author-selected; not fitted to a paper, organism or reactor',
            'time':t.tolist(),'states':a.tolist(),
            'state_columns':['electrons','oxygen','active_enzyme','H2_equivalents','input_electrons','competing_electrons','recombined_electrons','removed_oxygen'],
            'summary':{'H2_equivalents':float(a[-1,3]),'active_enzyme':float(a[-1,2]),
                       'electron_balance_max_error':float(np.max(np.abs(electron_residual))),
                       'oxygen_balance_max_error':float(np.max(np.abs(oxygen_residual))),
                       'incident_light_integral':p.input_light*p.duration}}


def export(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    base=Parameters()
    scenarios={
      'constant_light':base,
      'pulsed_equal_photons':replace(base,duty=.25),
      'oxygen_management':replace(base,oxygen_removal=1.0),
      'electron_rerouting':replace(base,electron_allocation=.9),
      'combined_controls':replace(base,oxygen_removal=1.0,electron_allocation=.9,duty=.25),
    }
    result={'schema':'qb-biohydrogen-process-v1','scope':'Qualitative mechanism-inspired scenarios, not biological validation',
      'as_of':'2026-11-18','sources':[
        {'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC7703569/','supports':'water oxidation, electron allocation and oxygen sensitivity; does not supply scenario rates'},
        {'url':'https://pubmed.ncbi.nlm.nih.gov/40265210/','year':2025,'supports':'oxygen monitoring/management and moderate light in pgr5 cultures; separate physical experiment'},
        {'url':'https://doi.org/10.1002/cmtd.70175','year':2026,'supports':'whole-cell electron allocation and oxygen management; different cyanobacterial system'}],
      'scenarios':{key:simulate(p) for key,p in scenarios.items()}}
    (out/'process-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v['summary'] for k,v in result['scenarios'].items()},indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    export(parser.parse_args().output)
