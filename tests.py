from unittest import TestCase
import simplejson
from json_diff import JsonDiff, make_json_diff

class ImplementationTests(TestCase):

    def setUp(self):
        self.json_str='[{"a": {"b": 1, "c": "t"}, "d": [{"e": "u", "f": 2},{"e": "v", "f": 3}]}]'
        self.json = simplejson.loads(self.json_str)
        self.json_diff = make_json_diff(self.json)
        self.counter = 0

    def test_create_json_diff(self):
        self.assertTrue( isinstance(self.json_diff, JsonDiff) )

    def test_iterate_as_dict(self):
        for i in self.json_diff:
            self.counter += 1
        self.assertEquals( len(self.json_diff), self.counter )

    def test_sub_objects_are_diffs(self, diff_obj=None):
        if not diff_obj:
            diff_obj = self.json_diff
        for i,v in enumerate(diff_obj):
            if not isinstance(v, basestring) and not isinstance(v, int) and not isinstance(v, float):
                self.assertTrue( isinstance(v, JsonDiff) )
                self.test_sub_objects_are_diffs(v)

    def test_list_objects_are_diffs(self):
        obj = '[{"a":[1,2,3]}]'
        obj_json = simplejson.loads(obj)
        diff = make_json_diff(obj_json)
        self.assertTrue( isinstance(diff[0]['a'], JsonDiff) )


