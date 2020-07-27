from rest_framework import serializers
from caster.models import Caster


class CasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caster
        fields = '__all__'
