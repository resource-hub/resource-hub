import json
import os
import random as r

from django.utils.dateparse import parse_date
from django.db.utils import IntegrityError
from django.http.request import HttpRequest

from core.models import *
from core.forms import *


def load_json(filename):
    cur_dir = os.path.dirname(__file__)
    file_path = os.path.join(cur_dir, filename)
    data = []

    with open(file_path) as f:
        data = json.load(f)

    return data


def create_users():
    data = load_json("_users.json")

    for user in data:
        name = user['first_name'] + " " + user['last_name']
        request = HttpRequest()
        request.POST = user
        user_form = UserFormManager(request)

        if (user_form.is_valid()):
            new_user = user_form.save()
        else:
            print("{} not created. Form not valid".format(name))
            continue

        print("User {} created".format(name))


def create_organizations():
    data = load_json("_organizations.json")
    users = User.objects.all()

    for o in data:
        request = HttpRequest()
        request.POST = o
        request.user = users[0]
        organization_form = OrganizationFormManager(request)

        if organization_form.is_valid():
            new_organization = organization_form.save()

            for i in range(0, 2):
                pos = r.randint(0, len(users)-1)
                new_organization.members.add(users[pos], through_defaults={
                    'role': OrganizationMember.MEMBER})

        else:
            print("{} not created. Form not valid".format(o['name']))
            continue
        print("Organization {} created".format(o['name']))


def main():
    create_users()
    create_organizations()


if __name__ == "__main__":
    main()
