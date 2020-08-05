from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import SensorEntry, Schedule, TrayState
from datetime import date, timedelta, datetime
import joblib

# Create your views here.


def index(request):
    # Render the HTML template app.html with the data in the context variable
    return render(request, 'app.html')


# API for arduino sensors to send data
def sensorentry_new(request) -> HttpResponse:
    example_hint = "GET structure:\n/new?sensor_id=0000&ec=####&temp=###"

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


# Tray state is a single entry in the database, modifies accordingly to the colors of the 4 trays
def tray_state(request) -> HttpResponse:
    if request.is_ajax and request.method == "GET":
        incoming = request.GET
        cycle1 = ['red',	'orange',	'green'	, 'blue']
        cycle2 = ['orange',	'red',	'green'	, 'blue']
        cycle3 = ['orange',	'red',	'blue'	, 'green']
        cycle4 = ['red',	'orange',	'blue'	, 'green']
        cycles = [cycle1, cycle2, cycle3, cycle4]
        initial_entries = 23

        if incoming.get('new') or TrayState.objects.count() == 0:
            TrayState.objects.all().delete
            e = TrayState(date=date.today(),
                            tray1='blank', tray2='blank', tray3='blank', tray4='blank')
            e.save()

        elif TrayState.objects.count() == 0:
            return JsonResponse({'Response': 'Tray state database empty'}, status=400)


        oldest_entry = TrayState.objects.first()
        return JsonResponse({
            'date': oldest_entry.date,
            'tray1': oldest_entry.tray1,
            'tray2': oldest_entry.tray2,
            'tray3': oldest_entry.tray3,
            'tray4': oldest_entry.tray4
        }, status=200)


# include 'growth_period' in data to generate new schedule, else returns schedule for all weeks
def scheduler(request) -> HttpResponse:
    if request.is_ajax and request.method == "GET":
        incoming = request.GET
        if (Schedule.objects.count() > 1):
            step = int(Schedule.objects.all()[1:2].get(
            ).week) - int(Schedule.objects.all()[:1].get().week)
        seq = ['red', 'blue', 'orange', 'green']
        times = 24


        # next harvest date
        if (incoming.get('next_harvest')):
            next_harvest_date = Schedule.objects.exclude(to_harvest='blank')[0].date
            return JsonResponse({'date': next_harvest_date.strftime("%d %b")}, status=200)


        # restart schedule
        if (incoming.get('growth_period') or incoming.get('restart')):
            Schedule.objects.all().delete()
            if incoming.get('growth_period'): step = round(int(incoming.get('growth_period'))/4)
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

            #reset tray state
            t = TrayState.objects.first()
            t.tray1 = 'blank'
            t.tray2 = 'blank'
            t.tray3 = 'blank'
            t.tray4 = 'blank'
            t.save()

            return JsonResponse({'Response': 'Restarted schedule'}, status=200)



        # populate database again when it gets low
        if Schedule.objects.count() <= 12:
            for i in range(16):
                e = Schedule(week=Schedule.objects.last().week+((i+1)*step), date=Schedule.objects.last().date +
                             timedelta((i+1)*step*7), to_plant=seq[i % 4], to_transfer=seq[(i+2) % 4], to_harvest=seq[i % 4])
                e.save()


        # user completes a task
        if (incoming.get('completed')):
            e = Schedule.objects.first()
            t = TrayState.objects.first()
            if (incoming.get('completed') == 'plant'):
                color = e.to_plant
                e.to_plant = 'blank'
                # only tray 2 and 3 can have new seeds
                if (color == 'red' or color == 'orange'): 
                    t.tray2 = color
                elif (color == 'blue' or color == 'green'):
                    t.tray3 = color
                t.save()

            elif (incoming.get('completed') == 'harvest'):
                color = e.to_harvest
                e.to_harvest = 'blank'
                if (color == 'red' or color == 'orange'): 
                    t.tray1 = 'blank'
                elif (color == 'blue' or color == 'green'):
                    t.tray4 = 'blank'
                t.save()
                
            elif (incoming.get('completed') == 'transfer'):
                color = e.to_transfer
                e.to_transfer = 'blank'
                if (color == 'red' or color == 'orange'): 
                    t.tray2 = 'blank'
                    t.tray1 = color
                elif (color == 'blue' or color == 'green'):
                    t.tray3 = 'blank'
                    t.tray4 = color
                t.save()

            if (e.to_plant == 'blank' and e.to_harvest == 'blank' and e.to_transfer == 'blank'):
                e.delete()
            else:
                e.save()

            return JsonResponse({'response': 'completed task ' + incoming.get('completed')}, status=200)



        # return all weeks tasks, default
        data = Schedule.objects.all()[:4].values()
        return JsonResponse({'data': list(data)}, safe=False)


# raw data route url for check sensor values history
def raw_data(request):
    context = {}
    all_data = SensorEntry.objects.all()
    context["all"] = all_data
    return render(request, "raw_data.html", context)


# returns latest sansor value, or calculation of nutrient sol
def latest_sensor_val(request):

    if request.is_ajax and request.method == "GET":

        datetime_created = SensorEntry.objects.last().datetime_created
        temp = SensorEntry.objects.order_by('datetime_created').last().temp
        ec = SensorEntry.objects.order_by('datetime_created').last().ec

        path = "./metta_app/models/nutr_model"  # relative path for dev
        # path = "/home/pi/Desktop/metta_server/metta_app/models/nutr_model" # path for rpi


        # nutrient vol calculator (machine learning)
        incoming = request.GET
        if incoming.get('calc'):
            target_conc = incoming.get('target_conc')
            water_vol = incoming.get('water_vol')
            nutr_vol = joblib.load(path).predict(
                [float(temp), float(target_conc), float(water_vol)])
            print(target_conc, water_vol, nutr_vol)
            return JsonResponse({'nutr_vol': nutr_vol}, status=200)

        # trim database
        if SensorEntry.objects.count() > 100000: # about a week of entries
            max_date = SensorEntry.objects[10000] # index 0 is oldest entry, delete 0 - 9999th entry
            old = SensorEntry.objects.filter(datetime_created__lt = max_date)
            old.delete()

        # realtime display
        return JsonResponse({
            'datetime_created': datetime_created,
            'temp': temp,
            'ec': ec
        }, status=200)

    return JsonResponse({}, status=400)
