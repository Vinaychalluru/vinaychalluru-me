from django.views.generic import TemplateView, View
from django.http.response import FileResponse


class AboutMe(TemplateView):
    template_name = "about_me.html"

    def get(self, request, *args, **kwargs):
        return super(AboutMe, self).get(request, *args, *kwargs)


class Profile(TemplateView):
    template_name = "profile.html"

    def get(self, request, *args, **kwargs):
        return super(Profile, self).get(request, *args, **kwargs)


class DownloadResume(View):

    def get(self, request, *args, **kwargs):
        from portfolio.settings import FILES_DIR
        resume_filename = "Vinay_10Y_Python_Team_Lead.pdf"
        resume_file = FILES_DIR / resume_filename
        return FileResponse(open(resume_file, 'rb'), as_attachment=True, filename=resume_filename, status=200)
