from app.models import Submission
from lib.comparator import Comparator
from lib.UploadFileHandler import FileHandler
from lib.fingerprinter import Fingerprinter


class SubmissionController:
    # TODO: name files consistently
    def __init__(self, file):
        filehandler = FileHandler(file)
        submission_list = filehandler.submissions

        # fill out the fingerprints in the models
        for submission in submission_list:
            fingerprinter = Fingerprinter(submission.file_contents)
            submission.fingerprint = fingerprinter.fingerprint

        print("Generated fingerprints")
        Submission.objects.bulk_create(submission_list)
        print("Saved submissions to db")
        comparator = Comparator(submission_list)
        self.report = comparator.report
        print("Got report from comparator: {0}".format(self.report))