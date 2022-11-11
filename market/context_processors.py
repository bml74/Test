from orgs.models import RequestForPaymentToGroupMember
from django.contrib.auth.decorators import login_required


@login_required
def get_num_notifications(request):
    try:
        num_notifications = RequestForPaymentToGroupMember.objects.filter(
            user_receiving_request=request.user
        ).count()
    except:
        num_notifications = 0
    return {
        'num_notifications': num_notifications
    }