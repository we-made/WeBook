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
        if (self.entity_name_attribute):
            obj = self.get_object()
            entity_name = obj.__getattribute__(self.entity_name_attribute)
            section_subtitle = f"{self.section_subtitle_prefix} {entity_name}" 

        context["SECTION_TITLE"] = self.section["SECTION_TITLE"]
        context["SECTION_CRUMB_TITLE"] = self.section["SECTION_TITLE"]
        context["SECTION_CRUMB_ICON"] = self.section["SECTION_ICON"]
        context["SECTION_CRUMB_URL"] = self.section["SECTION_CRUMB_URL"]()
        context["SECTION_SUBTITLE"] = section_subtitle
        context["RETURN_URL"] = self.section["SECTION_CRUMB_URL"]()
        context["CURRENT_CRUMB_TITLE"] = entity_name
        context["ENTITY_NAME"] = entity_name

        return context