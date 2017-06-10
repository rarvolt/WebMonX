from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Watch, Value


class WatchSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Watch
        fields = ('id', 'name', 'url', 'xpath', 'period', 'next_check', 'notify', 'owner')


class ValueSerializer(serializers.ModelSerializer):
    # watch = serializers.ReadOnlyField(source='watch.id')

    class Meta:
        model = Value
        fields = ('id', 'watch', 'created', 'content')


class UserSerializer(serializers.ModelSerializer):
    watches = serializers.PrimaryKeyRelatedField(many=True, queryset=Watch.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'watches')
