from django.db import models
from datetime import datetime
# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    long = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name


class Round(models.Model):
    round_number = models.IntegerField(default=1)
    question = models.CharField(max_length=750)
    audio=models.FileField(upload_to='media/audios',blank=True)
    answer = models.CharField(max_length=200)
    image=models.ImageField(upload_to='media/images',blank=True)

    def __str__(self):
        return str(self.round_number)

    def checkAnswer(self, answer):
        answer = answer.lower().strip()
        answer = answer.replace(" ","")
        answers = self.answer.split(",")
        for a in answers:
            a = a.lower()
            a = a.replace(" ","")
            if a == answer:
                return True
        return False


class Clue(models.Model):
    question = models.CharField(max_length=750)
    audio=models.FileField(upload_to='media/audios',blank=True)
    image=models.ImageField(upload_to='media/images',blank=True)
    answer = models.CharField(max_length=200)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True)
    round = models.ForeignKey('Round', on_delete=models.CASCADE)

    def __str__(self):
        return self.question

    def checkAnswer(self, answer):
        answer = answer.lower().strip()
        answer = answer.replace(" ","")
        answers = self.answer.split(",")
        for a in answers:
            a = a.lower()
            a = a.replace(" ","")
            if a == answer:
                return True
        return False

    def getPosition(self):
        lat = self.location.lat
        long = self.location.long
        return [lat, long]


class Player(models.Model):
    name = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=254)
    imageLink = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    roundNo = models.IntegerField(default=1)
    current_hints = models.CharField(max_length=200, blank=True)
    submit_time = models.DateTimeField(auto_now_add=True)
    isStaff = models.BooleanField(default = 0)

    def __str__(self):
        return self.name

    def getHints(self):
        if self.current_hints == '':
            return []
        else:
            return self.current_hints.split(',')

    def putClues(self, value):
        hints_arr = self.getHints()
        hints_arr.append(value)
        hints_str = [str(val) for val in hints_arr]
        self.current_hints = ','.join(hints_str)

    def checkClue(self, value):
        hints_arr = self.getHints()
        for hint in hints_arr:
            if value == int(hint):
                return 1
        return 0

class duration(models.Model):
    start_time = models.DateTimeField(default=datetime.now)
    end_time = models.DateTimeField(default=datetime.now)

    def __str__(self): 
        return "Duration" 
            