from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Crop, SensorEntry, Schedule, TrayState
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


def tray_state(request) -> HttpResponse:
    if request.is_ajax and request.method == "GET":
        incoming = request.GET
        cycle1 = ['red',	'orange',	'green'	, 'blue']
        cycle2 = ['orange',	'red',	'green'	, 'blue']
        cycle3 = ['orange',	'red',	'blue'	, 'green']
        cycle4 = ['red',	'orange',	'blue'	, 'green']
        cycles = [cycle1, cycle2, cycle3, cycle4]
        initial_entries = 23

        if incoming.get('task_done'):
            TrayState.objects.first().delete()

        if incoming.get('new') and TrayState.objects.count() == 0:
            step = int(Schedule.objects.all()[1:2].get(
            ).week) - int(Schedule.objects.all()[:1].get().week)
            if TrayState.objects.count() == 0:
                e = TrayState(date=date.today(), week=0,
                              tray1='blank', tray2='blank', tray3='blank', tray4='blank')
                e.save()
                e = TrayState(date=date.today(), week=0,
                              tray1='blank', tray2='red', tray3='blank', tray4='blank')
                e.save()
                e = TrayState(date=date.today()+timedelta(7*step), week=1,
                              tray1='blank', tray2='red', tray3='blue', tray4='blank')
                e.save()
                e = TrayState(date=date.today()+timedelta(14*step), week=2,
                              tray1='red', tray2='orange', tray3='blue', tray4='blank')
                e.save()

                for i in range(3, initial_entries):
                    e = TrayState(date=date.today()+timedelta(i*step*7),
                                  week=i,
                                  tray1=cycles[(i-3) % 4][0],
                                  tray2=cycles[(i-3) % 4][1],
                                  tray3=cycles[(i-3) % 4][2],
                                  tray4=cycles[(i-3) % 4][3])
                    e.save()

        elif TrayState.objects.count() == 0:
            return JsonResponse({'Response': 'Tray state database empty'}, status=400)

        # populate database again when it gets low
        elif TrayState.objects.count() <= 12:
            for i in range(16):
                e = TrayState(date=TrayState.objects.last().date+timedelta((i+1)*step*7),
                              tray1=cycles[i % 4][0],
                              tray2=cycles[i % 4][1],
                              tray3=cycles[i % 4][2],
                              tray4=cycles[i % 4][3])
                e.save()

        oldest_entry = TrayState.objects.first()
        return JsonResponse({
            'date': oldest_entry.date,
            'tray1': oldest_entry.tray1,
            'tray2': oldest_entry.tray2,
            'tray3': oldest_entry.tray3,
            'tray4': oldest_entry.tray4
        }, status=200)


# include growth_period in data to generate new schedule, else returns schedule for all weeks
def scheduler(request) -> HttpResponse:
    if request.is_ajax and request.method == "GET":
        incoming = request.GET
        if (Schedule.objects.count() != 0):
            step = int(Schedule.objects.all()[1:2].get(
            ).week) - int(Schedule.objects.all()[:1].get().week)
        seq = ['red', 'blue', 'orange', 'green']
        times = 24

        # return all weeks tasks
        if not (incoming.get('growth_period') or incoming.get('completed')):
            data = Schedule.objects.all().values()
            return JsonResponse({'data': list(data)}, safe=False)

        # restart schedule
        if (incoming.get('growth_period') and Schedule.objects.count() == 0):
            step = int(int(incoming.get('growth_period'))/4)
            for i in range(0, 2*step, step):
                e = Schedule(week=i, date=date.today(
                )+timedelta(i*7), to_plant=seq[int((i/step) % 4)], to_transfer='blank', to_harvest='blank')
                e.save()
            for i in range(2*step, 4*step, step):
                e = Schedule(week=i, date=date.today()+timedelta(i*7), to_plant=seq[int(
                    (i/step) % 4)], to_transfer=seq[int(((i/step)+2) % 4)], to_harvest='blank')
                e.save()
            for i in range(4*step, times*step, step):
                e = Schedule(week=i, date=date.today()+timedelta(i*7), to_plant=seq[int(
                    (i/step) % 4)], to_transfer=seq[int(((i/step)+2) % 4)], to_harvest=seq[int((i/step) % 4)])
                e.save()
            return JsonResponse({'Response': 'Restarted schedule'}, status=200)

        # populate database again when it gets low
        if Schedule.objects.count() <= 12:
            for i in range(16):
                e = Schedule(week=Schedule.objects.last().week+((i+1)*step), date=Schedule.objects.last().date +
                             timedelta((i+1)*step*7), to_plant=seq[i % 4], to_transfer=seq[(i+2) % 4], to_harvest=seq[i % 4])
                e.save()

        if (incoming.get('completed')):
            e = Schedule.objects.first()
            if (incoming.get('completed') == 'plant'):
                e.to_plant = 'blank'
            if (incoming.get('completed') == 'harvest'):
                e.to_harvest = 'blank'
            if (incoming.get('completed') == 'transfer'):
                e.to_transfer = 'blank'

            if (e.to_plant == 'blank' and e.to_harvest == 'blank' and e.to_transfer == 'blank'):
                e.delete()
            else:
                e.save()

            return JsonResponse({'to_harvest': Schedule.objects.first().to_harvest, 'to_transfer': Schedule.objects.first().to_transfer, 'to_plant': Schedule.objects.first().to_plant}, status=200)


def raw_data(request):
    context = {}
    all_data = SensorEntry.objects.all()
    context["all"] = all_data
    print(SensorEntry.objects.order_by('datetime_created').last().temp)
    return render(request, "raw_data.html", context)


def latest_sensor_val(request):

    if request.is_ajax and request.method == "GET":

        datetime_created = SensorEntry.objects.order_by(
            'datetime_created').last().datetime_created
        temp = SensorEntry.objects.order_by('datetime_created').last().temp
        ec = SensorEntry.objects.order_by('datetime_created').last().ec

        path = "./metta_app/models/nutr_model"  # relative path for dev
        # path = "/home/pi/Desktop/metta_server/metta_app/models/nutr_model" # path for rpi

        incoming = request.GET
        if incoming.get('calc'):
            target_conc = incoming.get('target_conc')
            water_vol = incoming.get('water_vol')
            nutr_vol = joblib.load(path).predict(
                [float(temp), float(target_conc), float(water_vol)])
            print(target_conc, water_vol, nutr_vol)
            return JsonResponse({'nutr_vol': nutr_vol}, status=200)

        return JsonResponse({
            'datetime_created': datetime_created,
            'temp': temp,
            'ec': ec
        }, status=200)

    return JsonResponse({}, status=400)
