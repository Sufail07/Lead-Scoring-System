from rest_framework import serializers
from .models import Offer, Lead

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'name', 'value_props', 'ideal_use_cases']
        read_only_fields = ['created_at']
        
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'offer', 'name', 'role', 'company', 'industry', 'location', 'linkedin_bio']

class LeadResultsSerializer(serializers.ModelSerializer):
    offer_name = serializers.StringRelatedField(source='offer')
    class Meta:
        model = Lead
        fields = ['id', 'offer_name', 'name', 'role', 'company', 'industry', 'location', 'intent_label', 'score', 'reasoning']
        