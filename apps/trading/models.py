from __future__ import unicode_literals

from django.db import models, IntegrityError


from ..users.models import User

import random

# Create your models here.

class Industry(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', default=1, related_name="children", on_delete=models.CASCADE)#"Generic" should always have the ID #1
    def getCompanies(self):
        companies = self.companies.all()
        for child in children.all():
            companies |= child.getCompanies()
        return companies.distinct()

class CompanyManager(models.Manager):
    def getCompanyList(self):
        return self.raw(("select trading_company.id, symbol, name, "
        "(select max(bids.price) from trading_order as bids where bids.company_id==trading_company.id and bids.buy_order==1 and bids.open==1) as bid, "
        "(select min(asks.price) from trading_order as asks where asks.company_id==trading_company.id and asks.buy_order==0 and asks.open==1) as ask, "
        "(select orders.price from trading_order as orders where orders.company_id==trading_company.id and orders.open==0 order by orders.created_at limit 1) as last_trade "
        "from trading_company"
        ))

class Company(models.Model):
    name = models.CharField(max_length=255)
    stocks = models.ManyToManyField(User, through="Stock", related_name="portfolio", blank=True)
    trades = models.ManyToManyField(User, through="Order", related_name="orders", blank=True)
    industries = models.ManyToManyField(Industry, through="Company_industries", related_name="companies", blank=True)
    symbol = models.CharField(max_length=3, unique=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = CompanyManager()
    def add_industry(self, industry):
        if type(industry) is str or type(industry) is unicode:
            industry=Industry.objects.get(name=industry)
        children = industry.children.all()
        if len(children):
            child = "Consulting"
            while(child=="Consulting"):
                child = random.choice(list(children))
            self.add_industry(child)
        else:
            try:
                self.save()
                Company_industries(company=self, industry=industry).save()
            except IntegrityError:
                return #duplicate industry, stop adding.
            parent = industry.parent
            rand = random.random()
            if rand < .5:
                self.add_industry(parent)
            elif rand < .7:
                self.add_industry("Generic")

class StockManager(models.Manager):
    def getUserPortfolio(self, user_id):
        result = self.raw('select stocks.id, companies.id as company_id, companies.name, companies.symbol, stocks.shares, (select orders.price from trading_order as orders where orders.company_id==companies.id and orders.open==0 order by orders.created_at limit 1) as price, (stocks.shares*(select orders.price from trading_order as orders where orders.company_id==companies.id and orders.open==0 order by orders.created_at limit 1)) as total from trading_stock as stocks join trading_company as companies on stocks.company_id = companies.id where stocks.owner_id='+str(user_id))
        print list(result)
        return result

class Stock(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    shares = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = StockManager()

class OrderManager(models.Manager):
    def getUserOrders(self, user_id):
        result = self.filter(owner_id=user_id).filter(open=True).annotate(total=models.ExpressionWrapper(models.F("price")*models.F("shares"), models.DecimalField(max_digits =12, decimal_places = 2)))
        return

class Order(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    shares = models.IntegerField()
    open = models.BooleanField(default=True)
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    buy_order = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = OrderManager()

class Company_industries(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)

    class Meta():
        unique_together = ("company", "industry")
