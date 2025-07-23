from .models import ContactForm, FAQ, InternForm, InvestorForm, MentorForm, SuggestionForm,TeamMember, WorkingTeamMember
from rest_framework import serializers

class ConatctFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactForm
        exclude = ('id',)

class SuggestionFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuggestionForm
        exclude = ('id',)

class MentorFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = MentorForm
        exclude = ('id',)


class InternFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = InternForm
        exclude = ('id',)


class InvestorFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestorForm
        exclude = ('id',)        


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        exclude = ('id', 'status')
        # fields = '__all__'


class TeamMeberSerializer(serializers.ModelSerializer):
    dp = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = ('name', 'title', 'dp')

    def get_dp(self, obj):
        request = self.context.get('request')
        dp_url = obj.dp.url
        return request.build_absolute_uri(dp_url)

class WorkingTeamMeberSerializer(serializers.ModelSerializer):
    dp = serializers.SerializerMethodField()

    class Meta:
        model = WorkingTeamMember
        fields = ('name', 'feedback', 'dp')

    def get_dp(self, obj):
        request = self.context.get('request')
        dp_url = obj.dp.url
        return request.build_absolute_uri(dp_url)





