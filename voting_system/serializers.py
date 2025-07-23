from rest_framework import serializers
from .models import *

class PostVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voters
        exclude = ('id',)

class GetVotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Votes
        fields = ('title', 'yes_count', 'no_count')
 