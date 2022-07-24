from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from account.models import Account
from account.models import Wiadomosc
import datetime
from datetime import datetime

from .forms import ComposeForm
from .models import Thread, ChatMessage


class InboxView(LoginRequiredMixin, ListView):
    template_name = 'home.html'
    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)


class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'chat/thread.html'
    form_class = ComposeForm
    success_url = './'

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self):
        other_username  = self.kwargs.get("username")
        account = get_object_or_404(Account, username = other_username)
        user = self.request.user
        if Thread.objects.filter(first = self.request.user, second = account).exists():
            Wiadomosc.objects.create(date_of_change = datetime.now(),  special_data=user.username, type_of = "czat", desc = "Użytkownik "+ user.username +" nawiązał konwersację w czacie", target = account)
  
        elif Thread.objects.filter(second = self.request.user, first = account).exists():
            Wiadomosc.objects.create(date_of_change = datetime.now(), special_data=user.username, type_of = "czat", desc = "Użytkownik "+ user.username +" nawiązał konwersację w czacie", target = account)

        else:
            Wiadomosc.objects.create(date_of_change = datetime.now(), special_data=user.username, type_of = "czat", desc = "Użytkownik "+ user.username +" rozpoczął konwersację w czacie", target = account)
   
        obj, created    = Thread.objects.get_or_new(self.request.user, other_username)
        if obj == None:
            raise Http404
        return obj
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        message = form.cleaned_data.get("message")
        ChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)
        return redirect("chat_reload", self.other_username)

def chat_reload(request,other_username):
    return redirect("chat", other_username)