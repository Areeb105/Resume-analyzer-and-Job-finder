from django.http import JsonResponse
from django.shortcuts import redirect

def index(request):
    return JsonResponse({"message": "Job Portal API is running. Please access the frontend via index.html."})
