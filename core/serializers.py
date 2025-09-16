from rest_framework import serializers
from .models import Offer, Lead

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'name', 'value_props', 'ideal_use_cases']
        read_only_fields = ['created_at']
        
class LeadSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=False, allow_blank=True, default="")
    company = serializers.CharField(required=False, allow_blank=True, default="")
    industry = serializers.CharField(required=False, allow_blank=True, default="")
    location = serializers.CharField(required=False, allow_blank=True, default="")
    linkedin_bio = serializers.CharField(required=False, allow_blank=True, default="")
    score = serializers.IntegerField(required=False, min_value=0, max_value=100, allow_null=True)
    intent_label = serializers.ChoiceField(choices=Lead.intent_choices, required=False, allow_null=True)
    reasoning = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Lead
        fields = '__all__'

class LeadResultsSerializer(serializers.ModelSerializer):
    offer_name = serializers.StringRelatedField(source='offer')
    class Meta:
        model = Lead
        fields = ['id', 'offer_name', 'name', 'role', 'company', 'industry', 'location', 'intent_label', 'score', 'reasoning']
        