from webook.utils.meta_utils.section_manifest import SUBTITLE_MODE


class CrumbMixin:
    
    def get_context_data(self, **kwargs):
        """
            Override get_context_data to inject our crumb variables directly into the context,
            allowing crumb_base (and others) to use this without polluting our other templates.
            Requires that you set a few attributes;
            
            In the section dict:
            SECTION_TITLE --> The title of the section, for instance Location
            SECTION_ICON  --> The icon of the section. Use fontawesome. Just give a class, base templates should handle rest.

            Other attributes:
            SECTION_SUBTITLE --> 
        """
        context =  super().get_context_data(**kwargs)

        entity_name = ""

        if self.view_meta.subtitle_mode == SUBTITLE_MODE.TITLE_AS_SUBTITLE:
            section_subtitle = self.view_meta.subtitle
            current_crumb_title = self.view_meta.current_crumb_title
        elif self.view_meta.subtitle_mode == SUBTITLE_MODE.ENTITY_NAME_AS_SUBTITLE:
            entity_name = getattr(self.get_object(), self.view_meta.entity_name_attribute)
            section_subtitle = entity_name
            current_crumb_title = entity_name

        section_subtitle = self.view_meta.subtitle_prefix + section_subtitle
        current_crumb_title = self.view_meta.subtitle_prefix + current_crumb_title

        current_crumb_icon = self.current_crumb_icon if hasattr(self, 'current_crumb_icon') else None

        context["SECTION_TITLE"] = self.section.section_title
        context["SECTION_CRUMB_TITLE"] = self.section.section_title
        context["SECTION_CRUMB_ICON"] = self.section.section_icon
        context["SECTION_CRUMB_URL"] = self.section.section_crumb_url()
        context["SECTION_SUBTITLE"] = section_subtitle
        context["RETURN_URL"] = self.section.section_crumb_url()
        context["CURRENT_CRUMB_TITLE"] = current_crumb_title
        context["CURRENT_CRUMB_ICON"] = current_crumb_icon
        context["ENTITY_NAME"] = entity_name

        return context