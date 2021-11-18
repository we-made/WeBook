import pytest 
from webook.calendar_buddy import factory_manager
from webook.calendar_buddy import base
from webook.calendar_buddy.exceptions import FactoryNotFoundException

def simple_fabrication_method (custom_event_standard = None, custom_resource_standard = None) -> base.BaseCalendarContext:
    ui_config = base.UIConfig()
    fabricated_context = base.BaseCalendarContext(ui_config=ui_config)
    fabricated_context.something = "something"
    return fabricated_context

def register_testing_calendarcontext_factory():
    factory = base.BaseCalendarContextFactory()
    factory.fabricate = simple_fabrication_method
    factory_manager.register_context_factory(
        factory=factory,
        context_type=base.CalendarContext.FULLCALENDAR
    )

def simple_hook (ctx):
    ctx.hook_has_been_here = True
    return ctx

def flush_factory_manager():
    factory_manager._CONTEXT_FACTORIES = {}
    factory_manager._FACTORY_HOOKS = list()

class TestFactoryManager:
    def test_register_context_factory (self):
        flush_factory_manager()
        factory = base.BaseCalendarContextFactory()
        context_type = base.CalendarContext.FULLCALENDAR
        factory_manager.register_context_factory(
            factory=factory,
            context_type=context_type
        )
        assert len(factory_manager._CONTEXT_FACTORIES) == 1
        flush_factory_manager()

    def test_fabricate_calendar_context(self):
        flush_factory_manager()
        factory = base.BaseCalendarContextFactory()
        factory.fabricate = simple_fabrication_method
        factory_manager.register_context_factory(
            factory=factory,
            context_type=base.CalendarContext.FULLCALENDAR
        )
        fabricated_context = factory_manager.fabricate_calendar_context(context_type=base.CalendarContext.FULLCALENDAR)

        assert type(fabricated_context) is base.BaseCalendarContext and fabricated_context.__getattribute__("something")
        flush_factory_manager()

    def test_fabricate_calendar_context_on_nonexisting_factory(self):
        flush_factory_manager()
        with pytest.raises(FactoryNotFoundException):
            factory_manager.fabricate_calendar_context(context_type=base.CalendarContext.FULLCALENDAR)
        flush_factory_manager()

    def test_that_hook_is_run_on_fabrication (self):
        flush_factory_manager()
        register_testing_calendarcontext_factory()
        factory_manager.register_fabrication_hook(
            hook=simple_hook,
            context_type=base.CalendarContext.FULLCALENDAR
        )
        fabricated = factory_manager.fabricate_calendar_context(base.CalendarContext.FULLCALENDAR)
        assert fabricated.__getattribute__("hook_has_been_here")
        flush_factory_manager()

    def test_attempt_register_defaults_on_nonexisting_factory(self):
        flush_factory_manager()
        with pytest.raises(FactoryNotFoundException):
            default_dict = dict()
            factory_manager.register_defaults(
                defaults=default_dict,
                context_type=base.CalendarContext.FULLCALENDAR,
                standard_type=factory_manager.StandardType.EVENT
            )

    def test_register_event_defaults(self):
        flush_factory_manager()
        register_testing_calendarcontext_factory()

        event_default_dict = dict()
        event_default_dict["something"] = "something something"

        factory_manager.register_defaults(
            defaults=event_default_dict,
            context_type=base.CalendarContext.FULLCALENDAR,
            standard_type=factory_manager.StandardType.EVENT
        )

        ctx_factory = factory_manager._CONTEXT_FACTORIES[1]
        assert ctx_factory is not None and ctx_factory.event_standard is not None and "something" in ctx_factory.event_standard

    def test_register_resource_defaults(self):
        flush_factory_manager()
        register_testing_calendarcontext_factory()

        resource_default_dict = dict()
        resource_default_dict["something"] = "something something"

        factory_manager.register_defaults(
            defaults=resource_default_dict,
            context_type=base.CalendarContext.FULLCALENDAR,
            standard_type=factory_manager.StandardType.RESOURCE
        )

        ctx_factory = factory_manager._CONTEXT_FACTORIES[1]
        assert ctx_factory is not None and ctx_factory.resource_standard is not None and "something" in ctx_factory.resource_standard
    
    def test_register_uiconfig_defaults(self):
        flush_factory_manager()
        register_testing_calendarcontext_factory()

        uiconfig_default_dict = dict()
        uiconfig_default_dict["something"] = "something something"

        factory_manager.register_defaults(
            defaults=uiconfig_default_dict,
            context_type=base.CalendarContext.FULLCALENDAR,
            standard_type=factory_manager.StandardType.UI_CONFIG
        )

        ctx_factory = factory_manager._CONTEXT_FACTORIES[1]
        assert ctx_factory is not None and ctx_factory.standard_ui_config is not None and "something" in ctx_factory.standard_ui_config