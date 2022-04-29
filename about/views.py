from django.shortcuts import render
from django.views.generic import TemplateView


class AboutMe(TemplateView):
    template_name = "about_me.html"

    def get(self, request, *args, **kwargs):
        return super(AboutMe, self).get(request, *args, *kwargs)
