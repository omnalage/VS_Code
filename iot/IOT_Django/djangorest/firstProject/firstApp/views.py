from django.http import JsonResponse
from firstApp.models import Employee

def employeeView(request):
    data = Employee.objects.all()
    response = {'employees': list(data.values('id', 'name', 'sal'))}
    return JsonResponse(response)
