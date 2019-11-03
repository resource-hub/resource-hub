import json
import os
import random as r

from django.utils.dateparse import parse_date
from django.db.utils import IntegrityError

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
        user_form = UserBaseForm(data=user)
        info_form = InfoForm(data=user, files=None)
        address_form = AddressForm(data=user)
        bank_account_form = BankAccountForm(data=user)

        if (user_form.is_valid() and
                info_form.is_valid() and
                address_form.is_valid() and
                bank_account_form.is_valid()):

            new_bank_account = bank_account_form.save()
            new_address = address_form.save()

            new_info = info_form.save(commit=False)
            new_info.address = new_address
            new_info.bank_account = new_bank_account
            new_info.save()

            new_user = user_form.save(commit=False)
            new_user.info = new_info
            new_user.save()
        else:
            print("{} not created".format(name))
            print("{} {} {} {}".format(user_form.errors, info_form.errors,
                                       address_form.errors, bank_account_form.errors))
            continue

        print("User {} created".format(name))


def create_organizations():
    data = load_json("_organizations.json")
    users = User.objects.all()

    for o in data:
        organization_form = OrganizationForm(data=o)
        info_form = InfoForm(data=o)
        address_form = AddressForm(data=o)
        bank_account_form = BankAccountForm(data=o)

        if (organization_form.is_valid() and
                info_form.is_valid() and
                address_form.is_valid() and
                bank_account_form.is_valid()):

            new_organization = organization_form.save(commit=False)
            new_address = address_form.save()
            new_bank_account = bank_account_form.save()

            new_info = info_form.save(commit=False)
            new_info.address = new_address
            new_info.bank_account = new_bank_account
            new_info.save()

            new_organization.info = new_info
            new_organization.save()

            new_organization.members.add(
                User.objects.get(username="test"),
                through_defaults={
                    'role': OrganizationMember.ADMIN
                }
            )

            for i in range(0, 2):
                pos = r.randint(0, len(users)-1)
                new_organization.members.add(users[pos], through_defaults={
                    'role': OrganizationMember.MEMBER})

        else:
            print("{} not created".format(o['name']))
            print("{} {} {} {}".format(organization_form.errors, info_form.errors,
                                       address_form.errors, bank_account_form.errors))
            continue
        print("Organization {} created".format(o['name']))


def main():
    print("hello")
    create_test_users()


if __name__ == "__main__":
    main()
