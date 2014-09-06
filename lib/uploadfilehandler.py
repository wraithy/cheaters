import datetime
import os
import shutil
import zipfile
from zipfile import ZipFile, ZIP_DEFLATED
import io
from app.models import Submission
from cheaters import settings
import mimetypes

class FileHandler():

    def __init__(self, file):

        self.submission_id = self.get_submission_id()
        self.submissions = []
        if zipfile.is_zipfile(file):
            self.process_zipfile(file)

    def process_zipfile(self, zfile):

        with ZipFile(zfile) as zip:

            file_names = [file for file in zip.namelist() if not file.endswith("/")]
            for file_name in file_names:
                    filetype = mimetypes.guess_type(file_name)[0]
                    if not file_name.__contains__("__MACOSX") and filetype == "text/plain":
                        print(file_name)
                        submission = Submission()
                        submission.submission_id = self.submission_id
                        submission.user_id = os.path.dirname(file_name)
                        if file_name.__contains__("MAC"):
                            print(submission.user_id)
                        submission.filename = os.path.basename(file_name)

                        file = zip.open(file_name)

                        submission.file_contents = file.read().decode('utf-8', "ignore")
                        if len(submission.file_contents) != 0:
                            self.submissions.append(submission)



    def get_submission_id(self):
        """
        :return: The increment of the current highest submission id
        """
        query = Submission.objects.order_by("-submission_id")

        return 0 if not query else query[0].submission_id + 1