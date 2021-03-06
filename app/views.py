import json
from django.shortcuts import render
from django.http import HttpResponse
import operator
from datetime import datetime
from app.submissioncontroller import SubmissionController
from app.models import Report, Submission
from app.forms import UploadFileForm, APIUploadFileForm
from django.views.generic import View
from django.views.generic.edit import FormView
from lib.source_highlighter import highlight


class UploadFileView(FormView):
    """
    This is the view to which batch files are uploaded through a form.
    :return: redirects to report_file_list with the report_id as a parameter
    """

    form_class = UploadFileForm

    def form_valid(self, form):
        # if form contains no validation errors then process form
        # delete the file and description keys from the dictionary after
        # getting them to easily get the remaining parameters
        file = form.cleaned_data["file"]
        del form.cleaned_data["file"]
        description = form.cleaned_data["description"]
        del form.cleaned_data["description"]

        parameters = {}

        # get the optional parameters which have been specified
        for key, value in form.cleaned_data.items():
            if value is not None:
                parameters[key] = value

        sub_controller = SubmissionController(file, description, **parameters)

        report = sub_controller.report
        response = {"report_id": report.id}
        response = json.dumps(response)

        return HttpResponse(response, content_type="application/json")

    def form_invalid(self, form):
        # send back validation errors
        data = json.dumps(form.errors)
        print(data)
        return HttpResponse(data, status=400, content_type='application/json')


class APIUploadFileView(FormView):
    """
    View for API for third party applications to submit single user files to this system.
    :return: returns a percent match in a json object
    """

    def post(self, request, user_id, description):

        form_class = APIUploadFileForm
        form = self.get_form(form_class)

        if form.is_valid():
            file = form.cleaned_data["file"]
            kwargs = {"year": 2000}
            sub_controller = SubmissionController(file, user_id, description, admin_submission=False, **kwargs)
            report = sub_controller.report

            report.match_list.sort(key=operator.itemgetter("percent_match"), reverse=True)
            percent_match = report.match_list[0].get("percent_match") if report.match_list else 0
            response = {"percent_match": percent_match}
            response = json.dumps(response)
            return HttpResponse(response, content_type="application/json")

        else:
            data = json.dumps(form.errors)
            return HttpResponse(data, status=400, content_type='application/json')


class AboutView(View):
    """
    gives a list of the comparisons in the report
    """
    def get(self, request):
        return render(request, "about.html")


class ReportView(View):
    """
    gives a list of the comparisons in the report
    """
    def get(self, request, report_id):
        report = Report.objects.get(id=report_id)
        report.match_list = eval(report.match_list)
        report.match_list.sort(key=operator.itemgetter("percent_match"), reverse=True)
        # get the corresponding user_id and filename for each file id and insert it into the dictionary
        for match in report.match_list:
            submission = Submission.objects.get(id=match["file_2"])
            match["user2"] = submission.user_id
            submission = Submission.objects.get(id=match["file_1"])
            match["user1"] = submission.user_id

        return render(request, "report.html", {"title": "Report File List",
                                                        "report_id": report_id,
                                                        "object_list": report.match_list})


class ComparisonView(View):
    """
    shows the comparison between 2 given files.
    """
    def get(self, request, report_id, file_1_id, file_2_id):
        report = Report.objects.get(id=report_id)
        report.match_list = eval(report.match_list)
        file_1_id = int(file_1_id)
        file_2_id = int(file_2_id)
        #need to find the particular comparison comparing the 2 files with file_1_id and file_2_id
        comparison = [x for x in report.match_list if x["file_1"] == file_1_id and x["file_2"] == file_2_id][0]

        line_matches = comparison["line_matches"]
        # get the two sources files from the database
        file1 = Submission.objects.get(id=file_1_id)
        file2 = Submission.objects.get(id=file_2_id)
        # highlight the necessary lines
        source1 = highlight(file1.file_contents, line_matches, 0)
        source2 = highlight(file2.file_contents, line_matches, 1)

        return render(
            request,
            "comparison.html",
            {
                "title": "Report Page",
                "year": datetime.now().year,
                "percent_match": comparison["percent_match"],
                "file1": source1,
                "file2": source2
            })


class ReportListView(View):
    """
    lists the reports for submissions flagged
    """
    def get(self, request):
        report_list = Report.objects.all().order_by("-date")

        return render(
            request,
            "report_list.html",
            {
                "title": "Report List Page",
                "year": datetime.now().year,
                "report_list": report_list,
            })


class VulaDemoView(View):
    """
    Provides a simple button to use the API
    """
    def get(self, request):
        return render(request, "vula_demo.html")



