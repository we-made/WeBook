import pytest

import pytest

from webook.utils.calendar_buddy.base import BaseCalendarContextFactory


base_calendar_context_factory = BaseCalendarContextFactory()

class TestBaseCalendarContextFactory: 
    def test_assign_specified_defaults ():
        original_dict = dict()
        original_dict["test1"] = "Test100"

        new_default = dict()
        new_default["test1"] = "Test101"
        new_default["test2"] = "Test200"

        original_dict = base_calendar_context_factory._assign_specified_defaults(
            dict_to_write_with=new_default,
            dict_to_overwrite=original_dict
        )

        assert len(original_dict == 2)
        assert original_dict["test1"] == "Test101"
        assert "test2" in original_dict and original_dict["test2"] == "Test200"
    
    def test_mesh_defaults_on_specified_none():
        base_defaults = dict()
        base_defaults["Test"] = "100"

        specified_defaults = None
        meshed_dicts = base_calendar_context_factory._mesh_defaults(base_defaults, specified_defaults)
        assert meshed_dicts.__hash__() == base_defaults.__hash__()

    def test_fabricate_notimplemented_error():
        try:
            base_calendar_context_factory.fabricate()
        except NotImplementedError:
            assert True

    def test_identify_self_notimplemented_error():
        try:
            base_calendar_context_factory.identify_self()
        except NotImplementedError:
            assert True