from __future__ import unicode_literals

from django.db import models
from django.contrib import messages
from django.contrib.postgres import fields as postgres
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator



import re
import bcrypt
import math


class UserManager(models.Manager):
    def register(self, userData):
        errors = []
        if len(userData["email"]) < 4:
            errors.append("Email must be at least 4 characters")
        if len(userData["username"]) < 4:
            errors.append("Username must be at least 2 characters")
        if len(userData["password"]) < 8:
            errors.append("Invalid Password")
        if userData["password"] != userData["passconf"]:
            errors.append("Password must match confirmation")
        user = None
        if len(errors) == 0:
            user = User(email=userData["email"], username=userData["username"],
                        password=bcrypt.hashpw(userData["password"].encode(),
                                               bcrypt.gensalt()))
            user.save()
            for company in trading.models.Company.objects.all():
                trading.models.Stock(company=company, owner=user, shares=10).save()
        return (user, errors)

    def tryLogin(self, name, password):
        try:
            user = self.get(username=name)
            if bcrypt.hashpw(password.encode(),
                             user.password.encode()) != user.password:
                return "Incorrect password"
            return user
        except ObjectDoesNotExist:
            return "User is not registered"


class User(models.Model):
    email = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, blank=True, null=True)
    cash = models.DecimalField(max_digits=12, decimal_places=2,
                               default=10000)
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Confidence(models.Model):
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE)
    level = models.FloatField(validators = [MinValueValidator(0.0), MaxValueValidator(1.0)])
    def add(self, amount):
        if not 0.0<=amount<1.0:
            raise ValueError("Attempted to add confidence outside of bounds:"+str(amount))
        self.level = self.level + amount - (self.level*amount);
        self.save();
    def subtract(self, amount):
        if not 0.0<=amount<1.0:
            raise ValueError("Attempted to subtract confidence outside of bounds:"+str(amount))
        self.level = self.level * (1-amount);
        self.save();
    class Meta:
        abstract = True;

class IndustryConfidence(Confidence):
    industry = models.ForeignKey("trading.Industry", on_delete=models.CASCADE)

class CompanyConfidence(Confidence):
    company = models.ForeignKey("trading.Company", on_delete=models.CASCADE)

class Bot(User):
    weights = postgres.ArrayField(models.FloatField(), size=3)
    static_weight = models.FloatField()
    function = models.IntegerField()
    def listIndustryConfidences(self, company):
        industry_objs = company.industries.all()
        industry_list = set()
        industry_list.add(1)
        for industry_obj in industry_objs:
            industry_list.add(industry_obj.id)
            industry_list.add(industry_obj.parent_id)
        industry_list.remove(1)
        return IndustryConfidence.objects.filter(bot=self).filter(industry_id__in=industry_list)
    def getIndustryConfidences(self, company):
        industry_confidences = self.listIndustryConfidences(company)
        temp_sum = 0
        for industry_confidence in industry_confidences:
            temp_sum += math.log((1/industry_confidence.level)-1)
        result = 1/(1+math.exp(temp_sum))
        return result
    def addIndustryConfidences(self, company, amount):
        industry_confidences = self.listIndustryConfidences(company)
        for industry_confidence in industry_confidences:
            industry_confidence.add(amount)
    def subtractIndustryConfidences(self, company, amount):
        industry_confidences = self.listIndustryConfidences(company)
        for industry_confidence in industry_confidences:
            industry_confidence.subtract(amount)
