import copy,unittest
import field_review

class FieldScopeTests(unittest.TestCase):
 def evidence(self):
  return {'currentRevision':'field-v4','portablePckSha256':field_review.PCK,'portableByMode':{'menu':92,'duel':92,'heroes':92},
   'modelSha256':{key:row[1] for key,row in field_review.MODELS.items()},'galleryChecks':127,'roamingChecks':84,'roamingMatchups':12,
   'cadenceInputChecks':489,'cadenceInputMatches':48,'cadenceRevision':'r3','normalBattleChecks':18,'normalBattleAgents':5184,'normalBattleOrders':2,'normalBattleGpuReadbacks':6,'packedRuntimeChecks':19,'gpuSkinReadbacks':10,'weightedHeroes':['lubu'],'measuredContactDirections':['zhangfei->lubu'],
   'packedPortraits':16,'catalogSha256':field_review.CATALOG,'pairedCurveSha256':field_review.CURVE,'groundingChecks':0,
   'approachChecks':0,'pairedOpponentChecks':0,'pairedArmChecks':0,'genericArmChecks':0}
 def test_reviewed_field_contract(self):field_review.validate_public(self.evidence())
 def test_source_or_pack_revision_cannot_be_relabelled(self):
  for key in ('portablePckSha256','pairedCurveSha256','catalogSha256','modelSha256'):
   value=self.evidence();value[key]='unreviewed'
   with self.subTest(key=key),self.assertRaises(ValueError):field_review.validate_public(value)
 def test_natural_matches_cannot_become_all_direction_mesh_physics(self):
  value=self.evidence();value['measuredContactDirections']=[a+'->'+b for a in field_review.MODELS for b in field_review.MODELS if a!=b]
  with self.assertRaises(ValueError):field_review.validate_public(value)
 def test_one_weighted_hero_cannot_become_four(self):
  value=self.evidence();value['weightedHeroes']=list(field_review.MODELS)
  with self.assertRaises(ValueError):field_review.validate_public(value)
 def test_input_scope_cannot_be_expanded(self):
  for key,value in (('cadenceInputChecks',999),('cadenceInputMatches',72),('cadenceRevision','unreviewed')):
   evidence=self.evidence();evidence[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):field_review.validate_public(evidence)
 def test_normal_battle_two_orders_cannot_become_all_pairs(self):
  evidence=self.evidence();evidence['normalBattleOrders']=12
  with self.assertRaises(ValueError):field_review.validate_public(evidence)
 def test_old_geometry_counts_cannot_be_reused_for_new_body(self):
  for key,count in (('pairedOpponentChecks',169),('pairedArmChecks',33),('genericArmChecks',22),('groundingChecks',43)):
   value=self.evidence();value[key]=count
   with self.subTest(key=key),self.assertRaises(ValueError):field_review.validate_public(value)
 def test_raw_private_fields_do_not_leave_report_selection(self):
  value=self.evidence();field_review.validate_public(value)
  self.assertFalse(any(key in value for key in ('executable','working_directory','contact_points','private_video_id')))

if __name__=='__main__':unittest.main()
