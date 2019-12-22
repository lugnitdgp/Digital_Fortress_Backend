from django.db import models

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
    answer = models.CharField(max_length=200)

    def __str__(self):
        return str(self.round_number)

    def transformAnswer(self):
        answer_array = self.answer.split(",")
        for index, answer in enumerate(answer_array):
            temp = answer.lower()
            temp = temp.strip()
            answer_array[index] = temp
        return answer_array

    def checkAnswer(self, answer):
        answer = answer.lower().strip()
        answers = self.transformAnswer()
        for a in answers:
            if a == answer:
                return True
        return False


class Clue(models.Model):
    question = models.CharField(max_length=750)
    answer = models.CharField(max_length=200)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True)
    round = models.ForeignKey('Round', on_delete=models.CASCADE)

    def __str__(self):
        return self.question

    def transformAnswer(self):
        answer_array = self.answer.split(",")
        for index, answer in enumerate(answer_array):
            temp = answer.lower()
            temp = temp.strip()
            answer_array[index] = temp
        return answer_array

    def checkAnswer(self, answer):
        answer = answer.lower().strip()
        answers = self.transformAnswer()
        for a in answers:
            if a == answer:
                return True
        return False

    def getPosition(self):
        lat = self.location.lat
        long = self.location.long
        return [lat, long]


class Player(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=254)
    imageLink = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    roundNo = models.IntegerField(default=1)
    current_hints = models.CharField(max_length=200, blank=True)
    submit_time = models.DateTimeField(auto_now_add=True)

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
