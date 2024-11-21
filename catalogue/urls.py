from django.urls import path

from .api_views import MedicationCreateReadAPIView, MedicationReadUpdateDeleteAPIView, BulkUploadAPIView

app_name = "catalogue"
urlpatterns = [
    path("medication-sku/", MedicationCreateReadAPIView.as_view(), name="medication_sku_create_read"),
    path("medication_sku_update_delete_read/", MedicationReadUpdateDeleteAPIView.as_view(), name="medication_sku_update_delete_read"),
    path("medication-bulk-upload/", BulkUploadAPIView.as_view(), name="bulk_upload")

]