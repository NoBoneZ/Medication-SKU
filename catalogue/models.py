from uuid import uuid4

from django.db import models

from account.models import BaseModel
# Create your models here.


class MedicationSKU(BaseModel):
    medication_name = models.CharField(max_length=255, unique=True)
    msku_id = models.UUIDField(default=uuid4, editable=False, db_index=True, unique=True)
    presentation = models.CharField(max_length=255)
    dose = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ('medication_name', 'presentation', 'dose', 'unit')

    def __str__(self):
        return f"{self.medication_name} - {self.presentation} - {self.dose}{self.unit}"