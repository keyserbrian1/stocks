from __future__ import division

import platform
import sys
import random
import math
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from ....users.models import User, Bot, IndustryConfidence, CompanyConfidence
from ...models import Company, Stock, Industry
from history_functions import functions

from tendo import singleton
me = singleton.SingleInstance()

def gen_value(bias = .5, n=5):
    sum = 0
    for x in range(n):
         if (random.random()<bias):
             sum += random.random()
         else:
             sum -= random.random()
    return sum/(2*n)+.5

def weighted_choice(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

def make_bots():
    for x in range(-1,-31,-1):
        bot = Bot.objects.create(id=x, static_weight = random.random(), weights = [random.random(),random.random(),random.random()], password="Bot", is_bot=True, function=-1)
        bot.function = weighted_choice([functions[f][1] for f in range(len(functions))])
        bot.username = "Bot "+str(-x)+": "+functions[bot.function][0].name
        for industry in Industry.objects.all():
            IndustryConfidence.objects.create(bot=bot, industry=industry, level=random.random())
        for company in Company.objects.all():
            CompanyConfidence.objects.create(bot=bot, company=company, level=random.random())
            Stock.objects.create(owner=bot, company=company, shares=100)
        bot.save()

class Command(BaseCommand):
    help = "Launches the bots, creating them if necessary."

    def handle(self, *args, **options):
        bots = Bot.objects.all()
        companies = list(Company.objects.all())
        if len(bots) == 0:
            make_bots()
            bots = Bot.objects.all().order_by("id")
        while(True):
            for bot in bots:
                target = random.choice(companies);
                (global_confidence, industry_confidence, company_confidence) = (bot.industryconfidence_set.get(industry_id=1).level, bot.getIndustryConfidences(target), bot.companyconfidence_set.get(company_id=target.id).level)
                (global_weight, industry_weight, company_weight) = map(lambda x:x/sum(bot.weights), bot.weights)
                static_confidence = global_confidence * global_weight + industry_confidence * industry_weight + company_confidence * company_weight
                history_confidence = functions[bot.function][0](target)
                confidence = static_confidence * bot.static_weight + history_confidence * (1-bot.static_weight)
                pick1 = random.random()>confidence
                pick2 = random.random()>confidence
                if pick1 and pick2:
                    with connection.cursor() as c:
                        c.execute("select orders.price from trading_order as orders where orders.company_id=%s and orders.open=false order by orders.created_at DESC limit 1",[target.id])
                        current_price = c.fetchall()
                    if not current_price:
                        current_price=100
                    else:
                        current_price=float(current_price[0][0])
                    to_spend = float(bot.cash) * gen_value(bias = confidence)
                    order_price = round(random.gauss(current_price, current_price/10),2)
                    shares = math.ceil(to_spend/order_price)
                    if shares*order_price > bot.cash:
                        shares-=1
                    if shares > 0:
                        print "Buy "+" ".join([str(bot.id), target.symbol, str(int(shares)), str(order_price)])
                        global_obj = bot.industryconfidence_set.get(industry_id=1)
                        global_obj.add(.05)
                        company_obj = bot.companyconfidence_set.get(company_id=target.id)
                        company_obj.add(.05)
                        bot.addIndustryConfidences(target, .05)
                        time.sleep(.1)
                elif (not pick1) and (not pick2):
                    with connection.cursor() as c:
                        c.execute("select orders.price from trading_order as orders where orders.company_id=%s and orders.open=false order by orders.created_at DESC limit 1",[target.id])
                        current_price = c.fetchall()
                    if not current_price:
                        current_price=100
                    else:
                        current_price=float(current_price[0][0])
                    shares = round(Stock.objects.get(owner=bot, company=target).shares * gen_value(bias = 1-confidence))
                    order_price = round(random.gauss(current_price, current_price/10),2)
                    if shares > 0:
                        print "Sell "+" ".join([str(bot.id), target.symbol, str(int(shares)), str(order_price)])
                        global_obj = bot.industryconfidence_set.get(industry_id=1)
                        global_obj.subtract(.05)
                        company_obj = bot.companyconfidence_set.get(company_id=target.id)
                        company_obj.subtract(.05)
                        bot.subtractIndustryConfidences(target, .05)
                        time.sleep(.1)
