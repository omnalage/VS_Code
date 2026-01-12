from django.shortcuts import render
from django.http import JsonResponse
def employeeView(request):
    emp = {
        'id': 123,
        'name': 'Anil',
        'Sal': 10000
    }
    return JsonResponse(emp)