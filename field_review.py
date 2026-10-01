"""Curated evidence for the adopted moving-duel package, with exact review pins."""
import hashlib,json
from pathlib import Path

PCK="235db6c2ba8c4e97f67c9455d1b01fbd19a522151133d4ddaa9ddcda7719bfd3"
CATALOG="37e6dc3f81db2c4c5319cdc5df4e7d8f3085ec5bf273a71f9d2cde494e259c4a"
MODELS={
 "lubu":("assets/models/heroes/field/lubu.glb","d74c3e065720e64d6b69f20f7f117b9c7695cdaa3253739c7d73c685e09fcfd6"),
 "guanyu":("assets/models/heroes/arm_v3/guanyu.glb","53d7d92dfba7d3a40afa2fc41118d5c1233d176d1355329b1a5a64d14af7e708"),
 "zhangfei":("assets/models/heroes/arm_v3/zhangfei.glb","08a14d403c09da4d43bd3794257f043c9d9e9252150c8e57d5ba2a9e01056592"),
 "machao":("assets/models/heroes/arm_v3/machao.glb","73f44e4bfaae268721088d403735b335aa1720e340daabaaa26a9e060ef3e6ec"),
}
REPORTS={
 "gallery":("flow-gallery-r1.json","6ef0245b71886e600a93ce741e87d1b4d2044d73c6bd60cd893414bc1a527b1a"),
 "pairs":("flow-production-pairs-r1.json","be33eb054c1d76851b60a628642678b53d1c2676797a4f84ee6c02212d9f3e12"),
 "packed":("flow-pack-duel-r1.json","e9dd17dfb90c463ffa15ff176211b1d9151d7e1f74c29e45718aaa621f20fd56"),
 "gpu":("flow-pack-skin-gpu-r1.json","4637425d1e492048d7ea6deca44e3252b42a979a49b0b33b62dd536bfb58226f"),
 "art":("flow-pack-art-r1.json","099a8268657606e982e901cd9f9f67e6371c9e121b66420cbc6e4b32211409c3"),
 "inputs":("flow-production-input-r1.json","3dec8d2cc8b7ccf2f0a6e6937f05883fbd67286aebde8ee7f298a140e1231b83"),
 "main_battle":("flow-pack-main-battle-r1.json","8859a92b6a6d2bae2f72a35a2294d4853f269a1396db3aa5d5b26bc452cd2d60"),
 "main_gpu":("flow-pack-main-gpu-r1.json","e0a88b582b6325da63adebd5253deb2113cd857001605c4e2ec674815be1d7b8"),
}
CURVE="7a0a0980e6b399c7fc81013387055dd467a4bcd6a122ca8bb654600a73a89466"

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

