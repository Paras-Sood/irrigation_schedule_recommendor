import json
from urllib import request
from rest_framework.response import Response
from rest_framework.views import APIView
import math

class HelloView(APIView):
    def get(self,request):
        return Response("Hello World!")

