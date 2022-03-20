from django.http import HttpResponse
import json, math, jwt, requests
from urllib import request
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import User, SampleSensorData
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from irrigation_schedule_recommendor import settings
from rest_framework import status
from backend.api.serializers import UserSerializer, RegisterSerializer

KC_TAB=[0,0.3,1.15,0.25]
HEIGHT=[0.15,0.25,0.5,0.3]

def jwt_decoder(encoded_token):
    return jwt.decode(
        encoded_token, settings.SIGNING_KEY, algorithms=["HS256"]
    )

class UserInfoView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request):
        payload = jwt_decoder(self.request.headers["Authorization"].split()[1])
        user = self.get_object(payload["user_id"])
        serializer = UserSerializer(user)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class HelloView(APIView):
    permission_classes = [
        AllowAny,
    ]
    def get(self,request):
        message="<html><body>Hello World!</body></html>"
        return HttpResponse(message)


def calculate_kc(kc_tab,u2,rh,h):
    kc_tab=float(kc_tab)
    u2=float(u2)
    rh=float(rh)
    h=float(h)
    return (kc_tab+(0.04*(u2-2) - 0.004*(rh-45)*pow(h/3,3)))

def calculate_delta(T_mean):
    denom=T_mean+237.3
    return (2503.0584*math.exp((17.27*T_mean)/denom)/pow(denom,2))

def calculate_u2(u,h):
    num=u*4.87
    denom=math.log(67.8*h - 5.42)
    return num/denom

def calculate_gamma(P):
    return 0.000665*P

def calculate_es(T):
    es = 0.6108 * math.exp(17.27 * T / (T + 237.3))
    return es

def calculate_ea(RH,es):
    ea=float(RH / 100) * es
    return ea

def calculate_eto(delta,Rn,gamma,T,es,ea,u2):
    delta=float(delta)
    Rn=float(Rn)
    gamma=float(gamma)
    T=float(T)
    es=float(es)
    ea=float(ea)
    u2=float(u2)
    num=(0.408*delta*Rn) + (gamma*(900/(T+273))*u2*(es-ea))
    denom=delta+gamma*(1+0.34*u2)
    return num/denom

def calculate_Pe(P):
    return (0.8*P - 25)

def irrigation_water_needed(lat,long,crop,crop_age):
    sensordata=SampleSensorData.objects.first()
    url=f"http://api.weatherapi.com/v1/forecast.json?key={settings.WEATHER_API_KEY}&q={lat},{long}&daya=1"
    weather_data=requests.get(url)
    weather_data=json.loads(weather_data.content)
    current_data=weather_data['current']
    day_data=weather_data['forecast']['forecastday'][0]['day']
    mxT=day_data['maxtemp_c']
    mnT=day_data['mintemp_c']
    T_mean=(mxT-mnT)/2
    u=current_data['wind_kph']
    u*=5/18 # converting kph to mps
    u2=calculate_u2(u,10) # converting u10 to u2
    Rn=sensordata.short_wave_irradiation
    # Rn=15
    delta=calculate_delta(T_mean)
    pressure=current_data['pressure_mb']
    pressure/=10 # Converting millibar to kPa
    gamma=calculate_gamma(pressure)
    es=calculate_es(T_mean)
    Rh=sensordata.relative_humidity
    # Rh=20
    ea=calculate_ea(Rh,es)
    eto=calculate_eto(delta,Rn,gamma,T_mean,es,ea,u2)

    kctab=KC_TAB[crop_age]
    h=HEIGHT[crop_age]
    kc=calculate_kc(kctab,u2,Rh,h)
    
    etc=eto*kc
    url=f"http://api.weatherapi.com/v1/forecast.json?key={settings.WEATHER_API_KEY}&q={lat},{long}&daya=30"
    weather_data30=json.loads(requests.get(url).content)
    total_precip_mm=0
    i=0
    for precip in weather_data30['forecast']['forecastday']:
        total_precip_mm+=precip['day']['totalprecip_mm']
    total_precip_mm*=30
    print("TP = ",total_precip_mm)
    total_precip_mm=max(total_precip_mm,27)
    pe=calculate_Pe(total_precip_mm)
    print("PE = ",pe)
    irrigation_water_needed=etc-pe
    print(etc)
    return max(irrigation_water_needed,0)

class SensorData(APIView):
    permission_classes = [
        AllowAny,
    ]
    def post(self,request):
        body=request.POST
        lat=int(body['lat'])
        long=int(body['long'])
        crop=body['crop']
        crop_age=int(body['crop_age'])
        field_area=int(body['field_area'])
        field_area*=1000
        iwn=irrigation_water_needed(lat,long,crop,crop_age)
        return Response(f"Received Data!  IWN = {iwn} totalWaterneeded={int(field_area*iwn)}")