def read(root):
 def load(name):return json.loads((root/name).read_text(encoding='utf-8-sig'))
 manifest=load('build/Tianxia-flow/build-manifest.json')
 if manifest.get('packaged_sha256',{}).get('Tianxia.pck')!=PCK or sha(root/'build/Tianxia-flow/Tianxia.pck')!=PCK:
  raise ValueError('Field package differs from its reviewed bytes')
 if manifest.get('source_unchanged_during_export_and_validation') is not True:raise ValueError('Field export did not preserve sources')
 for name,expected in manifest.get('source_sha256',{}).items():
  path=(root/name).resolve()
  if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path)!=expected:raise ValueError('Field source changed after review: '+name)
 for name,expected in [*MODELS.values(),('assets/animations/duel-exchanges.json',CURVE),('assets/data/officers.json',CATALOG)]:
  if sha(root/name)!=expected or manifest['source_sha256'].get(name)!=expected:raise ValueError('Field model/motion/catalog changed: '+name)
 reports={}
 for key,(name,expected) in REPORTS.items():
  path=root/'artifacts'/name
  if not path.is_file() or sha(path)!=expected:raise ValueError('Field reviewed report changed: '+key)
  report=load('artifacts/'+name)
  if report.get('failures')!=[]:raise ValueError('Field report contains failures: '+key)
  reports[key]=report
 gallery=reports['gallery']
 if gallery.get('passed')!=127 or len(gallery.get('heroes',[]))!=4 or gallery.get('sources_before')!=gallery.get('sources_after'):raise ValueError('Field gallery evidence changed')
 for hero in gallery['heroes']:
  name,expected=MODELS[hero['hero']]
  if hero.get('model')!='res://'+name or hero.get('model_sha256')!=expected or hero.get('authored') is not True:raise ValueError('Field gallery model differs from runtime')
 for name,expected in gallery['sources_before'].items():
  if sha(root/name.removeprefix('res://'))!=expected:raise ValueError('Reused gallery dependency changed: '+name)
 inputs=reports['inputs']
 if (inputs.get('passed')!=489 or len(inputs.get('cases',[]))!=48 or inputs.get('baseline_runtime') is not True
     or inputs.get('case_filter')!='' or inputs.get('sources_before')!=inputs.get('sources_after')):raise ValueError('Field input suite is incomplete')
 expected_inputs={f'slot{s}/{fps}fps/{intent}' for s in (0,1) for fps in (15,30,60,144) for intent in ('none','parry','dodge','guarded','skip','aggressive')}
 if {row.get('label') for row in inputs['cases']}!=expected_inputs:raise ValueError('Field input cases differ from review')
 for row in inputs['cases']:
  if (row.get('errors')!=[] or row.get('bad_contacts')!=0 or row.get('hp_prefix_errors')!=0 or row.get('effect_prefix_errors')!=0
      or row.get('duplicate_resolutions')!=0 or row.get('max_hip_m',1)>.18 or row.get('max_foot_error_m',1)>.025
      or row.get('max_planted_sole_plane_error_m',1)>.003):raise ValueError('Field input/foot evidence failed')
 for name,expected in inputs['sources_before'].items():
  if sha(root/name.removeprefix('res://'))!=expected:raise ValueError('Reviewed input producer changed: '+name)
 pairs=reports['pairs']
 expected_pairs={a+'->'+b for a in MODELS for b in MODELS if a!=b}
 if pairs.get('passed')!=84 or pairs.get('weighted_lubu') is not True or {row.get('pair') for row in pairs.get('cases',[])}!=expected_pairs:raise ValueError('Field needs all 12 ordered hero pairs')
 for row in pairs['cases']:
  if (row.get('contact_errors')!=[] or row.get('max_radius_m',0)<=3 or row.get('max_plant_slide_m',1)>=.002
      or row.get('max_foot_ik_error_m',1)>=.025 or row.get('max_sole_plane_error_m',1)>=.003 or row.get('max_pelvis_adjustment_m',1)>=.18
      or row.get('result',{}).get('outcome') not in ('surrender','death')):raise ValueError('Field traversal/foot evidence failed')
 packed=reports['packed'];gpu=reports['gpu'];art=reports['art']
 main=reports['main_battle'];main_gpu=reports['main_gpu']
 if main.get('passed')!=18 or {tuple(row['pair']) for row in main.get('cases',[])}!={(0,2),(2,0)}:raise ValueError('Normal battle integration evidence is incomplete')
 for row in main['cases']:
  if (row.get('agents')!=5184 or row.get('body_hits',0)==0 or row.get('contact_errors')!=[]
      or row.get('battle_seconds_after_result',0)<1 or row.get('maximum_pelvis_adjustment_m',1)>=.18
      or row.get('result',{}).get('outcome') not in ('surrender','death')):raise ValueError('Normal battle integration case failed')
 if main_gpu.get('agents')!=5184 or len(main_gpu.get('readbacks',[]))!=6 or any(row.get('scale',1)!=0 for row in main_gpu['readbacks']):raise ValueError('Normal battle GPU masks were not confirmed')
 if any(r.get('pck_sha256')!=PCK for r in (packed,gpu,art)):raise ValueError('Field reports attest a different package')
 if packed.get('passed')!=19 or {tuple(row['pair']) for row in packed.get('matches',[])}!={(2,0),(0,2)}:raise ValueError('Field packed matches missing')
 if any(row.get('weighted_body_hits',0)==0 or row.get('surface_gap_m',1)>=.001 for row in packed['matches']):raise ValueError('Field must hit actual weighted body surfaces')
 readbacks=gpu.get('skin_readbacks',[])
 if gpu.get('render_size')!=[1920,1080] or len(readbacks)!=10 or any(not row.get('comparison',{}).get('valid') for row in readbacks):raise ValueError('Field GPU skin proof missing')
 if art.get('passed')!=16 or art.get('portraits')!=16 or art.get('reference_ids')!=1000 or art.get('catalog_sha256')!=CATALOG:raise ValueError('Field art/roster counts changed')
 portable={}
 for mode in ('menu','duel','heroes'):
  report=load('artifacts/portable-validation-'+mode+'.json');recorded=manifest.get('headless_checks',{}).get(mode,{})
  if report.get('passed')!=92 or report.get('failures')!=[] or report.get('launch_mode')!=mode or report.get('pck_sha256')!=PCK or recorded.get('passed')!=92:raise ValueError('Field portable mode evidence changed')
  portable[mode]=92
 return {
  'currentRevision':'field-v4','portablePckSha256':PCK,'portableByMode':portable,'modelSha256':{key:row[1] for key,row in MODELS.items()},
  'modelRevisions':{'lubu':'field/v1f','guanyu':'arm_v3','zhangfei':'arm_v3','machao':'arm_v3'},'pairedCurveRevision':'v5 continuity-v2 + measured Zhang/Lu contacts','pairedCurveSha256':CURVE,
  'galleryChecks':127,'galleryHeroes':4,'roamingChecks':84,'roamingMatchups':12,'packedRuntimeChecks':19,'gpuSkinReadbacks':10,
  'cadenceInputChecks':489,'cadenceInputMatches':48,'cadenceRevision':'r3',
  'normalBattleChecks':18,'normalBattleAgents':5184,'normalBattleOrders':2,'normalBattleGpuReadbacks':6,
  'inputMaximumPelvisAdjustmentCm':round(max(row['max_hip_m'] for row in inputs['cases'])*100,2),
  'maximumPelvisAdjustmentCm':round(max(row['max_pelvis_adjustment_m'] for row in pairs['cases'])*100,2),
  'weightedHeroes':['lubu'],'measuredContactDirections':['zhangfei->lubu'],
  'groundingChecks':0,'approachChecks':0,'pairedOpponentChecks':0,'pairedMatchups':12,'pairedSampleHz':60,
  'pairedActorPairPoses':sum(row['frames'] for row in pairs['cases']),'pairedArmChecks':0,'genericArmChecks':0,
  'artPackageChecks':16,'packedPortraits':16,'catalogSha256':CATALOG,'experimentalPelvisAssetsPackaged':False,
  'referenceVideos':2,'referenceFrames':439,'comparisonFrames':58,'referenceViewerUiChecks':11,
  'referenceSnapshot':'과거 H 참고 비교 기록','scope':'이동하는 기본 일기토와 여포 가중 허리·망토를 연결한 실행본. 12조합 이동/접지와 실제 패키지·GPU를 검증했습니다. 표면 타격은 장비→여포이며 다른 방향의 정확한 무기 충돌, 전체 장수 스키닝·자유 지형/병사 회피·공방 자연스러움은 미완료입니다. 과거 I/arm_v3의169개 envelope 및 팔 정점 검사를 이 새 명단의 통과로 재사용하지 않습니다.'
 }

