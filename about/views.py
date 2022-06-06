import logging

from django.http.response import FileResponse, HttpResponseServerError
from django.views.generic import TemplateView, View


class Profile(TemplateView):
    template_name = "profile.html"

    def get(self, request, *args, **kwargs):
        try:
            return super(Profile, self).get(request, *args, **kwargs)
        except Exception as ex:
            logging.error(ex.args[0], exc_info=True)
            return HttpResponseServerError(content=ex.args[0])


class DownloadResume(View):

    def get(self, request, *args, **kwargs):
        try:
            from portfolio.settings import FILES_DIR
            resume_filename = "Vinay_10Y_Python_Team_Lead.pdf"
            resume_file = FILES_DIR / resume_filename
            return FileResponse(open(resume_file, 'rb'), as_attachment=True, filename=resume_filename, status=200)
        except Exception as ex:
            logging.error(ex.args[0], exc_info=True)
            return HttpResponseServerError(content=ex.args[0])
