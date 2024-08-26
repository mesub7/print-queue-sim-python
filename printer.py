import PySimpleGUI as sg

print = sg.cprint


class Printer:  # We are creating a new printer class.

    def __init__(self, print_speed, ID, logger):  # The constructor method.
        self.print_speed = print_speed
        self.ID = ID
        self.idle = True  # The printer is idle.
        self._current_job = None  # The printer is not printing anything.
        self.logger = logger

    def action(self, job):  # Does the actual 'printing'.
        self.current_job = job  # Set the printer's current job.
        job.EPT -= self.print_speed  # Does the 'printing' by subtracting the time left by the print speed.
        if job.EPT <= 0:  # If the time remaining is less than or equal to zero:
            print(f'INFO:\t Job with ID {job.ID} has completed.')  # Let the user know. # TODO: Change this once UI done.
            self.logger.log('c', 1)
            self.idle = True  # The printer is not busy anymore.

    @property
    def current_job(self):  # A pythonic getter method. This is exposed as current_job when the class is instantiated.
        return self._current_job

    @current_job.setter
    def current_job(self, job):  # A pythonic setter method.
        self._current_job = job
