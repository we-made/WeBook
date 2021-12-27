from django.conf.urls import url


class ModelNamingMetaMixin:
    """
        Mixin to help with getting info of entity naming, of the instance, and plurality/singularity forms of entity name.
    """
    instance_name_attribute_name = "name"
    entity_name_plural = "Entity"
    entity_name_singular = "Entities"

    @property
    def resolved_name(self):
        if hasattr(self, self.instance_name_attribute_name):
            return getattr(self, self.instance_name_attribute_name)
        else:
            raise Exception("instance_name_attribute_name not present for this model")