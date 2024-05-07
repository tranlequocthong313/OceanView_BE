from rest_framework import serializers

from guide.models import Guide, GuideCategory


class GuideCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideCategory
        fields = "__all__"


class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = "__all__"
