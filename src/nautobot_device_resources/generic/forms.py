from django.db import transaction
from django.db.models import Model
from django.forms import ModelForm


class MixedFormMixin(ModelForm):
    """Edit form to replace core form with another enhanced by custom form, supports both create and edit"""

    child_model = Model
    child_foreign_link = ""
    child_foreign_field = ""
    child_form = ModelForm

    @classmethod
    def child_fields(cls):
        # pylint: disable-next=protected-access
        return cls.child_form._meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" in kwargs:
            if hasattr(kwargs["instance"], self.child_foreign_link):
                kwargs["instance"] = getattr(kwargs["instance"], self.child_foreign_link)
            else:
                kwargs["instance"] = self.child_model(device=kwargs["instance"])
        self.child_form_instance = self.child_form(*args, **kwargs)
        self.fields.update(self.child_form_instance.fields)
        self.initial.update(self.child_form_instance.initial)

    def is_valid(self) -> bool:
        is_valid = True
        if not self.child_form_instance.is_valid():
            is_valid = False
        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        if not super().is_valid():
            is_valid = False
        self.errors.update(self.child_form_instance.errors)
        return is_valid


class MixedCSVFormMixin(MixedFormMixin):
    """Support import for MixedFormMixin"""

    def save(self, commit=True):
        with transaction.atomic():
            parent = super().save()
            child_fields = {child_field: self.cleaned_data[child_field] for child_field in self.child_fields()}
            self.child_model.objects.create(
                **{self.child_foreign_field: parent},
                **child_fields,
            )
            return parent
