"""Expand the published name index using a verified playable selection screen."""
import hashlib
import json
import re
import shutil
import struct
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(root, base=None):
    catalog=base if base is not None else read(root/'assets/data/officers.json')
    ledger=read(root/'docs/milestones.json')
    parent=next((v for v in ledger['milestones'] if v['id']=='M05.1'),{})
    editions=[('peicheng_xiahoudun','peicheng'),('hefei_zhangliao','hefei'),('fancheng_pangde','fancheng'),('jinfan_ganning','jinfan')]
    latest=next(((parent[k],folder) for k,folder in editions if k in parent),None)
    if latest is None:return catalog,{}
    release,revision=latest
    proof_path=root/'artifacts/qinglong/review'/revision/'verified.json'
    if digest(proof_path)!=release['proof_sha256']:
        raise ValueError('The playable officer index requires the verified release proof')
    proof=read(proof_path)
    source=read(root/'docs/DUEL_ROSTER_STAGE1.json')
    confirmed={r['reference_id']:r for r in source['officers'] if r['status']=='verified_in_duel'}
    cards=proof['controls']['officers']
    by_name={r['name']:r for r in cards}
    if len(confirmed)!=source['verified_in_duel'] or len(cards)!=len(by_name) or len(cards)!=proof['matrix']['officers']:
        raise ValueError('Selection screen count or unique identity mismatch')
    rows={r['id']:r for r in catalog['officers']}
    art={}
    for i,(ref,registered) in enumerate(confirmed.items()):
        row=rows[ref]
        card=by_name[registered['name_ko']]
        if row['name_han']!=registered['name_han'] or row['name_ko']!=card['name']:
            raise ValueError('Officer reference differs from selected character')
        slug=card['id'];group=card['portrait']
        if not re.fullmatch(r'[a-z0-9]+',slug) or group not in ('romance_v1','romance_v2','duel'):
            raise ValueError('Unexpected portrait name or collection')
        runtime=f'assets/portraits/{group}/{slug}.png'
        src=root/runtime
        header=src.read_bytes()[:24]
        if header[:8]!=b'\x89PNG\r\n\x1a\n' or header[12:16]!=b'IHDR':
            raise ValueError('Invalid runtime portrait')
        width,height=struct.unpack('>II',header[16:24])
        destination=f'portraits/{slug}.png'
        image={'runtime_path':runtime,'public_path':destination,'width':width,'height':height,'sha256':digest(src)}
        if row['portrait'] and row['portrait']!=image:
            raise ValueError('Existing original portrait was reassigned')
        if row['portrait'] is None:
            row['production_priority']=17+i
            row['art_direction']=registered['feature']
        row.update(alias=slug,portrait=image,illustration_status='original_generated',
                   roster_status='duel_verified',model_status='verified_free_duel',duel_playable=True)
        chapter=registered.get('romance_chapter')
        if chapter is not None:
            if type(chapter) is not int or not 1<=chapter<=120:raise ValueError('Invalid novel chapter')
            row.update(literature_classification='romance_text_attested',romance_chapter=chapter)
        art[destination]=src
    if set(by_name)!={r['name_ko'] for r in confirmed.values()}:
        raise ValueError('Verified reference names differ from the playable menu')
    catalog['illustrated']=sum(bool(r['portrait']) for r in rows.values())
    catalog['duel_playable']=sum(r['duel_playable'] for r in rows.values())
    catalog['gallery_revision']=revision
    update=parent.get('zhangfei_performance',{})
    catalog['generated_utc']=max(release['verified_utc'],update.get('verified_utc',''))
    return catalog,art


def sync(folder,catalog,images,check=False):
    if not images:return
    output=folder/'officers.json'
    payload=json.dumps(catalog,ensure_ascii=False,indent=2)+'\n'
    if check and (not output.is_file() or output.read_text(encoding='utf-8')!=payload):
        raise ValueError('Public officer index differs from the playable selection')
    for row in catalog['officers']:
        image=row.get('portrait')
        if image and image['public_path'] not in images:
            path=folder/image['public_path']
            if not path.is_file() or digest(path)!=image['sha256']:
                raise ValueError('Missing or modified previously published portrait')
    for rel,src in images.items():
        to=folder/rel
        if to.is_file():
            if digest(to)!=digest(src):raise ValueError('Published original differs: '+rel)
        elif check:raise ValueError('Missing public original: '+rel)
        else:shutil.copyfile(src,to)
    if not check and (not output.is_file() or output.read_text(encoding='utf-8')!=payload):
        output.write_text(payload,encoding='utf-8')

