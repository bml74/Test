import json
from django.dispatch import receiver

from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import DirectMessage
from .forms import DirectMessageForm



@login_required
def inbox(request):
	all_other_users = User.objects.exclude(id=request.user.id) # Get all users except for the logged in user.
	context = {
		"all_users": all_other_users
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
		"num_messages_from_other_user_to_current_user": all_messages_from_other_user_to_current_user.count()
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

