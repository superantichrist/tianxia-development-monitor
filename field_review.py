"""Curated evidence for the adopted moving-duel package, with exact review pins."""
import hashlib,json
from pathlib import Path

PCK="b3cce294dd9004f3d00efa1718c82a5662b0239a6cc569ea8d8e815316afb5b5"
CATALOG="37e6dc3f81db2c4c5319cdc5df4e7d8f3085ec5bf273a71f9d2cde494e259c4a"
MODELS={
 "lubu":("assets/models/heroes/field/lubu.glb","d74c3e065720e64d6b69f20f7f117b9c7695cdaa3253739c7d73c685e09fcfd6"),
 "guanyu":("assets/models/heroes/arm_v3/guanyu.glb","53d7d92dfba7d3a40afa2fc41118d5c1233d176d1355329b1a5a64d14af7e708"),
 "zhangfei":("assets/models/heroes/arm_v3/zhangfei.glb","08a14d403c09da4d43bd3794257f043c9d9e9252150c8e57d5ba2a9e01056592"),
 "machao":("assets/models/heroes/arm_v3/machao.glb","73f44e4bfaae268721088d403735b335aa1720e340daabaaa26a9e060ef3e6ec"),
}
REPORTS={
 "gallery":("hero-gallery-integrated-r1.json","6ef0245b71886e600a93ce741e87d1b4d2044d73c6bd60cd893414bc1a527b1a"),
 "pairs":("duel-integrated-all-pairs-r1.json","cdf28f546a045f53d2effef81b1a8f26bdea099dbcf967a673b4dfd1eef946d7"),
 "packed":("duel-integrated-pack-r1.json","b2bad3796e95b2d7308548b34fad77cc970d1c33e5fd2b15977af2f651ca5d63"),
 "gpu":("duel-integrated-pack-gpu-r1.json","9c535f949c78fe753620e0dffb411cfdc7811d1323c3ce5c79a7e215839424ec"),
 "art":("integrated-pack-art-r1.json","20b15224f9e26ec4d5fed76fb88ca874dcc6a6c1f53eeb2fb5b51162f918ec04"),
 "inputs":("duel-integrated-cadence-r1.json","50311a827fe4e84f2458d2414fcfd55c7122def1a1398a75e70806d1dc793a42"),
 "main_battle":("battle-duel-integrated-packed-r1.json","59e3af764f9dd90c9d1e7a2d8c55c599dc843c4b8b37bfd71690b72023a90aaf"),
 "main_gpu":("battle-duel-integrated-packed-gpu-r1.json","8b8978ee7908ff380d1a018f81df2d9420dbee657a68152f3fbe297f2b1b4b4e"),
}
CURVE="8eaa7adafc86b44a925f438aeed53124607c6385aa4174427ba172136f80855c"

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

def read(root):
 def load(name):return json.loads((root/name).read_text(encoding='utf-8-sig'))
 manifest=load('build/Tianxia-next/build-manifest.json')
 if manifest.get('packaged_sha256',{}).get('Tianxia.pck')!=PCK or sha(root/'build/Tianxia-next/Tianxia.pck')!=PCK:
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
  'currentRevision':'field-v3','portablePckSha256':PCK,'portableByMode':portable,'modelSha256':{key:row[1] for key,row in MODELS.items()},
  'modelRevisions':{'lubu':'field/v1f','guanyu':'arm_v3','zhangfei':'arm_v3','machao':'arm_v3'},'pairedCurveRevision':'v4 + measured Zhang/Lu contacts','pairedCurveSha256':CURVE,
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
 expected={'currentRevision':'field-v3','portablePckSha256':PCK,'portableByMode':{'menu':92,'duel':92,'heroes':92},
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
 update('hero_animation','발걸음으로 이어지는 전신 공방','준비·회수의 멈춤을 줄이고, 회피 뒤 지지 발을 회수해 다음 공격으로 연결했습니다.',
  '네 장수12조합84개 검사와 양 배치·4개 표시 FPS의 입력48경기489개 검사를 통과했습니다. 일반 대결 최대 골반 보정11.51cm, 회피 포함17.26cm. 준비·회수 시간을 줄이고 회피 뒤 발을 회수합니다. 자연스러움 완성 판정은 아닙니다.',
  '상체 버팀과 갑주 경직 개선, 다양한 반격·거리 회복 저작')
 update('paired_motion','이동 공방의 접지와 변형된 몸통 타격','화면·시뮬레이션·무기 조회에 같은 이동 프레임을 쓰고, 갑옷과 실제 스킨 복부를 타격 표면에 포함했습니다.',
  '현재 표면 타격은 장비→여포 한 방향입니다. 실제 패키지의 두 배치에서 변형 복부에 각5번 명중했고 자연 종료를 확인했습니다. 12개 이동 조합 검사는 모든 방향의 정밀 충돌 검증이 아닙니다.',
  '다른 장수·반대 공격의 표면 접촉, 연속 충돌과 체중 반응 확장')
 rows['hero_gallery']['evidence']='현재 모델 감상127개 회귀 검사. 원화와 같은 플레이 모델을 읽으며 변형된 허리·망토의 실제 좌표로 구도를 맞춥니다. 시각 품질이나 원작 동등성 판정은 아닙니다.'
 rows['officer_portraits']['evidence']='서로 다른16개 원화를 검수했으며 새 패키지에서16장 모두1024×1536 텍스처로 읽었습니다. 원화16명과 모델·플레이4명은 구분합니다. 새 네 원화는 보존된 이전 마일스톤 영상 이후 추가됐습니다.'
 return cards
