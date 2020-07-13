from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Crop, SensorEntry

# Create your views here.


def index(request):

    context = {
        'num_crops': Crop.objects.all().count(),
        'crops': Crop.objects.all(),
        'ec': SensorEntry.objects.last().ec,
        'temp': SensorEntry.objects.last().temp,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


def sensorentry_new(request) -> HttpResponse:
    example_hint = "GET structure:\n/new?sensor_id=0000&ec=####&temp=####"

    incoming = request.GET
    if len(incoming) != 0:
        try:
            reply = HttpResponse(
                incoming["sensor_id"]+", "+incoming["ec"]+", "+incoming["temp"])

            e = SensorEntry(
                sensor_id=incoming["sensor_id"], ec=incoming["ec"], temp=incoming["temp"])
            e.save()

            return reply
        except:
            return HttpResponse("Wrong format, "+example_hint)

    return HttpResponse(example_hint)


def raw_data(request):
    context = {}
    all_data = SensorEntry.objects.all()
    context["all"] = all_data
    print(SensorEntry.objects.order_by('datetime_created').last().temp)
    return render(request, "raw_data.html", context)


def latest_sensor_val(request):

    if request.is_ajax and request.method == "GET":
        return JsonResponse({
            'datetime_created': SensorEntry.objects.order_by('datetime_created').last().datetime_created,
            'temp': SensorEntry.objects.order_by('datetime_created').last().temp,
            'ec': SensorEntry.objects.order_by('datetime_created').last().ec
        }, status=200)

    return JsonResponse({}, status=400)
