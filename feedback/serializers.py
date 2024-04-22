from rest_framework import serializers

from . import models


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feedback
        exclude = ["deleted", "author"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = instance.image.url if instance.image else None

        return rep

    def create(self, validated_data):
        return models.Feedback.objects.create(
            **validated_data, author=self.context["user"]
        )
