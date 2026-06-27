from rest_framework import serializers

from .models import ProcessingJob


class ProcessingJobCreateSerializer(serializers.ModelSerializer):
    options = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = ProcessingJob
        fields = ["id", "job_type", "input_file", "options", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate_input_file(self, value):
        max_mb = 20
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Fayl hajmi {max_mb}MB dan oshmasligi kerak.")
        return value


class ProcessingJobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingJob
        fields = [
            "id", "job_type", "status", "input_file", "result_file",
            "error_message", "options", "created_at", "updated_at",
        ]
