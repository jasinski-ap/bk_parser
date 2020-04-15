from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from protokoly.parser import bk_dict_from_url
from protokoly.docx_generator import protokol_generator


class LandingPage(View):
    template_name = "bk/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # get url
        url = request.POST.get('url')
        validator = URLValidator()
        url_is_valid = True
        # get project
        project = request.POST.get('project')
        try:
            validator(url)
        except ValidationError as msg:
            print(msg)
            url_is_valid = False
            messages.error(request, 'Invalid URL.')

        if "bazakonkurencyjnosci.funduszeeuropejskie.gov.pl/" not in url:
            url_is_valid = False
            messages.error(request, 'URL Not from BK. ')

        if url_is_valid:
            try:
                bk_data = bk_dict_from_url(url)
            except Exception as msg:
                print(msg)
                bk_data = None
                messages.error(
                    request, 'Error. Data not retrived from url. %s' % msg
                )
        else:
            bk_data = None
        if bk_data:
            try:
                filename, generated_file = protokol_generator(bk_data, project)
            except Exception as msg:
                print(msg)
                filename = None
                generated_file = None
                messages.error(request, 'Error. Report not generated.')
        else:
            filename = None
            generated_file = None

        if filename and generated_file:
            response = HttpResponse(
                generated_file,  # use the stream's contents
                content_type=
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

            response["Content-Disposition"
                    ] = f'attachment; filename = "{filename}"'
            response["Content-Encoding"] = "UTF-8"
            return response
        return render(request, self.template_name)