import unittest
import battle_review

class BattlefieldScopeTests(unittest.TestCase):
 def evidence(self):return {'status':'prototype','productionIntegrated':False,'agents':320,'matches':20,'checks':221,'orderedPairs':12,'gpuInstanceReadbacks':12,'gpuSkinReadbacks':18,'terrainComparisonPoints':256,'measuredContactDirections':['zhangfei->lubu']}
 def test_reviewed_scope(self):battle_review.validate_public(self.evidence())
 def test_prototype_cannot_become_shipped_integration(self):
  data=self.evidence();data['productionIntegrated']=True
  with self.assertRaises(ValueError):battle_review.validate_public(data)
 def test_sampled_fixtures_cannot_become_full_army_or_all_weapon_physics(self):
  for key,value in [('agents',5184),('measuredContactDirections',['all']),('matches',48)]:
   data=self.evidence();data[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):battle_review.validate_public(data)

if __name__=='__main__':unittest.main()
