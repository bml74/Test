from django.shortcuts import get_object_or_404
from orgs.models import ListingForGroupMembers, RequestForPaymentToGroupMember
from config.utils import getGroupProfile



def print_divider():
    print("-" * 20)


def get_group_and_group_profile_and_listing_from_listing_id(ListingForGroupMembers_obj_id):
    listing_for_group_members = get_object_or_404(ListingForGroupMembers, id=ListingForGroupMembers_obj_id)
    group = listing_for_group_members.group
    group_profile = getGroupProfile(group)
    return (group, group_profile, listing_for_group_members)


def get_data_on_listing_for_group_members(ListingForGroupMembers_obj_id):
    """
    This function gets a ton of data on listings for group members.
    It returns a tuple of four items:

    1) Group object.
    2) GroupProfile object.
    3) ListingForGroupMembers object.
    4) A list that contains all the users of the group members who haven't paid their dues for the ListingForGroupMembers object. The elements in the array are User objects.
    """
    (group, group_profile, listing_for_group_members) = get_group_and_group_profile_and_listing_from_listing_id(ListingForGroupMembers_obj_id)

    for member in listing_for_group_members.members_who_have_paid.all():
        assert(member in group_profile.group_members.all() or member == group_profile.group_creator)
    
    list_of_members = list(group_profile.group_members.all())
    list_of_members_who_have_paid = list(listing_for_group_members.members_who_have_paid.all())
    list_of_members_who_have_not_paid = list(set(list_of_members) - set(list_of_members_who_have_paid))
    return (
        group, 
        group_profile, 
        listing_for_group_members, 
        list_of_members_who_have_paid,
        list_of_members_who_have_not_paid
    )


def create_payment_request_from_group_member(user_sending_request, user_receiving_request, ListingForGroupMembers_obj_id):
    (group, group_profile, listing_for_group_members, list_of_members_who_have_paid, list_of_members_who_have_not_paid) = get_data_on_listing_for_group_members(ListingForGroupMembers_obj_id)
    assert(user_sending_request == group_profile.group_creator)
    assert(user_receiving_request in list_of_members_who_have_not_paid)
    if not RequestForPaymentToGroupMember.objects.filter(user_receiving_request=user_receiving_request, listing_for_group_members=listing_for_group_members).exists():
        new_payment_request = RequestForPaymentToGroupMember(
            user_receiving_request=user_receiving_request,
            listing_for_group_members=listing_for_group_members
        )
        new_payment_request.save()


def remove_payment_request_from_group_member(user_sending_request, user_receiving_request, listing_for_group_members):
    payment_request = get_object_or_404(
        RequestForPaymentToGroupMember,
        user_receiving_request=user_receiving_request,
        listing_for_group_members=listing_for_group_members
    )
    payment_request.delete()


