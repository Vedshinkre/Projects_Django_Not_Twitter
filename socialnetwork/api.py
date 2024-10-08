from django.db.models import Q
from django.db.models.sql.query import Query
from django.shortcuts import render
from fame.models import Fame, FameLevels,ExpertiseAreas,FameUsers
from socialnetwork.models import Posts, SocialNetworkUsers
from collections import defaultdict

from django.http import JsonResponse
from .models import SocialNetworkUsers
# general methods independent of html and REST views
# should be used by REST and html views


def _get_social_network_user(user) -> SocialNetworkUsers:
    """Given a FameUser, gets the social network user from the request. Assumes that the user is authenticated."""
    try:
        user = SocialNetworkUsers.objects.get(id=user.id)
    except SocialNetworkUsers.DoesNotExist:
        raise PermissionError("User does not exist")
    return user


def timeline(user: SocialNetworkUsers, start: int = 0, end: int = None, published=True):
    """Get the timeline of the user. Assumes that the user is authenticated."""
    _follows = user.follows.all()
    posts = Posts.objects.filter(
        (Q(author__in=_follows) & Q(published=published)) | Q(author=user)
    ).order_by("-submitted")
    if end is None:
        return posts[start:]
    else:
        return posts[start : end + 1]


def search(keyword: str, start: int = 0, end: int = None, published=True):
    """Search for all posts in the system containing the keyword. Assumes that all posts are public"""
    posts = Posts.objects.filter(
        Q(content__icontains=keyword)
        | Q(author__email__icontains=keyword)
        | Q(author__first_name__icontains=keyword)
        | Q(author__last_name__icontains=keyword),
        published=published,
    ).order_by("-submitted")
    if end is None:
        return posts[start:]
    else:
        return posts[start : end + 1]


def follows(user: SocialNetworkUsers, start: int = 0, end: int = None):
    """Get the users followed by this user. Assumes that the user is authenticated."""
    _follows = user.follows.all()
    if end is None:
        return _follows[start:]
    else:
        return _follows[start : end + 1]


def followers(user: SocialNetworkUsers, start: int = 0, end: int = None):
    """Get the followers of this user. Assumes that the user is authenticated."""
    _followers = user.followed_by.all()
    if end is None:
        return _followers[start:]
    else:
        return _followers[start : end + 1]


def follow(user: SocialNetworkUsers, user_to_follow: SocialNetworkUsers):
    """Follow a user. Assumes that the user is authenticated. If user already follows the user, signal that."""
    if user_to_follow in user.follows.all():
        return {"followed": False}
    user.follows.add(user_to_follow)
    user.save()
    return {"followed": True}


def unfollow(user: SocialNetworkUsers, user_to_unfollow: SocialNetworkUsers):
    """Unfollow a user. Assumes that the user is authenticated. If user does not follow the user anyway, signal that."""
    if user_to_unfollow not in user.follows.all():
        return {"unfollowed": False}
    user.follows.remove(user_to_unfollow)
    user.save()
    return {"unfollowed": True}

def submit_post(
    user: SocialNetworkUsers,
    content: str,
    cites: Posts = None,
    replies_to: Posts = None,
):
    """Submit a post for publication. Assumes that the user is authenticated.
    returns a tuple of three elements:
    1. a dictionary with the keys "published" and "id" (the id of the post)
    2. a list of dictionaries containing the expertise areas and their truth ratings
    3. a boolean indicating whether the user was banned and logged out and should be redirected to the login page
    """

    # create post instance:
    post = Posts.objects.create(
        content=content,
        author=user,
        cites=cites,
        replies_to=replies_to,
    )

    # classify the content into expertise areas:
        # only publish the post if none of the expertise areas contains bullshit:

    _at_least_one_expertise_area_contains_bullshit, _expertise_areas = (
        post.determine_expertise_areas_and_truth_ratings()
    )

    # Check if the user has a negative fame level in any expertise area
    fame_profiles = Fame.objects.filter(user=user)
    negative_fame_expertise_areas = set(
        fame.expertise_area.id for fame in fame_profiles if fame.fame_level.numeric_value < 0
    )
    expertise_area_ids = set(area["expertise_area"].id for area in _expertise_areas)
    contains_negative_fame_area = bool(negative_fame_expertise_areas & expertise_area_ids)

    post.published = not (_at_least_one_expertise_area_contains_bullshit or contains_negative_fame_area)
        #task 1 has been already completed

    redirect_to_logout = False
   
    if _at_least_one_expertise_area_contains_bullshit:
    # Get a list of IDs of expertise areas containing bullshit
     bullshit_expertise_areas = {i["expertise_area"].id for i in _expertise_areas if i["truth_rating"] == "bullshit"}

    for area_id in bullshit_expertise_areas:
        # Check if the user has fame in this specific expertise area
        if Fame.objects.filter(user=user, expertise_area_id=area_id).exists():
            faming = Fame.objects.get(user=user, expertise_area_id=area_id)
            try:
                # Reduce the fame level
                lower_fame_level = FameLevels.get_next_lower_fame_level(faming.fame_level)
                faming.fame_level = lower_fame_level
                faming.save()
            except ValueError:
                # Deactivate user if no lower fame level is available
                user.is_active = False
                user.save()
                redirect_to_logout = True

                # Unpublish all of the user's posts
                user_posts = Posts.objects.filter(author=user)
                for post in user_posts:
                    post.published = False
                    post.save()
        else:
            # If the user does not already have fame in this expertise area, assign the "Confuser" level
            confuser_level = FameLevels.objects.get(name="Confuser")
            Fame.objects.create(user=user, expertise_area_id=area_id, fame_level=confuser_level)


    post.save()

    return (
        {"published": post.published, "id": post.id},
        _expertise_areas,
        redirect_to_logout,
    )

