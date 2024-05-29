from rest_framework import serializers

from news.models import News, NewsCategory


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["thumbnail"] = instance.thumbnail_url

        return rep

    class Meta:
        model = News
        fields = "__all__"
