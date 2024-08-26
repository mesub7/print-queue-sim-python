from job import Job  # Acessing a class attribute.
from random import choice, randint


class Computer:

    SELECTION = [False, True]  # False is draft/greyscale, True is best/colour.
    PEOPLE = ['Staff', 'Student', 'Senior Student']  # The types of people that will be printing.
    ID = 0  # Used to uniquely identify each job.

    def __init__(self, interface):  # This is the constructor method.
        self.job_frequency = int(interface['AverageJobFrequency'])  # Use the frequency from the user settings.
        self._selected_random_num = randint(1, self.job_frequency)  # Used to decide if a job should be created or not.
        self.interface = interface  # Expose the interface to the class.

    def newjob(self, time):  # This decides if a new job should be created.
        chance = randint(1, self.job_frequency)   # Randomly pick a number for comparison.
        if chance == self._selected_random_num:  # If it matches (so a job is created)...
            quality_selector = choice(Computer.SELECTION)  # High quality or low quality.
            colour_selector = choice(Computer.SELECTION)  # Greyscale or Colour.
            person_selector = choice(Computer.PEOPLE)  # Student, Senior Student or Staff.
            pages = randint(int(self.interface['MinLength']), int(self.interface['MaxLength']))  # Number of pages job should have.
            Computer.ID += 1   # Increment ID by one.
            return Job(time, pages, quality_selector, colour_selector, person_selector, Computer.ID)  # Returns a Job object.
        return None  # No job is created.
