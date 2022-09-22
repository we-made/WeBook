from django import forms

from webook.arrangement.models import Arrangement, Person


class AddPlannersForm (forms.Form):
    arrangement_slug = forms.SlugField()
    planner_ids = forms.CharField()

    def is_person_eligible(self, person):
        return True

    def save(self):
        arrangement = Arrangement.objects.get(slug=self.cleaned_data["arrangement_slug"])
        print(self.cleaned_data.items())
        planner_pks = self.cleaned_data["planner_ids"].split(",")
        for planner_pk in planner_pks:
            planner_person = Person.objects.get(id=planner_pk)
            
            if self.is_person_eligible(planner_person) is False:
                raise "Person attempted to be added to arrangement is ineligible"

            arrangement.planners.add(planner_person)
        
        arrangement.save()


class AddPlannerForm (forms.Form):
    arrangement_id = forms.IntegerField()
    planner_person_id = forms.IntegerField()

    def is_person_eligible(self, person):
        return True

    def save(self):
        arrangement = Arrangement.objects.get(id=self.cleaned_data["arrangement_id"])
        planner_person = Person.objects.get(id=self.cleaned_data["planner_person_id"]) 
        
        if self.is_person_eligible(planner_person) is False:
            raise "Person attempted to be added to arrangement is ineligible"

        arrangement.planners.add(planner_person)
        arrangement.save()


class RemovePlannerForm (forms.Form):
    arrangement_id = forms.IntegerField()
    planner_person_id = forms.IntegerField()

    def save(self):
        arrangement = Arrangement.objects.get(id=self.cleaned_data["arrangement_id"])
        planner_person = Person.objects.get(id=self.cleaned_data["planner_person_id"]) 
        arrangement.planners.remove(planner_person)
        arrangement.save()


class RemovePlannersForm (forms.Form):
    arrangement_slug = forms.SlugField()
    planner_ids = forms.CharField()

    def save(self):
        arrangement = Arrangement.objects.get(slug=self.cleaned_data["arrangement_slug"])
        planner_pks = self.cleaned_data["planner_ids"].split(",")

        for planner_pk in planner_pks:
            planner_person = Person.objects.get(id=planner_pk)
            arrangement.planners.remove(planner_person)
        
        arrangement.save()


class PromotePlannerToMainForm (forms.Form):
    arrangement_id = forms.IntegerField()
    promotee = forms.IntegerField()

    def promote(self):
        arrangement = Arrangement.objects.get(id=self.cleaned_data["arrangement_id"]) 
        
        promotee_person = arrangement.planners.get(id=self.cleaned_data["promotee"])

        # remove the promotee from the "common" planners group
        arrangement.planners.remove(promotee_person)

        # demote the old main to a normal "planner" status
        arrangement.planners.add(arrangement.responsible)

        arrangement.responsible = promotee_person
        arrangement.save()