def validate_public(data):
 expected={'currentRevision':'field-v4','portablePckSha256':PCK,'portableByMode':{'menu':92,'duel':92,'heroes':92},
  'modelSha256':{key:row[1] for key,row in MODELS.items()},'galleryChecks':127,'roamingChecks':84,'roamingMatchups':12,
  'packedRuntimeChecks':19,'gpuSkinReadbacks':10,'weightedHeroes':['lubu'],'measuredContactDirections':['zhangfei->lubu'],
  'cadenceInputChecks':489,'cadenceInputMatches':48,'cadenceRevision':'r3',
  'normalBattleChecks':18,'normalBattleAgents':5184,'normalBattleOrders':2,'normalBattleGpuReadbacks':6,
  'packedPortraits':16,'catalogSha256':CATALOG,'pairedCurveSha256':CURVE,'groundingChecks':0,'approachChecks':0,
  'pairedOpponentChecks':0,'pairedArmChecks':0,'genericArmChecks':0}
 if any(data.get(key)!=value for key,value in expected.items()):raise ValueError('Public field snapshot differs from reviewed scope')

def update_cards(cards):
 rows={row['id']:row for row in cards}
 def update(key,title,summary,evidence,next_step):
  rows[key].update(title=title,summary=summary,evidence=evidence,next=next_step)
 update('duel_mode','전장에서 이동하는 독립 일기토','기본 일기토를 이동·회전하는 교전 프레임과 각자의 지지 발을 사용하는 전장 모드로 연결했습니다.',
  '메뉴·일기토·감상 각92개 독립 실행 검사. 작업 폴더 밖의 실제 PCK 두 경기19개에서 자연 승부·이동·가중 복부 명중·재대결을 확인했습니다. M05 완료 영상과 현재 제작 중인 개선을 구분합니다.',
  '공방 연결 리듬과 다른 공격 방향의 실제 무기 충돌 확장')
 update('hero_models','여포의 가중 허리·망토와 장수 모델','여포 field/v1f의 골반·복부·망토가 따로 움직이고, 관우·장비·마초는 arm_v3를 유지합니다.',
  '실제 패키지 GPU에서 복부·망토 스킨을10번 읽어 CPU 좌표와 비교했습니다. 이전 모델의 팔 정점 검사 수치를 이 새 모델의 검증으로 재사용하지 않습니다. 얼굴·갑주·옷과 원화의 미술 격차는 남습니다.',
  '전체 장수의 의상 스키닝과 모델·재질 품질 개선')
 update('hero_animation','준비·회수 자세의 연속적인 공방','v5 곡선으로 중복된 준비 정지를 제거하고 상체가 회수를 이어가게 했습니다. 무기 접촉 구간·발·HP/승패 시계는 유지합니다.',
  '새 실행본의12조합84개·입력48경기489개 검사. 같은 여포 공격 회수의120Hz 진단에서 최대 각속도9.0→7.3rad/s이며 첫 후보24rad/s는 수정했습니다. 이 한 경기 진단을 자연스러움 점수로 사용하지 않습니다. 기본/후보 GPU 비교와 편집용 Blender312프레임 재로딩을 별도 검수했습니다.',
  '상체 버팀과 갑주 경직 개선, 다양한 반격·거리 회복 저작')
 update('paired_motion','이동 공방의 접지와 변형된 몸통 타격','화면·시뮬레이션·무기 조회에 같은 이동 프레임을 쓰고, 갑옷과 실제 스킨 복부를 타격 표면에 포함했습니다.',
  '현재 표면 타격은 장비→여포 한 방향입니다. 실제 패키지의 두 배치에서 변형 복부에 각5번 명중했고 자연 종료를 확인했습니다. 12개 이동 조합 검사는 모든 방향의 정밀 충돌 검증이 아닙니다.',
  '다른 장수·반대 공격의 표면 접촉, 연속 충돌과 체중 반응 확장')
 rows['hero_gallery']['evidence']='현재 모델 감상127개 회귀 검사. 원화와 같은 플레이 모델을 읽으며 변형된 허리·망토의 실제 좌표로 구도를 맞춥니다. 시각 품질이나 원작 동등성 판정은 아닙니다.'
 rows['officer_portraits']['evidence']='서로 다른16개 원화를 검수했으며 새 패키지에서16장 모두1024×1536 텍스처로 읽었습니다. 원화16명과 모델·플레이4명은 구분합니다. 새 네 원화는 보존된 이전 마일스톤 영상 이후 추가됐습니다.'
 return cards
