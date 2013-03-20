from unittest import TestCase
import simplejson
from json_diff import AJson, AJsonDiff

class ImplementationTests(TestCase):

    def setUp(self):
        self.json_str='[{"a": {"b": 1, "c": "t"}, "d": [{"e": "u", "f": 2},{"e": "v", "f": 3}]}]'
        self.json = simplejson.loads(self.json_str)
        self.ajson = AJson().get_instance(self.json)
        self.counter = 0

    def test_create_json_diff(self):
        self.assertTrue( isinstance(self.ajson, AJson) )

    def test_iterate_as_dict(self):
        for i in self.ajson:
            self.counter += 1
        self.assertEquals( len(self.ajson), self.counter )

    def test_sub_objects_are_diffs(self, diff_obj=None):
        if not diff_obj:
            diff_obj = self.ajson
        for i,v in enumerate(diff_obj):
            if not isinstance(v, basestring) and not isinstance(v, int) and not isinstance(v, float):
                self.assertTrue( isinstance(v, AJson) )
                self.test_sub_objects_are_diffs(v)

    def test_list_objects_are_diffs(self):
        obj = '[{"a":[1,2,3]}]'
        obj_json = simplejson.loads(obj)
        ajson = AJson().get_instance(obj_json)
        self.assertTrue( isinstance(ajson[0]['a'], AJson) )

    def test_keep_original(self):
        self.ajson[0]['a']['b'] = 0
        self.assertEquals( self.ajson._original[0]['a']['b'], 1 )
        self.assertEquals( self.ajson[0]['a']['b'], 0 )

    def test_get_all_instances(self):
        for i in self.ajson._instances:
            self.assertTrue( isinstance(i, AJson) )
            self.assertTrue( isinstance(i.diff(), AJsonDiff) )
            self.assertTrue( isinstance(i.diff().changed(), set) )



class BasicFunctionalityTests(TestCase):
    def setUp(self):
        self.json_str='[{"a": {"b": 1, "c": "t"}, "d": [{"e": "u", "f": 2},{"e": "v", "f": 3}]}]'
        self.json = simplejson.loads(self.json_str)
        self.ajson = AJson().get_instance(self.json)

    def test_get_diff_instance(self):
        self.assertTrue( isinstance(self.ajson.diff(), AJsonDiff) )

    def test_getting_changes_return_sets(self):
        diff = self.ajson.diff()
        self.assertTrue( isinstance(diff.changed(), set) )
        self.assertTrue( isinstance(diff.unchanged(), set) )
        self.assertTrue( isinstance(diff.removed(), set) )
        self.assertTrue( isinstance(diff.added(), set) )

