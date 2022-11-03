import json
from django.dispatch import receiver
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import DirectMessage, Room, RoomMembershipRequest
from .forms import DirectMessageForm
from config.utils import get_group_and_group_profile_from_group_id, formValid
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME
from config.abstract_settings.model_fields import ROOM_FIELDS

@login_required
def inbox(request):
	all_other_users = User.objects.exclude(id=request.user.id) # Get all users except for the logged in user.
	context = {
		"all_users": all_other_users,
		"direct_message": True
	}
	return render(request, "messaging/inbox.html", context=context)


@login_required
def detail(request, pk):
	other_user = get_object_or_404(User, id=pk)
	form = DirectMessageForm()
	if request.method == "POST":
		form = DirectMessageForm(request.POST)
		if form.is_valid():
			msg = form.save(commit=False)
			msg.sender_of_message = request.user
			msg.receiver_of_message = other_user
			msg.save()
			return redirect("detail", pk=other_user.id)
	all_messages_from_current_user_to_other_user = DirectMessage.objects.filter(sender_of_message=request.user, receiver_of_message=other_user).all()
	all_messages_from_other_user_to_current_user = DirectMessage.objects.filter(sender_of_message=other_user, receiver_of_message=request.user).all()
	all_messages_between_these_two_users = list(all_messages_from_current_user_to_other_user) + list(all_messages_from_other_user_to_current_user)
	all_messages_between_these_two_users.sort(key=lambda msg: msg.id)

	# Update unread messages so that seen is True
	unread_messages = DirectMessage.objects.filter(sender_of_message=other_user, receiver_of_message=request.user, seen=False).all()
	unread_messages.update(seen=True)

	all_other_users = User.objects.exclude(id=request.user.id)

	context = {
		"logged_in_user": request.user,
		"other_user": other_user,
		"all_users": all_other_users,
		"form": form,
		"all_messages_between_these_two_users": all_messages_between_these_two_users,
		"num_messages_from_other_user_to_current_user": all_messages_from_other_user_to_current_user.count(),
		"direct_message": True
	}
	return render(request, "messaging/detail.html", context=context)


def sentDirectMessage(request, pk):
	other_user = get_object_or_404(User, id=pk)
	data = json.loads(request.body)
	msg_body = data['message']
	new_direct_message = DirectMessage(body=msg_body, sender_of_message=request.user, receiver_of_message=other_user)
	new_direct_message.save()
	return JsonResponse(f"Message sent. Message content: {new_direct_message.body}", safe=False)


def receivedDirectMessages(request, pk):
	# Get messages sent by other user in real time.
	other_user = get_object_or_404(User, id=pk)
	messages_sent_by_other_user = DirectMessage.objects.filter(sender_of_message=other_user, receiver_of_message=request.user).all()
	msgs = []
	for message in messages_sent_by_other_user:
		msgs.append(message.body)
	return JsonResponse(msgs, safe=False)


def directMessageNotification(request):
	all_other_users = User.objects.exclude(id=request.user.id)
	num_unread = []
	for other_user in all_other_users:
		msgs = DirectMessage.objects.filter(sender_of_message=other_user, receiver_of_message=request.user, seen=False).all()
		num_unread.append(msgs.count())
	return JsonResponse(num_unread, safe=False)


@login_required
def enter_room(request):
	context = {"direct_message": True}
	return render(request, "messaging/home.html", context=context)


def room(request, pk):
    # username = request.GET.get('username')
    room = Room.objects.get(id=pk)
    return render(request, 'messaging/room.html', {
        'username': request.user.username,
        'room': room,
        'room_details': room,
		'room_id': room.id,
		"direct_message": True
    })

def checkview(request):
	room_name = request.POST['room_name']
	# username = request.POST['username']

	if Room.objects.filter(title=room_name).exists():
		room_obj = Room.objects.filter(title=room_name).first()
		# return redirect('/messaging/room/'+str(room_obj.id)+'/?username='+username)
		return redirect("room", pk=room_obj.id)
	else:
		new_room = Room.objects.create(title=room_name)
		new_room.save()
		# return redirect('/messaging/room/'+str(new_room.id)+'/?username='+username)
		return redirect("room", pk=new_room.id)


def send(request):
	message = request.POST['message']
	# username = request.POST['username']
	room_id = request.POST['room_id']
	room = Room.objects.get(id=room_id)

	new_message = DirectMessage.objects.create(body=message, sender_of_message=request.user, room=room)
	new_message.save()
	return HttpResponse('Message sent successfully')


def getMessages(request, room_id):
	room = Room.objects.get(id=room_id)
	messages = DirectMessage.objects.filter(room=room)
	print(room)
	print(messages)
	msgs = [{
		"body": message.body,
		"sender": get_object_or_404(User, id=message.sender_of_message.id).username,
		"timestamp": message.date_time_sent
	} for message in messages]
	return JsonResponse({"messages":msgs})


