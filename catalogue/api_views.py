import csv
import io

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT

from catalogue.models import MedicationSKU
from catalogue.serializers import MedicationSKUReadSerializer, MedicationSKUCreateSerializer, \
    MedicationSKUUpdateSerializer, MedicationSKUDeleteSerializer, BulkUploadSerializer
from utils.authorization_utils import RequestAuthentication
from utils.encryption_utils import decrypt_request_body
from utils.exception_handler import api_safe_execution
from utils.pagination import CustomPagination


class MedicationCreateReadAPIView(RequestAuthentication, ListCreateAPIView):
    queryset = MedicationSKU.objects.all()
    serializer_class =  MedicationSKUReadSerializer
    pagination_class = CustomPagination

    @api_safe_execution
    def get(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


    @api_safe_execution
    def post(self, request, *args, **kwargs):
        status, data = decrypt_request_body(data=request.data)
        if not status:
            return Response(data=data, status=HTTP_400_BAD_REQUEST)

        serializer = MedicationSKUCreateSerializer(data=data)
        if serializer.is_valid():
            MedicationSKU.objects.create(
                medication_name=serializer.validated_data.get("medication_name"),
                dose=serializer.validated_data.get("dose"),
                presentation=serializer.validated_data.get("presentation"),
                unit=serializer.validated_data.get("unit")
            )
            return Response(status=HTTP_201_CREATED)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)


class MedicationReadUpdateDeleteAPIView(RequestAuthentication, RetrieveUpdateDestroyAPIView):

    @api_safe_execution
    def get(self, request, *args, **kwargs):
        medication = self.request.GET.get("medication_id")
        medication = MedicationSKU.objects.filter(msku_id=medication).first()
        return Response(data=dict(data=MedicationSKUReadSerializer(medication).data), status=HTTP_200_OK)




    @api_safe_execution
    def patch(self, request, *args, **kwargs):
        status, data = decrypt_request_body(data=request.data)
        if not status:
            return Response(data=data, status=HTTP_400_BAD_REQUEST)

        serializer =  MedicationSKUUpdateSerializer(data=data)
        if serializer.is_valid():
            MedicationSKU.objects.filter(msku_id=serializer.validated_data.get("msku_id")).update(**serializer.validated_data)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)


    @api_safe_execution
    def delete(self, request, *args, **kwargs):
        status, data = decrypt_request_body(data=request.data)
        if not status:
            return Response(data=data, status=HTTP_400_BAD_REQUEST)

        serializer =  MedicationSKUDeleteSerializer(data=data)
        if serializer.is_valid():
            MedicationSKU.objects.filter(msku_id=serializer.validated_data.get("msku_id")).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)



class BulkUploadAPIView(RequestAuthentication, CreateAPIView):


    @api_safe_execution
    def post(self, request, *args, **kwargs):
        serializer = BulkUploadSerializer(data=request.data)
        if serializer.is_valid():
            successful_rows = 0
            unsuccessful_rows = 0
            errors = list()

            file = serializer.validated_data.get("file")

            data_set = file.read().decode("utf-8")
            io_string = io.StringIO(data_set)
            csv_data = list(csv.reader(io_string, delimiter=",", quotechar='"'))

            for index, column in enumerate(csv_data[1:]):
                data = dict(
                    medication_name=column[0],
                    presentation=column[1],
                    dose=column[2],
                    unit=column[3]
                )
                serializer = MedicationSKUCreateSerializer(data=data)
                if serializer.is_valid():
                    MedicationSKU.objects.create(**data)
                    successful_rows += 1
                else:
                    unsuccessful_rows +=1
                    errors.append(
                        dict(
                            row=index,
                            error=serializer.errors
                        )
                    )

            return Response(data=dict(
                successful_rows=successful_rows,
                unsuccessful_rows=unsuccessful_rows,
                errors=errors
            ), status=HTTP_201_CREATED)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)


