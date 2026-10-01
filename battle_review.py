"""Reviewed experimental battlefield-duel evidence, separate from the shipped PCK."""
import hashlib,json

PINS={
 'logic':('duel-battle-navigation-validation-r2.json','f1ab981b4b07ef7f16eff2dfa19771ffccfade00431e34365e25d43d826bb689'),
 'terrain':('duel-battle-surface-validation-r1.json','33b4b50b4be7e325b091cbccd5bd2c57e4d0170c54ef8ff57d31beff0918a6c1'),
 'mask':('duel-battle-gpu-mask-r1.json','a2d92243e8bb8b50393d95ec7ebb5d3acb02555afa7710be3bd11a0767f0b5dd'),
 'render':('duel-battle-navigation-gpu-r4.json','8b25451558012b6ffe790cd17032dcc7cba3170bdaeaf7859fbdc93d7c09a0a3'),
}
def read(root):
 reports={}
 for key,(name,expected) in PINS.items():
  path=root/'artifacts'/name
  if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Battlefield prototype report changed: '+key)
  reports[key]=json.loads(path.read_text(encoding='utf-8'))
  if reports[key].get('failures')!=[]:raise ValueError('Battlefield prototype has failed checks')
 logic=reports['logic'];render=reports['render'];terrain=reports['terrain'];mask=reports['mask']
 if logic.get('passed')!=221 or len(logic.get('cases',[]))!=20 or logic.get('sources_before')!=logic.get('sources_after'):raise ValueError('Battlefield prototype logic scope is incomplete')
 for name,expected in logic['sources_before'].items():
  path=root/name.removeprefix('res://')
  if name.startswith('res://src/'):path=root/'artifacts/pre-full-battle-duel-build'/name.removeprefix('res://')
  if name=='res://assets/animations/duel-exchanges.json':path=root/'artifacts/pre-motion-flow-source/duel-exchanges.json'
  if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Archived battlefield prototype source changed')
 pairs={(a,b) for a in range(4) for b in range(4) if a!=b}
 if {tuple(row['pair']) for row in logic['cases'] if row['intent']=='none'}!=pairs:raise ValueError('Battlefield prototype pairs are incomplete')
 for row in logic['cases']:
  if (row.get('agents')!=320 or row.get('contact_errors')!=[] or row.get('projectile_age_errors')!=0
      or row.get('hero_draw_mask_errors')!=0 or row.get('maximum_pelvis_adjustment_m',1)>=.18
      or row.get('maximum_planted_ground_error_m',1)>=.003):raise ValueError('Battlefield prototype case failed')
 if mask.get('passed')!=4 or sum(row.get('readbacks',0) for row in mask.get('records',[]))!=12 or any(row.get('maximum_hidden_scale',1)!=0 for row in mask['records']):raise ValueError('Battlefield prototype GPU draw evidence is missing')
 if (terrain.get('compared_points')!=256 or terrain.get('maximum_height_error_m',1)>.0001
     or render.get('source_unchanged') is not True or render.get('native_frames_written')!=799
     or render.get('native_render_size')!=[1920,1080] or render.get('battlefield_agents')!=320
     or len(render.get('skin_readbacks',[]))!=18 or any(not row['comparison']['valid'] for row in render['skin_readbacks'])):raise ValueError('Battlefield prototype terrain/render scope changed')
 return {'status':'prototype','productionIntegrated':False,'agents':320,'matches':20,'checks':221,'orderedPairs':12,
  'gpuInstanceReadbacks':12,'gpuSkinReadbacks':18,'terrainComparisonPoints':256,'measuredContactDirections':['zhangfei->lubu']}

def validate_public(data):
 expected={'status':'prototype','productionIntegrated':False,'agents':320,'matches':20,'checks':221,'orderedPairs':12,
  'gpuInstanceReadbacks':12,'gpuSkinReadbacks':18,'terrainComparisonPoints':256,'measuredContactDirections':['zhangfei->lubu']}
 if data!=expected:raise ValueError('Battlefield prototype cannot be promoted or expanded without review')
