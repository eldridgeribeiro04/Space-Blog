from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views import generic
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from . import models


from groups.models import Group, GroupMember


class CreateGroup(LoginRequiredMixin, generic.CreateView):
    
    fields = ('name', 'description')
    model = Group

    def get_absolute_url(self):
        return reverse("{% url 'groups:all' %}", kwargs=self.pk)


class SingleGroup(generic.DetailView):
    model = Group


class ListGroups(generic.ListView):
    model = Group


class JoinGroup(LoginRequiredMixin, generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug': self.kwargs.get('slug')})
    
    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs.get('slug'))

        try:
            GroupMember.objects.create(user=self.request.user, group=group)
        except IntegrityError:
            messages.warning(self.request, 'Warning, already a member')
        else:
            messages.success(self.request, "You are now a member!")

        return super().get(request, *args, **kwargs)




class LeaveGroup(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug': self.kwargs.get('slug')})
    
    def get(self, request, *args, **kwargs):

        try:
            membership = models.GroupMember.objects.filter(
                user = self.request.user,
                group__slug = self.kwargs.get('slug')
            ).get()
        except models.GroupMember.DoesNotExist:
            messages.warning(self.request, 'Sorry, you are not a member of this group')
        else:
            membership.delete()
            messages.success(self.request, 'You have left the group')
        
        return super().get(request, *args, **kwargs)
