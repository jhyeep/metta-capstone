from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Crop, SensorEntry, Schedule
from datetime import date, timedelta
import joblib

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
    

def scheduler(request) -> HttpResponse:
    if request.is_ajax and request.method == "GET":
        incoming = request.GET
        step = int(int(incoming.get('growth_weeks'))/4)
        seq = ['red','blue','orange','green']
        if Schedule.objects.count() == 0:
            for i in range(0, 2*step, step):
                e = Schedule(week=i, date=date.today()+timedelta(i*7), to_plant=seq[int((i/step)%4)], to_transfer='blank', to_harvest='blank')
                e.save()
            for i in range(2*step, 4*step, step):
                e = Schedule(week=i, date=date.today()+timedelta(i*7), to_plant=seq[int((i/step)%4)], to_transfer=seq[int(((i/step)+2)%4)], to_harvest='blank')
                e.save()
            for i in range(4*step, 8*step, step):
                e = Schedule(week=i, date=date.today()+timedelta(i*7), to_plant=seq[int((i/step)%4)], to_transfer=seq[int(((i/step)+2)%4)], to_harvest=seq[int((i/step)%4)])
                e.save()
            return JsonResponse({}, status=200)
        # else: 
        #     latest_week = Schedule.objects.last().week
        #     for i in range(latest_week, latest_week+8*step, step):
        #         e = Schedule(week=i, date=date.today()+timedelta(i*7), to_plant=seq[int((i/step)%4)], to_transfer=seq[int(((i/step)+2)%4)], to_harvest=seq[int((i/step)%4)])
        #         e.save()


def raw_data(request):
    context = {}
    all_data = SensorEntry.objects.all()
    context["all"] = all_data
    print(SensorEntry.objects.order_by('datetime_created').last().temp)
    return render(request, "raw_data.html", context)


def latest_sensor_val(request):

    if request.is_ajax and request.method == "GET":

        datetime_created = SensorEntry.objects.order_by('datetime_created').last().datetime_created
        temp = SensorEntry.objects.order_by('datetime_created').last().temp
        ec = SensorEntry.objects.order_by('datetime_created').last().ec

        path = "./metta_app/models/nutr_model" # relative path for dev
        # path = "/home/pi/Desktop/metta_server/metta_app/models/nutr_model" # path for rpi

        if request.GET.get('calc'):
            target_conc = request.GET.get('target_conc')
            water_vol = request.GET.get('water_vol')
            nutr_vol = joblib.load(path).predict([float(temp),float(target_conc),float(water_vol)])
            print(target_conc, water_vol, nutr_vol)
            return JsonResponse({'nutr_vol': nutr_vol}, status=200)

        return JsonResponse({
            'datetime_created': datetime_created,
            'temp': temp,
            'ec': ec
        }, status=200)


    return JsonResponse({}, status=400)




