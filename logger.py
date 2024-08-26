import math
from job import Job  # we need to access a class attribute.


class Logger:
    def __init__(self):
        self.accepted = 0  # Number of accepted jobs (into the queue).
        self.completed = 0  # Number of jobs that have finished printing.
        self.job_length = 0  # Aggregate job length.
        self.job_lengths = []  # The raw lengths of the job pages.
        self.num_jobs = 0  # Total number of jobs.
        self.printing_time = 0  # Aggregate printing time.
        self.printing_times = []  # Raw data of time taken to print job.
        self.ratio = ""  # The ratio of accepted jobs to rejected jobs in x:y format.
        self.rejected = 0  # Number of rejected jobs (into the queue).
        self.remaining_jobs = 0  # The number of jobs that were remaining.
        self.waiting_time = 0  # Aggregate waiting time.
        self.waiting_times = []  # Raw data of waiting times.

    def log(self, type, data):
        """Method to start collating statistics about the simulation.
        Codes:
        a: Accepted.
        c: Completed.
        l: Job Length.
        p: Estimated Printing Time (directly from job).
        r: Rejected.
        rj: Remaining Jobs.
        w: Waiting Time (Current time - created time).
        :param str type: One of the codes (a, p, r or w).
        """
        if type == 'a':  # A is for accepted
            self.accepted += data
        elif type == 'c':
            self.completed += data
        elif type == 'l':
            self.job_lengths.append(data)
        elif type == 'p':
            self.printing_times.append(data)
        elif type == 'r':
            self.rejected += data
        elif type == 'rj':
            self.remaining_jobs = data
        elif type == 'w':
            self.waiting_times.append(data)

    def finalise(self):  # Generating all of the statistics for returning to the main program.
        self.num_jobs = Job.counter  # Get the number of print jobs created overall.
        if not self.num_jobs:  # 0 is False Pythonically.
            self.average_waiting_time = self.average_printing_time = 0
            self.ratio = f'{None}'
        else:
            self.waiting_time = sum(self.waiting_times)  # Combine all of the waiting times together.
            self.average_waiting_time = self.waiting_time / self.num_jobs  # Average waiting time for a job.
            self.printing_time = sum(self.printing_times)  # Combining all of the printing times.
            self.average_printing_time = self.printing_time / self.num_jobs  # Average time that a job was printing for.
            divisor = math.gcd(self.accepted, self.rejected)  # Find the greatest common divisor so that the ratio is as simplified as possible.
            self.ratio = f"{int(self.accepted/divisor)}:{int(self.rejected/divisor)}"  # The actual ratio. a:b

    def reset(self):
        self.__init__()
