import json
import tempfile
import unittest
from pathlib import Path

import duel_gallery


class PlayableGalleryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.public=self.root/'project_monitor'
        (self.public/'portraits').mkdir(parents=True)
        def write(name,data):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(data),encoding='utf-8')
            return path
        self.write=write
        self.asset=self.root/'assets/portraits/duel/ganning.png'
        self.asset.parent.mkdir(parents=True)
        import base64
        self.asset.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jWZkAAAAASUVORK5CYII='))
        rows=[dict(id=k,name_han='甘寧',name_ko='감녕',alias=None,portrait=None,duel_playable=False,model_status='not_created') for k in ['one','two']]
        self.base=write('assets/data/officers.json',{'count':2,'officers':rows})
        self.proof=write('artifacts/qinglong/review/jinfan/verified.json',{'matrix':{'officers':1},'controls':{'officers':[{'id':'ganning','name':'감녕','portrait':'duel'}]}})
        write('docs/milestones.json',{'milestones':[{'id':'M05.1','jinfan_ganning':{'proof_sha256':duel_gallery.digest(self.proof),'verified_utc':'2026-11-19T23:22:32+00:00'}}]})
        write('docs/DUEL_ROSTER_STAGE1.json',{'verified_in_duel':1,'officers':[{'reference_id':'two','name_han':'甘寧','name_ko':'감녕','feature':'금범','status':'verified_in_duel','romance_chapter':38}]})

    def test_only_verified_reference_is_promoted(self):
        old=self.base.read_bytes()
        catalog,images=duel_gallery.prepare(self.root)
        first,second=catalog['officers']
        self.assertFalse(first['duel_playable'])
        self.assertTrue(second['duel_playable'])
        self.assertEqual(second['romance_chapter'],38)
        self.assertEqual((catalog['duel_playable'],catalog['illustrated']),(1,1))
        duel_gallery.sync(self.public,catalog,images)
        duel_gallery.sync(self.public,catalog,images,check=True)
        self.assertEqual(self.base.read_bytes(),old)
        (self.public/'portraits/ganning.png').write_bytes(b'changed')
        with self.assertRaises(ValueError):duel_gallery.sync(self.public,catalog,images,check=True)

    def test_changed_game_evidence_is_rejected(self):
        self.proof.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'release proof'):duel_gallery.prepare(self.root)

