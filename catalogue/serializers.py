from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, FileField
from rest_framework.serializers import ModelSerializer, Serializer

from catalogue.models import MedicationSKU


class MedicationSKUReadSerializer(ModelSerializer):

    class Meta:
        model = MedicationSKU
        fields = ("medication_name", "msku_id", "presentation", "dose", "unit")


class MedicationSKUCreateSerializer(Serializer):
    medication_name = CharField()
    unit = CharField()
    presentation = CharField()
    dose = IntegerField()

    def validate(self, attrs):
        medication_name = attrs.get("medication_name", "").title().strip()
        attrs["medication_name"] = medication_name
        if attrs.get("dose") < 0:
            raise ValidationError("Dose cannot be less than 0", "dose")

        if MedicationSKU.objects.filter(medication_name__iexact=medication_name).exists():
            raise ValidationError("Medication Name already exists", "medication_name")


        if MedicationSKU.objects.filter(**attrs).exists():
            raise ValidationError("Medication with this parameters already exists")

        return attrs



class MedicationSKUUpdateSerializer(Serializer):
    medication_name = CharField()
    unit = CharField()
    presentation = CharField()
    dose = IntegerField()
    msku_id = CharField()

    def validate(self, attrs):
        medication_name = attrs.get("medication_name", "").title().strip()
        attrs["medication_name"] = medication_name

        if attrs.get("dose") < 0:
            raise ValidationError("Dose cannot be less than 0", "dose")

        if MedicationSKU.objects.filter(medication_name__iexact=medication_name).exclude(msku_id=attrs.get("msku_id")).exists():
            raise ValidationError("Medication Name already exists", "medication_name")


        if MedicationSKU.objects.filter(**attrs).exists():
            raise ValidationError("Medication with this parameters already exists, no parameter was changed")

        return attrs



class MedicationSKUDeleteSerializer(Serializer):
    msku_id = CharField()



class BulkUploadSerializer(Serializer):
    file = FileField()

    def validate_file(self, file):
        if not file.name.endswith('.csv'):
            raise serializers.ValidationError('Only CSV files are allowed.')

        if file.content_type not in ['text/csv', 'application/csv']:
            raise serializers.ValidationError('Invalid file type. Ensure it is a CSV file.')
        
        return file