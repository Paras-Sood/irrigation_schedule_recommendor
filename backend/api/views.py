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
    ea=RH / 100 * es
    return ea

def calculate_eto(delta,Rn,gamma,T,es,ea,u2):
    num=(0.408*delta*Rn) + (gamma*(900/(T+273))*u2*(es-ea))
    denom=delta+gamma*(1+0.34*u2)
    return num/denom

class SensorData(APIView):
    permission_classes = [
        AllowAny,
    ]
    def post(self,request):
        # body=json.loads(request.body)
        body=request.data
        sensordata=SampleSensorData.objects.first()
        lat=body['lat']
        long=body['long']
        url=f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={lat},{long}"
        weather_data=requests.get(url).response
        current_data=weather_data['current']
        day_data=weather_data['forecast']['forecastday'][0]['day']
        mxT=day_data['maxtemp_c']
        mnT=day_data['mintemp_c']
        T_mean=(mxT-mnT)/2
        u=current_data['wind_kph']
        u*=5/18 # converting kph to mps
        u2=calculate_u2(u,10) # converting u10 to u2
        Rn=sensordata.short_wave_irradication
        delta=calculate_delta(T_mean,Rn)
        pressure=current_data['pressure_mb']
        pressure/=10 # Converting millibar to kPa
        gamma=calculate_gamma(pressure)
        es=calculate_es(T_mean)
        Rh=body['Rh']
        ea=calculate_ea(Rh,es)
        eto=calculate_eto(delta,Rn,gamma,T_mean,es,ea,u2)
        return Response(body)