@login_required
def room_membership(request, username, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, username=username)
    if room.room_members.filter(id=user.id).exists():
        room.room_members.remove(user)
    else:
        room.room_members.add(user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


# Membership request: Create membership request object
@login_required
def request_room_membership(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Boolean filters:
    user_is_member = request.user in room.room_members.all()
    request_exists = RoomMembershipRequest.objects.filter(user_requesting_to_become_room_member=request.user, room_receiving_membership_request=room).exists()
    # If user is not a member and user has not made a request for this group so far, create request and save.
    if not user_is_member and not request_exists:
        group_request = RoomMembershipRequest(user_requesting_to_become_room_member=request.user, room_receiving_membership_request=room)
        group_request.save()
    return redirect('rooms_that_user_is_a_member_of_or_user_created', username=request.user.username)


def delete_membership_request(username, room_receiving_request):
    user = get_object_or_404(User, username=username)
    membership_request = get_object_or_404(RoomMembershipRequest, user_requesting_to_become_room_member=user, room_receiving_membership_request=room_receiving_request)
    membership_request.delete()


# Withdraw membership request: Delete membership request object
@login_required
def withdraw_room_membership_request(request, username, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, username=username)
    user_is_member = user in room.room_members.all()
    request_exists = RoomMembershipRequest.objects.filter(user_requesting_to_become_room_member=user, room_receiving_membership_request=room).exists()
    # If user is not a member and user has not made a request for this group so far, create request and save.
    if not user_is_member and request_exists:
        delete_membership_request(username, room)
    return redirect('rooms_that_user_is_a_member_of_or_user_created', username=user.username)


# Accept memebrship request: Add to MTM field and delete membership request object
@login_required
def accept_room_membership_request(request, username, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Add membership
    room_membership(request, username, room_id)
    delete_membership_request(username, room)
    return redirect('room', pk=room_id)


class RoomDetailView(UserPassesTestMixin, DetailView):
	model = Room
	context_object_name = 'item'

	def test_func(self, request):
		room = get_object_or_404(Room, id=self.kwargs['pk'])
		if self.request.user in room.room_members:
			return True
		return False

	def get(self, request, *args, **kwargs):
		room = get_object_or_404(Room, pk=kwargs['pk'])
		return render(request, 'messaging/room.html', {
			'username': request.user.username,
			'room': room,
			'room_details': room,
			'room_id': room.id,
			"direct_message": True
    	})


class RoomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
	model = Room
	fields = ROOM_FIELDS
	template_name = FORM_VIEW_TEMPLATE_NAME

	def form_valid(self, form):
		form.instance.room_creator = self.request.user
		if form.instance.room_group_profile:
			group = form.instance.room_group_profile.group
		else: 
			group = None
        # If user has chosen a group, make sure the user is a member of that group:
		return super().form_valid(form) if formValid(user=form.instance.room_creator, group=group) else super().form_invalid(form)

	def test_func(self):
		return self.request.user.is_authenticated

	def get_context_data(self, **kwargs):
		context = super(RoomCreateView, self).get_context_data(**kwargs)
		header = "Create room"
		create = True # If update, false; if create, true
		context.update({"header": header, "create": create})
		return context


class RoomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Room
	fields = ROOM_FIELDS
	template_name = FORM_VIEW_TEMPLATE_NAME

	def form_valid(self, form):
		form.instance.room_creator = self.request.user
		if form.instance.room_group_profile:
			group = form.instance.room_group_profile.group
		else: 
			group = None
        # If user has chosen a group, make sure the user is a member of that group:
		return super().form_valid(form) if formValid(user=form.instance.room_creator, group=group) else super().form_invalid(form)

	def test_func(self):
		return self.request.user == self.get_object().room_creator

	def get_context_data(self, **kwargs):
		context = super(RoomUpdateView, self).get_context_data(**kwargs)
		header = "Update room"
		create = False # If update, false; if create, true
		context.update({"header": header, "create": create})
		return context


class RoomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Room
    success_url = '/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        return self.request.user == self.get_object().room_creator

    def get_context_data(self, **kwargs):
        context = super(RoomDeleteView, self).get_context_data(**kwargs)
        room = get_object_or_404(Room, id=self.kwargs.get('pk'))
        title = f"Room: {room.title}"
        context.update({"type": "room", "title": title})
        return context


class RoomListView(ListView):
	model = Room
	context_object_name = 'items'
	template_name = 'messaging/room_list_view.html'
	paginate_by = 10

	def get_context_data(self, **kwargs):
		context = super(RoomListView, self).get_context_data(**kwargs)
		rooms_that_user_is_a_member_of_or_user_created = set(list(Room.objects.filter(room_members=self.request.user.id)) + list(Room.objects.filter(room_creator=self.request.user)))
		context.update({"header": "Explore all rooms", "direct_message": False, "rooms_that_user_is_a_member_of_or_user_created": rooms_that_user_is_a_member_of_or_user_created})
		return context


class UserRoomListView(ListView):
	model = Room
	context_object_name = 'items'
	paginate_by = 10

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Room.objects.filter(author=user).order_by('-date_posted')

	def get(self, request, *args, **kwargs):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		rooms_that_user_is_a_member_of_or_user_created = set(list(Room.objects.filter(room_members=user.id)) + list(Room.objects.filter(room_creator=user)))
		context = {
			"header": f"Rooms that I am a member of or have created", 
			"rooms_that_user_is_a_member_of_or_user_created": rooms_that_user_is_a_member_of_or_user_created,
			"direct_message": False,
		}
		return render(request, "messaging/room_list_view.html", context=context)


