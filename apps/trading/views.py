from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, ExpressionWrapper, DecimalField
from django.core import serializers
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from models import *

import json
from decimal import Decimal

def index(response):
    companies = Company.objects.getCompanyList()
    user_orders = Order.objects.getUserOrders(response.session["user"]["id"])
    user_portfolio = Stock.objects.getUserPortfolio(response.session["user"]["id"])
    user_cash = User.objects.get(id=response.session["user"]["id"]).cash
    return render(response, "trading/index.html", {"companies":companies, "user_orders":user_orders, "user_portfolio":user_portfolio, "user_cash":user_cash})

def display_company(response, id):
    company = Company.objects.get(id=id)
    return render(response, "trading/company.html", {"company":company})

def get_asks_for_company(response, id):
    return JsonResponse(list(Order.objects.filter(company_id=id).filter(open=True).filter(buy_order=False).values("price", "shares").order_by("price")), safe=False)

def get_bids_for_company(response, id):
    return JsonResponse(list(Order.objects.filter(company_id=id).filter(open=True).filter(buy_order=True).values("price", "shares").order_by("-price")), safe=False)

def get_user_orders_for_company(response, id):
    return JsonResponse(list(Order.objects.filter(owner_id=response.session["user"]["id"]).filter(company_id=id).filter(open=True).values("price", "shares", "buy_order", "created_at", "id").order_by("created_at")), safe=False)

def place_order(response, id):
    company = Company.objects.get(id=id)
    user=User.objects.get(id=response.session["user"]["id"])
    post = response.POST
    if (post["type"]=="buy"):
        if (Decimal(post["total"]) > user.cash):
            messages.error(response, "You do not have enough cash to complete this purchase!")
            return redirect("./")
        price = Decimal(post["price"])
        shares = int(post["shares"])
        user.cash -= Decimal(post["total"])
        user.save()
        asks = Order.objects.filter(company=company).filter(buy_order = False).filter(open=True).order_by("price","created_at")
        i = 0
        try:
            portfolio = Stock.objects.get(company=company, owner=user)
        except ObjectDoesNotExist:
            portfolio = Stock(company=company, owner=user, shares=0)
            portfolio.save()
        while(shares):
            if (i == len(asks) or price < asks[i].price):
                Order(company=company, owner=user, shares=shares, price=price, buy_order=True).save()
                break
            if (shares < asks[i].shares):
                asks[i].shares -= shares
                asks[i].save()
                asks[i].owner.cash += shares*asks[i].price
                asks[i].owner.save()
                portfolio.shares += shares
                portfolio.save()
                Order(company=company, owner=asks[i].owner, shares=shares, open=False, price=asks[i].price, buy_order=False, created_at=asks[i].created_at).save()
                break
            else:
                shares -= asks[i].shares
                asks[i].open = False
                asks[i].save()
                asks[i].owner.cash += asks[i].shares*asks[i].price
                asks[i].owner.save()
                portfolio.shares += asks[i].shares
                portfolio.save()
                i+= 1
        messages.success(response, "Your order has been placed.")
        return redirect("./")
    else:
        try:
            portfolio = Stock.objects.get(company=company, owner=user)
            if (Decimal(post["shares"]) > portfolio.shares):
                messages.error(response, "You do not have enough shares to complete this purchase!")
                return redirect("./")
        except ObjectDoesNotExist:
            messages.error(response, "You do not have enough shares to complete this purchase!")
            return redirect("./")
        price = Decimal(post["price"])
        shares = int(post["shares"])
        portfolio.shares -= shares
        if portfolio.shares == 0:
            portfolio.delete()
        else:
            portfolio.save()
        bids = Order.objects.filter(company=company).filter(buy_order = True).filter(open=True).order_by("-price","created_at")
        i = 0
        while(shares):
            if (i == len(bids) or price > bids[i].price):
                Order(company=company, owner=user, shares=shares, price=price, buy_order=False).save()
                break
            if (shares<bids[i].shares):
                bids[i].shares -= shares
                bids[i].save()
                try:
                    buyer_portfolio = Stock.objects.get(company=company, owner=bids[i].owner)
                except ObjectDoesNotExist:
                    buyer_portfolio = Stock(company=company, owner=bids[i].owner, shares=0)
                buyer_portfolio.shares += shares
                buyer_portfolio.save()
                user.cash += bids[i].price*shares
                user.save()
                Order(company=company, owner=bids[i].owner, shares=shares, open=False, price=bids[i].price, buy_order=False, created_at=bids[i].created_at).save()
                break
            else:
                shares -= bids[i].shares
                bids[i].open = False
                bids[i].save()
                try:
                    buyer_portfolio = Stock.objects.get(company=company, owner=bids[i].owner)
                except ObjectDoesNotExist:
                    buyer_portfolio = Stock(company=company, owner=bids[i].owner, shares=0)
                buyer_portfolio.shares += bids[i].shares
                buyer_portfolio.save()
                user.cash += bids[i].shares*bids[i].price
                user.save()
                i+= 1

        messages.success(response, "Your order has been placed.")
        return redirect("./")

def cancel_order(response, id):
    order = Order.objects.get(id=id)
    owner = order.owner
    if owner.id != response.session["user"]["id"]:
        messages.error(response, "That is not your order!")
        return redirect("/trading")
    if order.buy_order:
        owner.cash += order.price*order.shares
        owner.save()
    else:
        try:
            portfolio = Stock.objects.get(company=order.company, owner=owner)
            portfolio.shares += order.shares
        except ObjectDoesNotExist:
            portfolio = Stock(company=order.company, owner=owner, shares=order.shares)
        portfolio.save()
    comp = order.company_id
    order.delete()
    return redirect("/trading/company/"+str(comp))
