from redis_nest import Nest
import unittest

class TestRedisNest(unittest.TestCase):
    BASE_KEY = 'nest-test'
    def setUp(self):
        self.nest = Nest(TestRedisNest.BASE_KEY)
        self.assertEqual(TestRedisNest.BASE_KEY, self.nest)
        
    def test_exists(self):
        self.nest.set(1)
        self.assertTrue(self.nest.exists())
        
    def _verify_delete(self, nest_obj):
        nest_obj.delete()
        self.assertFalse(nest_obj.exists())
        
        
    def test_getset(self):
        self.assertTrue(self.nest['getset'].set(1))
        self.assertEqual(self.nest['getset'].get(), '1')
        self._verify_delete(self.nest['getset'])
        
    def test_nested(self):
        nested = self.nest['nested']['subkey']['subsubkey']
        self.assertEqual(nested, '%s:nested:subkey:subsubkey' % TestRedisNest.BASE_KEY)
        nested.set(2345)
        self.assertEqual(nested.get(), '2345')
        self._verify_delete(nested)

    def test_as_is_methods(self):
        # TO BE COMPLETED...
        pass
        
if __name__ == "__main__" :
    unittest.main()