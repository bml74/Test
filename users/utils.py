from .models import FollowersCount
from orgs.models import GroupProfile


def get_user_followers_data(user):
    # Who is following the user?
    list_of_followers = FollowersCount.objects.filter(user_being_followed=user).all()
    num_followers = len(list_of_followers)
    # Who is the user following?
    users_that_user_with_profile_being_viewed_is_following = FollowersCount.objects.filter(follower_of_user=user).all()
    num_following = len(users_that_user_with_profile_being_viewed_is_following)
    # Return data in tuple:
    return (list_of_followers, num_followers, users_that_user_with_profile_being_viewed_is_following, num_following)



def get_groups_that_user_created(user):
    groups_that_user_created = GroupProfile.objects.filter(group_creator=user).all()
    group_creator_data = {}
    for item in groups_that_user_created:
        group_creator_data[item.group.name] = item.group.id

    num_groups_that_user_created = len(groups_that_user_created)  

    return (group_creator_data, num_groups_that_user_created)


def get_groups_that_user_is_a_member_of(user):
    groups_that_user_created = GroupProfile.objects.filter(group_creator=user).all()
    group_creator_data = {}
    for item in groups_that_user_created:
        group_creator_data[item.group.name] = item.group.id

    group_profiles_of_groups_that_user_is_a_member_of = GroupProfile.objects.filter(group_members__username=user.username).all() # Gets all Group Profiles where user is a member according to the ManyToMany field.
    # Create a dictionary in the format: {"GROUP_NAME": GROUP_ID, ....}
    group_profiles_of_groups_that_user_is_a_member_of = set(list(group_profiles_of_groups_that_user_is_a_member_of) + list(groups_that_user_created))
    group_member_data = {}
    for item in group_profiles_of_groups_that_user_is_a_member_of:
        group_member_data[item.group.name] = item.group.id

    num_groups_that_user_is_a_member_of = len(group_profiles_of_groups_that_user_is_a_member_of)
    
    return (group_member_data, num_groups_that_user_is_a_member_of)


def get_groups_that_user_follows(user):
    groups_that_user_follows = GroupProfile.objects.filter(group_followers__username=user.username).all() # Gets all Group Profiles where user is a member according to the ManyToMany field.
    group_follows_data = {}
    for item in groups_that_user_follows:
        group_follows_data[item.group.name] = item.group.id
    num_groups_that_user_is_following = len(groups_that_user_follows)
    return (group_follows_data, num_groups_that_user_is_following)
