from unittest import TestCase
import simplejson
from json_diff import AJsonBase, AJsonDiffBase, AJsonDictDiff, AJsonListDiff, AJsonDict, AJsonList, SuperJson


JSON_STRING_SAMPLE = '[{"a": {"b": 1, "c": "t"}, "d": [{"e": "u", "f": 2},{"e": "v", "f": 3}], "g": {"12":"abcd"}}]'


class ImplementationTests(TestCase):

    def setUp(self):
        json = simplejson.loads(JSON_STRING_SAMPLE)
        superj = AJsonBase()
        self.ajson = superj(json)
        self.counter = 0

    def tearDown(self):
        self.superj = None
        self.json = None
        self.ajson = None

    def test_create_json_diff(self):
        self.assertTrue(isinstance(self.ajson, AJsonBase))

    def test_getting_entry_returns_correct_json_obj(self):
        entry1 = self.ajson[0]
        self.assertTrue(isinstance(self.ajson, AJsonList))
        self.assertTrue(isinstance(entry1, AJsonDict))
        entry2 = entry1['a']
        self.assertTrue(isinstance(entry2, AJsonDict))
        entry3 = entry1['d']
        entry4 = entry3[0]
        self.assertTrue(isinstance(entry4, AJsonDict))

    def test_iterate_list(self):
        for i, entry in enumerate(self.ajson):
            self.assertTrue(entry, self.ajson[i])
            self.counter += 1
        self.assertEquals(len(self.ajson), self.counter)

    def test_iterate_dict(self):
        for k, v in self.ajson[0].items():
            self.assertEquals(v, self.ajson[0][k])
            self.counter += 1
        self.assertEquals(len(self.ajson[0]), self.counter)

    def test_keep_original(self):
        self.ajson[0]['a']['b'] = 2
        self.assertEqual(1, self.ajson[0]['a']._meta['original']['b'])

    def test_assignment_on_dict(self):
        c = self.ajson[0]['a']
        c['b'] = 123
        self.assertEquals(123, c['b'])
        self.ajson[0]['a']['b'] = 456
        self.assertEquals(456, self.ajson[0]['a']['b'])

    def test_get_all_instances(self):
        print "instances at test_get_all_instances: ", self.ajson.get_instances()
        # print self.ajson[0]['a']
        for i in self.ajson.get_instances():
            self.assertTrue(isinstance(i, AJsonBase))
            self.assertTrue(isinstance(i.diff().changed(), set))

    def test_list_return_list_diff(self):
        o = self.ajson[0]['d']
        diff = o.diff()
        self.assertTrue(isinstance(diff, AJsonListDiff))

    def test_dict_return_dict_diff(self):
        obj = self.ajson[0]
        self.assertTrue(isinstance(obj, AJsonDict))
        diff = obj.diff()
        self.assertTrue(isinstance(diff, AJsonDictDiff))


class BasicFunctionalityTests(TestCase):
    def setUp(self):
        self.json = simplejson.loads(JSON_STRING_SAMPLE)
        self.superj = SuperJson()
        self.ajson = self.superj(self.json)

    def test_get_diff_instance(self):
        self.assertTrue(isinstance(self.ajson.diff(), AJsonDiffBase))

    def test_getting_changes_from_list_diffs(self):
        diff = self.ajson[0]['d'].diff()
        self.assertTrue(isinstance(diff.changed(), set))
        self.assertTrue(isinstance(diff.unchanged(), set))
        self.assertTrue(isinstance(diff.removed(), set))
        self.assertTrue(isinstance(diff.added(), set))

    def test_getting_changes_from_dict_diffs(self):
        diff = self.ajson[0].diff()
        self.assertTrue(isinstance(diff.changed(), set))
        self.assertTrue(isinstance(diff.unchanged(), set))
        self.assertTrue(isinstance(diff.removed(), set))
        self.assertTrue(isinstance(diff.added(), set))

    def test_diff_for_changed_value_in_dict(self):
        # a change in nested dict
        self.ajson[0]['a']['b'] = 'c'
        diff = self.ajson[0]['a'].diff()
        self.assertEquals(diff.changed(), set('b'))
        # a change in a dict nested in a list
        self.ajson[0]['d'][0]['e'] = 12
        diff = self.ajson[0]['d'][0].diff()
        self.assertEquals(diff.changed(), set('e'))

    # ******  lists
    # TODO: put in separate class
    # remainder: json_str = '[{"a": {"b": 1, "c": "t"}, "d": [{"e": "u", "f": 2}, {"e": "v", "f": 3}]}]'
    def test_diff_for_changed_value_in_list(self):
        self.ajson[0]['d'][0] = 12
        diff = self.ajson[0]['d'].diff()
        self.assertEquals(diff.changed(), set([0]))
        self.assertEquals(diff.added(), set([]))
        self.assertEquals(diff.removed(), set([]))
        self.assertEquals(diff.unchanged(), set([1]))

        # now change another object
        self.ajson[0]['a']['b'] = {"e": "v", "f": 1}
        diff = self.ajson[0]['a'].diff()
        self.assertEquals(diff.unchanged(), set(['c']))
        self.assertEquals(diff.changed(), set(['b']))
        self.assertEquals(diff.added(), set([]))
        self.assertEquals(diff.removed(), set([]))

    def test_diff_for_added_entry_in_list(self):
        self.ajson[0]['d'].append(12)
        diff = self.ajson[0]['d'].diff()
        self.assertEquals(diff.added(), set([2]))
        self.assertEquals(diff.removed(), set([]))
        self.assertEquals(diff.changed(), set([]))
        self.assertEquals(diff.unchanged(), set([0, 1]))

    def test_diff_for_removed_entry_in_list(self):
        #note: of course, list are re-ordered when removing entries
        del self.ajson[0]['d'][0]
        diff = self.ajson[0]['d'].diff()
        self.assertEquals(diff.removed(), set([1]))
        self.assertEquals(diff.added(), set([]))
        self.assertEquals(diff.changed(), set([0]))
        self.assertEquals(diff.unchanged(), set([]))


class NestedDiffsTests(TestCase):
    # remainder: JSON_STRING_SAMPLE = '[{"a": {"b": 1, "c": "t"}, "d": [{"e": "u", "f": 2},{"e": "v", "f": 3}]}, "g": {12:"abcd"}]'

    def setUp(self):
        self.json = simplejson.loads(JSON_STRING_SAMPLE)
        self.superj = SuperJson()
        self.ajson = self.superj(self.json)

    def test_get_global_diff(self):
        self.ajson[0]['d'][0]['e'] = 'si sisi'
        self.ajson[0]['a']['c'] = 'nonono'
        print self.ajson[0]['d'][0].diff().changed()
        self.ajson[0]['a']['c'] = 'nonono'
        print self.ajson[0]['d'][0].diff().changed()
        print self.ajson[0]['a'].diff().changed()
        self.ajson[0]['g']["12"] = "yes"
        print self.ajson[0]['g'].diff().changed()
        diffs = self.ajson.recursive_diff()

        self.assertEquals(
            diffs.changed(),
            set([(0, 'a', 'c'), (0, 'd', 0, 'e')])
        )