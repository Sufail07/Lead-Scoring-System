from .serializers import LeadResultsSerializer, LeadSerializer, OfferSerializer
from .models import Offer, Lead
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, serializers
import csv
import requests
from io import StringIO
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.http import HttpResponse
from .helpers import get_rule_points, get_ai_response
# Create your views here.


BASE_URL = 'https://lead-scoring-system-4eiv.onrender.com/api'


'''
Endpoint to create Offers. @extend_schema is used for drf-spectacular documentation, as it is not supported for function based views off the go.
'''

@extend_schema(
    summary="Create a New Offer",
    description="Creates a new offer with specified details.",
    request=OfferSerializer,
    responses={
        201: OfferSerializer,
        400: OpenApiResponse(description="Bad Request - Invalid data provided."),
    },
    tags=['Offers']
)
@api_view(['POST'])
def offer(request):
    serializer = OfferSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadLeadsSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    failed = serializers.CharField()
    created_leads = LeadSerializer(many=True)
    failed_leads = serializers.ListField(child=serializers.DictField())


'''
Endpoint to upload leads for a specific offer. It accepts an integer -> offer_id, through which it recognizes the offer to which the leads are uploaded to.
'''

@extend_schema(
    summary="Upload Leads via CSV",
    description="Uploads a CSV file of leads to associate with a specific offer.",
    parameters=[
        OpenApiParameter(name='offer_id', description='ID of the offer to associate leads with', required=True, type=int, location=OpenApiParameter.PATH),
    ],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary'
                }
            },
            'required': ['file']
        }
    },
    responses={
        200: UploadLeadsSuccessResponseSerializer,
        400: OpenApiResponse(description="Bad Request - The uploaded file is not a valid CSV."),
        404: OpenApiResponse(description="Not Found - The specified offer_id does not exist."),
    },
    tags=['Leads']
)
@api_view(['POST'])
def upload_leads(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if not offer:
        return Response({'error': 'Provide a valid offer_id'}, status=status.HTTP_404_NOT_FOUND)
    file = request.FILES['file']

    if not file:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not file.name.endswith('.csv'):
        return Response({'error': 'Only CSV files are  supported'}, status=status.HTTP_400_BAD_REQUEST)
    
    decoded_file = file.read().decode('utf-8')
    io_string = StringIO(decoded_file)
    reader = csv.DictReader(io_string)

    created_leads, failed_leads = [], []
    for row in reader:
        row_data = {**row, "offer": offer.id}

        serializer = LeadSerializer(data=row_data)
        if serializer.is_valid():
            serializer.save()
            created_leads.append(serializer.data)
        else:
            # if only "name" is missing, fail; otherwise model handles defaults
            failed_leads.append({"row": row, "errors": serializer.errors})

    return Response({
        'message': f'{len(created_leads)} leads uploaded successfully to offer: {offer_id}',
        'failed': f'Failed to upload {len(failed_leads)} leads',
        'created_leads': created_leads,
        'failed_leads': failed_leads})



@extend_schema(
    summary="Score leads associated with an offer",
    description="Triggers the rule-based and AI-powered scoring process for leads for a specific offer. The result is saved to the lead record.",
    parameters=[
        OpenApiParameter(name='offer_id', description='ID of the offer to score', required=True, type=int, location=OpenApiParameter.PATH),
    ],
    request=None,
    responses={
        200: OpenApiResponse(description="Scoring completed successfully."),
        404: OpenApiResponse(description="Not Found - The specified offer_id does not exist."),
        500: OpenApiResponse(description="Internal Server Error during scoring process."),
    },
    tags=['Offers']
)
@api_view(['POST'])
def get_leads_score(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    try:
        # In case all the leads are scored for the given offer, the function stops.
        leads_to_score = offer.leads.filter(score__isnull=True, intent_label__isnull=True, reasoning__isnull=True)
        if not leads_to_score.exists():
            return Response({'message': 'No leads left to score on this offer'}, status=status.HTTP_400_BAD_REQUEST)
        
        for lead in leads_to_score:
            
            # for each lead we find the rule layer point out of 50 and the AI layer point out of 50. The AI layer also returns the AI verdict on the Intent and the reasoning for the verdict. 
            rule_layer_points = get_rule_points(lead)
            ai_layer_response = get_ai_response(lead)
            
            if 'error' in ai_layer_response:
                return Response(ai_layer_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # The calculated score out of 100, is saved to the corresponding object, along with the intent and reasoning.
            final_score = rule_layer_points + ai_layer_response['AI_score']
            lead.score = final_score
            lead.intent_label = ai_layer_response['Intent']
            lead.reasoning = ai_layer_response['Reason']
            lead.save()
            
        return Response({'message': f'Scoring completed on the offer with id: {offer_id}'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
Endpoint to fetch the result of scored leads from the database.
'''
@extend_schema(
    summary="View Scored Leads",
    description="Retrieves a list of all leads that have been successfully scored.",
    responses=LeadResultsSerializer(many=True),
    tags=['Results']
)
@api_view(['GET'])
def result(request):
    evaluated_leads = Lead.objects.exclude(intent_label='').exclude(reasoning='')
    serializer = LeadResultsSerializer(evaluated_leads, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="View All Leads",
    description="Retrieves a list of all leads in the system, regardless of their scoring status.",
    responses=LeadResultsSerializer(many=True),
    tags=['Leads']
)
@api_view(['GET'])
def view_leads(request):
    all_leads = Lead.objects.all()
    serializer = LeadResultsSerializer(all_leads, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    summary="View All Offers",
    description="Retrieves a list of all offers in the system.",
    responses=OfferSerializer(many=True),
    tags=['Offers']
)
@api_view(['GET'])
def view_offers(request):
    all_offers = Offer.objects.all()
    serializer = OfferSerializer(all_offers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




'''
Endpoint to export the evaluated leads data as CSV. It sends a request to /result endpoint, builds a CSV file for the returned data, and provides a link for the user to download the CSV file.
'''
@extend_schema(
    summary="Export scored results as CSV",
    description="Fetches the scored results and downloads as CSV file",
    responses=OfferSerializer(many=True),
    tags=['Offers']
)
@api_view(['GET'])
def export_result(request):
    url = f'{BASE_URL}/result/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        leads_data = response.json()

    except requests.exceptions.RequestException as e:
        return Response({'message': f'Error fetching data: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # In case there exists no data in the /result endpoint.
    if not leads_data:
        return Response({'message': 'No leads data available for download'}, status=status.HTTP_404_NOT_FOUND)
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="leads_scores.csv"'},
    )   
    
    writer = csv.DictWriter(response, fieldnames=leads_data[0].keys())
    writer.writeheader()
    writer.writerows(leads_data)
    return response
    

    