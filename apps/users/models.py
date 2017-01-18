from __future__ import unicode_literals

from django.db import models
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .. import trading

import re
import bcrypt

class UserManager(models.Manager):
    def register(self, userData):
        errors = []
        if len(userData["email"]) < 4:
            errors.append("Name must be at least 2 characters")
        if len(userData["username"]) < 4:
            errors.append("Username must be at least 2 characters")
        if len(userData["password"]) < 8:
            errors.append("Invalid Password")
        if userData["password"] != userData["passconf"]:
            errors.append("Password must match confirmation")
        user = None
        if len(errors) == 0:
            user = User(email=userData["email"], username=userData["username"], password=bcrypt.hashpw(userData["password"].encode(), bcrypt.gensalt()))
            user.save()
            for company in trading.models.Company.objects.all():
                trading.models.Stock(company=company, owner=user, shares=10).save()
        return (user, errors)

    def tryLogin(self, name, password):
        try:
            user = self.get(username=name)
            if bcrypt.hashpw(password.encode(), user.password.encode()) != user.password:
                return "Incorrect password"
            return user
        except ObjectDoesNotExist:
            return "User is not registered"

class User(models.Model):
        email = models.CharField(max_length=255)
        username = models.CharField(max_length=255)
        password = models.CharField(max_length=255)
        cash = models.DecimalField(max_digits=12, decimal_places=2, default=1000000)
        created_at = models.DateTimeField(auto_now_add = True)
        updated_at = models.DateTimeField(auto_now = True)
        objects = UserManager()