def rate_post(
    user: SocialNetworkUsers, post: Posts, rating_type: str, rating_score: int
):
    """Rate a post. Assumes that the user is authenticated. If user already rated the post with the given rating_type,
    update that rating score."""
    user_rating = None
    try:
        user_rating = user.userratings_set.get(post=post, rating_type=rating_type)
    except user.userratings_set.model.DoesNotExist:
        pass

    if user == post.author:
        raise PermissionError(
            "User is the author of the post. You cannot rate your own post."
        )

    if user_rating is not None:
        # update the existing rating:
        user_rating.rating_score = rating_score
        user_rating.save()
        return {"rated": True, "type": "update"}
    else:
        # create a new rating:
        user.userratings_set.add(
            post,
            through_defaults={"rating_type": rating_type, "rating_score": rating_score},
        )
        user.save()
        return {"rated": True, "type": "new"}

def fame(user: SocialNetworkUsers):
    """Get the fame of a user. Assumes that the user is authenticated."""
    try:
        user = SocialNetworkUsers.objects.get(id=user.id)
    except SocialNetworkUsers.DoesNotExist:
        raise ValueError("User does not exist")

    return user, Fame.objects.filter(user=user)


def experts():
    """Return for each existing expertise area in the fame profiles a list of the users having positive fame for that
    expertise area. The list should be a Python dictionary with keys ``user'' (for the user) and ``fame_level_numeric''
    (for the corresponding fame value), and should be ranked, i.e. users with the highest fame are shown first, in case
    there is a tie, within that tie sort by date_joined (most recent first). Note that expertise areas with no expert
    may be omitted.
    """
    filter_fame = (Fame.objects.exclude(fame_level__numeric_value__lt=1 ))
    
    famelevels= FameLevels.numeric_value
    grouping = filter_fame.order_by('-fame_level__numeric_value', '-user__date_joined')
    def default():
        return "null"
    
    list = defaultdict(default)
    for i in grouping:
        if i.expertise_area not in list:
            list[i.expertise_area] = [{"user": i.user, "fame_level_numeric":i.fame_level.numeric_value}]
        else:
            list[i.expertise_area].append({"user": i.user, "fame_level_numeric":i.fame_level.numeric_value})
   
    return dict(list)






def bullshitters():
    """Return for each existing expertise area in the fame profiles a list of the users having negative fame for that
    expertise area. The list should be a Python dictionary with keys ``user'' (for the user) and ``fame_level_numeric''
    (for the corresponding fame value), and should be ranked, i.e. users with the lowest fame are shown first, in case
    there is a tie, within that tie sort by date_joined (most recent first). Note that expertise areas with no expert
    may be omitted.
    """
    filter_fame = (Fame.objects.exclude(fame_level__numeric_value__gt=1 ))
    
    famelevels= FameLevels.numeric_value
    grouping = filter_fame.order_by('fame_level__numeric_value', '-user__date_joined')
    def default():
        return "null"
    
    list = defaultdict(default)
    for i in grouping:
        if i.expertise_area not in list:
            list[i.expertise_area] = [{"user": i.user, "fame_level_numeric":i.fame_level.numeric_value}]
        else:
            list[i.expertise_area].append({"user": i.user, "fame_level_numeric":i.fame_level.numeric_value})
   
    return dict(list)



def follow_user(request, user_id):
    if request.user.is_authenticated:
        try:
            user_to_follow = SocialNetworkUsers.objects.get(id=user_id)
            result = follow(request.user, user_to_follow)
            return JsonResponse(result)
        except SocialNetworkUsers.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)
    return JsonResponse({"error": "Unauthorized"}, status=401)

def unfollow_user(request, user_id):
    if request.user.is_authenticated:
        try:
            user_to_unfollow = SocialNetworkUsers.objects.get(id=user_id)
            result = unfollow(request.user, user_to_unfollow)
            return JsonResponse(result)
        except SocialNetworkUsers.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)
    return JsonResponse({"error": "Unauthorized"}, status=401)