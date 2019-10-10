from google.oauth2 import id_token
from django.core.exceptions import ObjectDoesNotExist
from google.auth.transport import requests
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, authentication, permissions
from knox.models import AuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse, JsonResponse
from .models import Round, Player, Clue
import datetime
import requests as r
import time
import json
import csv
import os
from django.utils import timezone
import urllib
from .serializers import CreateUserSerializer, RoundSerializer, PlayerSerializer
from decouple import config


# Create your views here.


def LeaderBoard(request):
    if request.GET.get("password") == config('DOWNLOAD', cast=str):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="leaderboards.csv"'
        writer = csv.writer(response)
        for player in Player.objects.order_by("-score", "submit_time"):
            writer.writerow([player.name, player.email])
        return response
    else:
        return HttpResponse("You are not authorized to see this page!")


def verifyGoogleToken(token):
    CLIENT_ID = config('CLIENT_ID', cast=str)
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        return {
            "email": idinfo['email'],
            "username": idinfo['name'],
            "image": idinfo['picture'],
            "status": 200
        }
    except ValueError:
        return {"status": 404, "message": "Your Token has expired. Please login/register again!"}


def verifyFacebookToken(accesstoken, expiration_time, userID):
    if(int(expiration_time) < int(time.time())):
        return {"status": 404}
    else:
        url = "https://graph.facebook.com/{}".format(userID)
        parameters = {
            'fields': 'name,email,picture',
            'access_token': accesstoken
        }
        idInfo = r.get(url=url, params=parameters).json()
        return {
            "email": idInfo['email'],
            "username": idInfo['name'],
            "image": idInfo['picture']['data']['url'],
            'status': 200
        }


def centrePoint(roundNo):
    clues = Clue.objects.filter(round=roundNo)
    x = 0.0
    y = 0.0
    count = 0
    for clue in clues:
        pos = clue.getPosition()
        x += pos[0]
        y += pos[1]
        count += 1
    centre = []
    centre.append(x/count)
    centre.append(y/count)
    return centre


def verifyUser(email):
    try:
        Player.objects.get(email=email)
        return True
    except ObjectDoesNotExist:
        return False


@permission_classes([AllowAny, ])
class leaderboard(generics.GenericAPIView):
    def get(self, request, format=None):
        p = Player.objects.order_by("-score", "submit_time")
        current_rank = 1
        players_array = []
        for player in p:
            player.rank = current_rank
            players_array.append({
                "name": player.name,
                "rank": player.rank,
                "score": player.score,
                "image": player.imageLink,
            })
            current_rank += 1
        return Response({"standings": players_array, "safe": False})


@permission_classes([AllowAny, ])
class Register(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get('type') == '1':
            res = verifyGoogleToken(request.data.get('accesstoken'))
        else:
            res = verifyFacebookToken(request.data.get('accesstoken'), request.data.get('expiration_time'), request.data.get(
                'userID'))
        if res['status'] == 404:
            return Response({
                "status": 404,
                "message": "Token expired."
            })
        else:
            if verifyUser(res['email']) == False:
                serializer = self.get_serializer(data=res)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                player = Player.objects.create(
                    name=res['username'], email=res['email'], imageLink=res['image'])
                return Response({
                    "user": serializer.data,
                    "token": AuthToken.objects.create(user)[1],
                    "status": 200
                })
            else:
                return Response({"message": "Email Already Registered!", "status": 402})


@permission_classes([AllowAny, ])
class Login(generics.GenericAPIView):
    serializer_class = PlayerSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get('type') == '1':
            res = verifyGoogleToken(request.data.get('accesstoken'))
        else:
            res = verifyFacebookToken(request.data.get('accesstoken'), request.data.get('expiration_time'), request.data.get(
                'userID'))
        if res['status'] == 404:
            return Response({
                "status": 404,
                "message": "Token expired."
            })
        else:
            if verifyUser(res['email']) == True:
                print(res)
                user = User.objects.get(username=res['username'])
                player = Player.objects.get(name=res['username'])
                serializer = self.get_serializer(player)
                return Response({
                    "user": serializer.data,
                    "token": AuthToken.objects.create(user)[1],
                    "status": 200
                })
            else:
                return Response({
                    "message": "Email is not registered!",
                    "status": 401
                })


@permission_classes([IsAuthenticated, ])
class getRound(APIView):
    def get(self, request, format=None):
        player = Player.objects.get(name=request.user.username)
        try:
            curr_round = Round.objects.get(round_number=player.roundNo)
            serializer = RoundSerializer(curr_round)
            centre = centrePoint(curr_round)
            return Response({"question": serializer.data, "centre": centre, "status": 200, "detail": 1})
        except:
            if Round.DoesNotExist:
                return Response({"message": "Finished!", "status": 404, "detail": 1})
        return Response({"data": None})


@permission_classes([IsAuthenticated])
class checkRound(APIView):
    def post(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(name=request.user.username)
            round = Round.objects.get(
                round_number=(player.roundNo))

            if round.checkAnswer(request.data.get("answer")):
                player.score += 10
                player.roundNo += 1
                player.submit_time = timezone.now()
                player.save()
                return Response({"status": 200, "detail": 1})
            else:
                return Response({"status": 500, "detail": 1})
        except (Player.DoesNotExist, Round.DoesNotExist):
            return Response({"status": 404, "detail": 1})


@permission_classes([IsAuthenticated])
class getClue(APIView):
    def get(self, request, format=None):
        try:
            player = Player.objects.get(name=request.user.username)
            round = Round.objects.get(round_number=(player.roundNo))
            response = []
            clues = Clue.objects.filter(round=round)
            for clue in clues:
                if player.checkClue(clue.id):
                    response.append({
                        "id": clue.id,
                        "question": clue.question,
                        "position": clue.getPosition(),
                        "solved": True
                    })
                else:
                    response.append(
                        {"id": clue.id, "question": clue.question, "solved": False}
                    )
            return Response({"clues": response, "status": 200, "detail": 1})
        except (Player.DoesNotExist, Round.DoesNotExist):
            return Response({"status": 404, "detail": 1})


@permission_classes([IsAuthenticated])
class putClue(APIView):
    def post(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(name=request.user.username)
            try:
                clue = Clue.objects.get(pk=int(request.data.get("clue_id")))
                if clue.checkAnswer(request.data.get("answer")):
                    player.putClues(clue.pk)
                    player.save()
                    return Response({"status": 200, "position": clue.getPosition(), "detail": 1})
                else:
                    return Response({"status": 500, "detail": 1})
            except (ValueError, Clue.DoesNotExist):
                return Response({"status": 403, "message": "Wrong Clue ID."})
        except Player.DoesNotExist:
            return Response({"data": None, "status": 404})

