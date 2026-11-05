import pathlib, subprocess, json, random, concurrent.futures, time, hashlib
import sys
root=pathlib.Path(sys.argv[1]).resolve()
if root.exists() and any(root.iterdir()): raise SystemExit('Use an empty evaluation directory; existing results will not be overwritten.')
root.mkdir(parents=True,exist_ok=True)
repo=pathlib.Path(__file__).resolve().parents[3]
cases=[
 {'id':'research','skill':'research','prompt':'Should we increase advertising spend based on these supplied results? January: £100 spend, 10 leads. February: £300 spend, 15 leads. The management summary says: "Lead volume grew 50%, so efficiency improved 50%." Recommend a decision using only these figures. Keep the answer under 220 words.'},
 {'id':'write','skill':'write','prompt':'Make this client proposal concise, preserving every commercial term: We expect delivery in six weeks, dependent on the client supplying approved photographs. Estimate £4,000, excluding hosting. The optional maintenance package costs £75 per month and can be cancelled with 30 days notice. Do not add claims or commitments. Return only the revised proposal.'},
 {'id':'design','skill':'design','prompt':'Critique a presentation slide using only this description: 12pt body text, an 8pt source note, three charts and a 90-word paragraph. Audience: a room of 40. The existing navy and cream identity must remain. No slide file, screenshot or renderer is available. Give the highest-priority improvements, without implementing changes. Keep the answer under 220 words.'},
 {'id':'review','skill':'review','prompt':'Review this existing document and supplied Python function. Return actionable findings only, with location, severity, trigger and smallest correction. Do not edit anything. Proposal page 2 says: "Delivery is guaranteed in six weeks." The approved brief says: "Expected delivery in six weeks after approved photographs arrive." Code at pricing.py:1-2 is: def cost_per_lead(spend, leads): return spend // leads. Callers pass nonnegative decimal spend and positive integer leads, and require the unrounded cost per lead. There is no Git diff. Keep the answer under 250 words.'}
]
plan={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'client':subprocess.check_output(['claude','--version'],text=True).strip(),'model':'client default; resolved model recorded from result modelUsage','constraints':'fresh process per answer; safe mode; no tools; no session persistence; no MCP; source-only tasks; no renderer','cases':cases,'limitations':'single sample per condition per case; tests instruction packet rather than automatic discovery; no native rendered artifact or executing code'}
evaldir=root/'evaluation';(evaldir/'raw').mkdir(parents=True,exist_ok=True)
(evaldir/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
rng=random.Random(20261105)
trials=[];mapping={}
for case in cases:
 conditions=['control','jstack'];rng.shuffle(conditions)
 for label,condition in zip(['A','B'],conditions):
  tid=case['id']+'-'+label;mapping[tid]=condition
  trials.append((tid,case,condition))
(evaldir/'mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
common=['claude','--safe-mode','-p','--tools','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--output-format','json','--no-session-persistence']
def run(trial):
 tid,case,condition=trial
 packet=''
 if condition=='jstack':
  packet=(repo/'shared/rules.md').read_text()+'\n'+(repo/'skills'/case['skill']/'SKILL.md').read_text()
  for p in sorted((repo/'skills'/case['skill']/'references').glob('*.md')): packet+='\n'+p.read_text()
  packet+='\nAll necessary skill references are included above. Apply the relevant guidance; no tools are available.'
 args=common+(['--append-system-prompt',packet] if packet else [])+[case['prompt']]
 start=time.time()
 try:
  p=subprocess.run(args,cwd=evaldir,capture_output=True,text=True,timeout=180)
  (evaldir/'raw'/(tid+'.stdout.json')).write_text(p.stdout);(evaldir/'raw'/(tid+'.stderr')).write_text(p.stderr)
  d=json.loads(p.stdout)
  output={'id':tid,'exit':p.returncode,'is_error':d.get('is_error'),'output':d.get('result'),'models':list(d.get('modelUsage',{})),'seconds':round(time.time()-start,1),'usage':d.get('usage'),'packet_sha256':hashlib.sha256(packet.encode()).hexdigest() if packet else None}
 except Exception as e:
  output={'id':tid,'error':str(e),'seconds':round(time.time()-start,1)}
 (evaldir/(tid+'.json')).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 return {k:v for k,v in output.items() if k not in ['output','usage','packet_sha256']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(run,trials): print(json.dumps(result),flush=True)
