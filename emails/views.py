from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmailForm
from django.contrib import messages
from .tasks import send_email_task
from .models import Subscriber, Email, Sent, EmailTracking
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect


def send_email(request):
    if request.method == 'POST':
        email_form = EmailForm(request.POST, request.FILES)
        if email_form.is_valid():
            email = email_form.save()

            mail_subject = request.POST.get('subject')
            message = request.POST.get('body')
            email_list = request.POST.get('email_list')

            email_list = email.email_list
            
            subscribers = Subscriber.objects.filter(email_list=email_list)

            to_email = [email.email_address for email in subscribers]

            if email.attachment:
                attachment = email.attachment.path
            else:
                attachment = None

            email_id = email.id

            send_email_task.delay(mail_subject, message, to_email, attachment, email_id)

            messages.success(request, 'Email sent successfully!')
            return redirect('send_email')
    else:
        email = EmailForm()
        context = {
            'email_form': email,
        }
        return render(request, 'emails/send-email.html', context)
    

def track_click(request, unique_id):
    try:
        email_tracking = EmailTracking.objects.get(unique_id=unique_id)
        url = request.GET.get('url')

        if not email_tracking.clicked_at:
            email_tracking.clicked_at = timezone.now()
            email_tracking.save()
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(url)
    except Exception:
        return HttpResponse('Email tracking record not found!')


def track_open(request, unique_id):
    try:
        email_tracking = EmailTracking.objects.get(unique_id=unique_id)
        if not email_tracking.opened_at:
            email_tracking.opened_at = timezone.now()
            email_tracking.save()
            return HttpResponse('Email opened successfully!')
        else:
            return HttpResponse('Email already opened.')
    except Exception:
        return HttpResponse('Email tracking record not found!')
    


def track_dashboard(request):
    emails = Email.objects.all().annotate(total_sent=Sum('sent__total_sent')).order_by('-sent_at')
    
    context = {
        'emails': emails,
    }
    return render(request, 'emails/track-dashboard.html', context)


def track_stats(request, pk):
    email = get_object_or_404(Email, pk=pk)
    sent = Sent.objects.get(email=email)
    context = {
        'email': email,
        'total_sent': sent.total_sent
    }
    return render(request, 'emails/track-stats.html', context)