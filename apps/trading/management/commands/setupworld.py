from ...models import Company, Industry, Company_industries, Stock

from .... import users

from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand, CommandError

from django.db import IntegrityError

import barnum
import random

class Command(BaseCommand):
    help = 'Sets up the world for trading'


    def handle(self, *args, **options):
        users.models.Bot.objects.all().delete() #delete all the bots, to regen them.
        make_industries()
        make_companies()
        for user in users.models.User.objects.all():
            for company in Company.objects.all():
                Stock(company=company, owner=user, shares=100).save()


industry_from_name={"Telecom": "Telephony","Software": "Software","Technology": "Technology","Hardware": "Hardware","Electronics": "Technology","Consulting": "Consulting","General": "Generic","Frontier": "Generic","Alpha": "Generic","Industries": "Manufacturing","Net": "Software","People": "Generic","Star": "Generic","Bell": "Telephony","Research": "Generic","Architecture": "Manufacturing","Building": "Construction","Construction": "Construction","Medicine": "Medical","Hill": "Generic","Graphics": "Graphical Design","Analysis": "Consulting","Vision": "Generic","Contract": "Consulting","Solutions": "Generic","Advanced": "Generic","Venture": "Generic","Innovation": "Generic","Systems": "Technology","Solutions": "Generic","Provider": "Generic","Design": "Design","Internet": "Technology","Virtual": "Software","Vision": "Generic","Application": "Generic","Signal": "Technology","Network": "Technology","Net": "Technology","Data": "Software","Electronic": "Technology","Max": "Generic","Adventure": "Generic","Atlantic": "Generic","Pacific": "Generic","North": "Generic","East": "Generic","South": "Generic","West": "Generic","Speed": "Generic","Universal": "Generic","Galaxy": "Generic","Future": "Generic","Digital": "Software","Studio": "Generic","Interactive": "Software","Source": "Generic","Omega": "Generic","Direct": "Generic","Resource": "Generic","Power": "Generic","Federated": "Generic","Star": "Generic"}

def make_industries():
    Industry.objects.all().delete()
    print Industry.objects.all().count()
    Industry(name="Generic", id=1).save()
    Industry(name="Technology").save()
    Industry(name="Telephony", parent=Industry.objects.get(name="Technology")).save()
    Industry(name="Hardware", parent=Industry.objects.get(name="Technology")).save()
    Industry(name="Software", parent=Industry.objects.get(name="Technology")).save()
    Industry(name="Construction").save()
    Industry(name="Residential", parent=Industry.objects.get(name="Construction")).save()
    Industry(name="Commercial", parent=Industry.objects.get(name="Construction")).save()
    Industry(name="Industrial", parent=Industry.objects.get(name="Construction")).save()
    Industry(name="Medical").save()
    Industry(name="Medical Research", parent=Industry.objects.get(name="Medical")).save()
    Industry(name="Medical Care", parent=Industry.objects.get(name="Medical")).save()
    Industry(name="Consulting").save()
    Industry(name="Design").save()
    Industry(name="Graphical Design", parent=Industry.objects.get(name="Design")).save()
    Industry(name="Audiovisual", parent=Industry.objects.get(name="Design")).save()
    Industry(name="Legal").save()
    Industry(name="Patent Law", parent=Industry.objects.get(name="Legal")).save()
    Industry(name="Civil Law", parent=Industry.objects.get(name="Legal")).save()
    Industry(name="Criminal Law", parent=Industry.objects.get(name="Legal")).save()
    Industry(name="Corporate Law", parent=Industry.objects.get(name="Legal")).save()
    Industry(name="Manufacturing").save()
    Industry(name="Technological", parent=Industry.objects.get(name="Manufacturing")).save()
    Industry(name="Industrial", parent=Industry.objects.get(name="Manufacturing")).save()
    Industry(name="Consumer", parent=Industry.objects.get(name="Manufacturing")).save()

def get_industries_from_split_name(name):
    industries = []
    for word in name:
        industry = industry_from_name.get(word,"Generic")
        if industry != "Generic" and industry not in industries:
            industries.append(industry)
    return industries

def make_companies():
    Company.objects.all().delete()
    for x in range(50):
        valid = False
        while not valid:
            if random.random() < .03:
                name = barnum.create_company_name(biz_type="LawFirm")
                namesplit = name.split()
                symbol = namesplit[0][0]+namesplit[1][0]+namesplit[3][0] #Get the names of the partners
                industries = ["Legal"]
            elif random.random() < .6:
                name = barnum.create_company_name(biz_type="Generic")
                namesplit = name.split()
                if len(namesplit) > 2:
                    symbol = namesplit[0][0]+namesplit[1][0]+namesplit[2][0]
                elif len(namesplit) == 2:
                    symbol = namesplit[0][0]+namesplit[1][0]
                else: #One word name, trash this company
                    continue
                industries = get_industries_from_split_name(namesplit)
            else:
                name = barnum.create_company_name(biz_type="Short")
                namesplit = name.split()
                if len(namesplit) > 2:
                    symbol = namesplit[0][0]+namesplit[1][0]+namesplit[2][0]
                elif len(namesplit) == 2:
                    symbol = namesplit[0][0]+namesplit[1][0]
                else: #One word name, trash this company
                    continue
                industries = get_industries_from_split_name(namesplit)
            try:
                company = Company(name=name, symbol=symbol)
                company.save()
                if "Consulting" in industries:
                    industries.remove("Consulting")
                    Company_industries(company=company, industry=Industry.objects.get(name="Consulting")).save()
                if not len(industries):
                    industries.append("Generic")
                for industry in industries:
                    try:
                        company.add_industry(industry)
                    except ObjectDoesNotExist as e:
                        print industry
                        raise e
                valid=True
            except IntegrityError:
                pass #duplicate symbol, trash this company
