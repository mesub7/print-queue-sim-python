import PySimpleGUI as sg

print = sg.cprint  # Override the default print function to use PySimpleGUI's output function.


class Job:
    counter = 0  # This will count how many jobs have been created.

    def __init__(self, time, pages, quality, colour, type, ID):  # This is the constructor method.
        Job.counter += 1  # This increases the job counter by one.
        self.time, self.pages, self.quality, self.colour, self.type, self.ID, self.EPT = self.create(time, pages, quality, colour, type, ID)  # Assigns all the different attributes of the class from the output of the create method.

    def __str__(self):  # Magic string method.
        return f'Job with ID {self.ID}'

    def create(self, time, pages, quality, colour, type, ID):  # This uses some of the attributes to calculate further attributes of the Job class.
        scaling = 2 if quality else 1  # Increases the time it takes to print a job if it wants to print in a higher quality.
        quality = 'high' if quality else 'draft'  # High Quality Job if True
        colour = 'Colour' if colour else 'Greyscale'  # Colour Job if True
        EPT = pages * scaling * 6  # 6 is a preliminary value.
        print(f'NOTE:\t {colour} print job created at {time} seconds by {type}. '  # Improve readability
              f'\tPrinting {pages} pages in {quality} quality. Printing time: {EPT} seconds. '
              f'\tJob ID: {ID}')
        return time, pages, quality, colour, type, ID, EPT  # Return all values to be set as attributes.
