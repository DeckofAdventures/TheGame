from automation.utils.dict_manip import filter_dict_by_key, flatten_embedded

basic_dict = {"a": 1}
embed_dict = {"a": {"b": 1}, "c": {"b": 2}, "d": {"b": 3}}


def test_flatted_embedded():
    assert flatten_embedded(basic_dict) == basic_dict
    assert flatten_embedded(embed_dict) == {"a_b": "1", "c_b": "2", "d_b": "3"}


def test_null_filter_dict():
    assert filter_dict_by_key(basic_dict) == basic_dict
    assert filter_dict_by_key(embed_dict, key_filter="b", key_options=[1, 2]) == {
        "a": {"b": 1},
        "c": {"b": 2},
    }
