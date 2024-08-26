from computer import Computer
from job import Job
from logger import Logger
from printer import Printer
from print_queue import PriorityQueue, Queue


# External Libraries
import PySimpleGUI as sg
import time
import textwrap
from pathlib import Path

logger = Logger()  # Own Logger
sg.theme("DarkGrey9")  # Make it look somewhat nice...

# Shortcuts // Shadowing
text = sg.Text
button = sg.Button
print = sg.cprint
checkbox = sg.Checkbox
dropdown = sg.Combo
input = sg.Input
spinner = sg.Spin

accepted_combinations = ('Student', 'Staff', 'Senior Student',  # Accepted combinations in settings.
                         'Student Staff', 'Student Senior Student', 'Staff Senior Student')

with open('help_text.txt', 'r', encoding='utf-8') as t:  # Load in the help text.
    help_text_raw = t.read().splitlines()


def config():  # Create a link to access the settings from the INI file.
    settings = sg.UserSettings('pqs_config.ini', use_config_file=True, convert_bools_and_none=True, path=Path.cwd())
    return settings  # ^^^ INI format with some pythonic values automatically converted. ^^^


settings = config()
PRINT_QUEUE_INTERFACE = settings['Print Queue']  # Creating links to the different settings.
PRINTER_INTERFACE = settings['Printers']
JOB_INTERFACE = settings['Jobs']
global SIMULATION_INTERFACE  # Errors if line not included...
SIMULATION_INTERFACE = settings['Simulation']
output = '-ML_A-' + sg.WRITE_ONLY_KEY  # Unique ID for the printing queue.
X = sg.WIN_CLOSED  # Event that is generated if Windows 'X' is closed.
TAB = '\t'  # Formatting


def select_queue():  # Set which type of queue needs to be used.
    if PRINT_QUEUE_INTERFACE['PriorityQueue']:
        queue = PriorityQueue(int(PRINT_QUEUE_INTERFACE['QueueCapacity']), int(PRINT_QUEUE_INTERFACE['MaxAcceptedJobLength']),
                              int(PRINT_QUEUE_INTERFACE['MaxAcceptedRunningTime']), logger, PRINT_QUEUE_INTERFACE['PriorityJobCriteria'])
    else:
        queue = Queue(int(PRINT_QUEUE_INTERFACE['QueueCapacity']), int(PRINT_QUEUE_INTERFACE['MaxAcceptedJobLength']),
                      int(PRINT_QUEUE_INTERFACE['MaxAcceptedRunningTime']), logger)
    return queue


def prepare_text(logger):  # Preparing the text for display.
    logger.finalise()  # Finalise the values from the logger.
    text = f"""
    Statistics:
    Jobs Created:{logger.num_jobs:^48}
    {TAB}Of which accepted:{logger.accepted:^25}
    {TAB}Of which rejected:{logger.rejected:^26}
    {TAB}Of which completed:{logger.completed:^24}
    {TAB}Accepted:Rejected Ratio:{logger.ratio:^8}
    Average Waiting Time:{logger.average_waiting_time:12.1f} seconds
    Average Printing Time:{logger.average_printing_time:12.1f} seconds


    {logger.remaining_jobs if logger.remaining_jobs != 0 else 'No'} job(s) remain in the Queue.
    """
    return text


def simulation():  # The simulation function.
    generator = Computer(JOB_INTERFACE)  # What generates the jobs.
    printer = Printer(int(PRINTER_INTERFACE['PrintSpeed']), 1, logger)  # What does the 'printing'.
    simulation_layout = [[sg.Multiline(autoscroll=False, autoscroll_only_at_bottom=True, disabled=True, key=output, size=(200, 38), write_only=True, reroute_cprint=True, auto_refresh=True)],
                         [sg.Push(), button('End Simulation'), sg.Push()]]  # UI layout.
    queue = select_queue()  # Select which queue to use based on most recent settings
    Computer.ID = 0  # Needed to ensure statistics are accurate.
    Job.counter = 0  # " "
    logger.reset()  # " "
    sim_window = sg.Window('Simulation - Print Queue Simulator', simulation_layout, resizable=True, finalize=True)  # A UI window.
    sim_window.maximize()  # Maximise the window.
    running = True  # Begin looping
    while running:  # Keeps the window open...
        for currentSec in range(1, int(SIMULATION_INTERFACE['SimulationTime'])+1):  # Simulator Event Loop.
            event, values = sim_window.read(timeout=1)  # Waiting for a trigger for a second, otherwise continue.
            if currentSec == int(SIMULATION_INTERFACE['SimulationTime']) or event in (X, 'End Simulation'):  # If simulation closed by window or times up...
                logger.log('rj', queue.size)  # Log the number of jobs that remain in the queue.
                final_text = prepare_text(logger)  # Get the text ready for display by collating all the values.
                sg.popup(final_text, title='Statistics - PQS',
                         grab_anywhere=True, button_justification='centre')  # Popup with final text.
                running = False  # Not running the simulation anymore.
                sim_window.close()
                break  # End loop
            created_job = generator.newjob(currentSec)  # Create a new job.
            if created_job:  # If a new job has been created...
                queue.enqueue(created_job)  # Enqueue job, subject to conditions.
            if printer.idle and queue.size != 0:  # If printer idle and there's a job waiting...
                printer.idle = False  # No longer idle.
                job = queue.dequeue()  # Dequeue the job from the queue.
                logger.log('w', currentSec-job.time)  # Log that a job's been accepted.
                print(f'INFO:\t Job with ID {job.ID} is now printing.')  # Let user know.
                printer.action(job)  # Print part of the job.
            elif printer.idle and queue.size == 0:
                pass  # Maybe remove this or add a metric for printer idle time?
            else:
                job = printer.current_job  # Set the current
                printer.action(job)
            time.sleep(0.05)  # Don't want it to refresh too quickly.


def configuration():  # Where the settings are sorted. Optimise in future?
    layout = [  # All of the elements are defined here...
        [text('Settings:')],
        [text('Print Queue Management Options')],
        [text('Centralised Print Queue:'),
         checkbox('', key='Centralised', tooltip='Disable to have a print queue per printer.', disabled=True, default=PRINT_QUEUE_INTERFACE['Centralised'])],
        [text('Use Priority Queue:'),
         checkbox('', key='PriorityQueue', tooltip='Disable to ONLY have a standard queue.', default=PRINT_QUEUE_INTERFACE['PriorityQueue'])],
        [text('Priority Queue Criteria:'),
         dropdown(accepted_combinations, key='PriorityJobCriteria', readonly=True, default_value=PRINT_QUEUE_INTERFACE['PriorityJobCriteria'])],
        [text('Queue Capacity:'),
         spinner([x for x in range(1, 251)], tooltip='The maximum number of jobs the queue can handle.', key='QueueCapacity', initial_value=PRINT_QUEUE_INTERFACE['QueueCapacity'], size=(6, 10)), text('jobs')],
        [text('Maximum Acceptable Job Length:'),
         spinner([x for x in range(1, 101)], tooltip='The maximum length a job should be to be considered for printing.', key='MaxAcceptedJobLength', initial_value=PRINT_QUEUE_INTERFACE['MaxAcceptedJobLength'], size=(6, 10)), text('pages')],
        [text('Maximum Acceptable Job Running Time:'),
         spinner([x for x in range(1, 501)], tooltip='The maximum running time a job can be to be considered for printing.', key='MaxAcceptedRunningTime', initial_value=PRINT_QUEUE_INTERFACE['MaxAcceptedRunningTime'], size=(6, 10)), text('print-seconds')],
        [text('Printer Options')],
        [text('Number of Printers to use:'),
         spinner([x for x in range(1, 21)], tooltip='More printers allows jobs to be printed quicker.', key='NumberOfPrinters', initial_value=PRINTER_INTERFACE['NumberOfPrinters'], disabled=True, size=(6, 10)), text('printers')],
        [text('Print Speed:'),
         spinner([x for x in range(1, 101)], tooltip='A higher print speed will mean jobs are printed quicker.', key='PrintSpeed', initial_value=PRINTER_INTERFACE['PrintSpeed'], size=(6, 10)), text('print-seconds')],
        [text('Job Settings')],
        [text('Minimum and Maximum Job Length:'),
         spinner([x for x in range(1, 100)], tooltip='Shortest length that will be automatically generated.', key='MinLength', initial_value=JOB_INTERFACE['MinLength'], size=(6, 10)), text('-'),
         spinner([x for x in range(1, 200)], tooltip='Longest length that will be automatically generated.', key='MaxLength', initial_value=JOB_INTERFACE['MaxLength'], size=(6, 10)), text('pages')],
        [text('Job Frequency:'),
         spinner([x for x in range(1, 3601)], tooltip='A job will be produced every n seconds, on average.', key='AverageJobFrequency', initial_value=JOB_INTERFACE['AverageJobFrequency'], size=(6, 10)), text('seconds')],
        [text('Simulation Settings')],
        [text('Simulation Runtime:'),
         spinner([x for x in range(1, 7201)], tooltip='Number of iteration the simulation should do.', key='SimulationTime', initial_value=SIMULATION_INTERFACE['SimulationTime'], size=(6, 10)), text('iterations')],
        [sg.Push(), button('OK'), button('Cancel'), sg.Push()]
              ]
    window = sg.Window('Settings - Print Queue Simulator', layout=layout)  # Make the window.
    configuring = True
    while configuring:  # Looping
        events, values = window.read()  # See if the user has put anything.
        if events in ('Cancel', X):  # They have exited without saving...
            configuring = False
            window.close()
            break
        if events == 'OK':  # Begin the save proces...
            for key in values:
                if values[key] == '0':  # Catching ZeroDivision Errors.
                    sg.popup(f'Setting {key} failed to save due to being a invalid value. It must be a whole, non-zero number.', title='For your information')
                    continue  # Next please!
                if key in ('Centralised', 'PriorityQueue', 'PriorityJobCriteria'):
                    PRINT_QUEUE_INTERFACE.set(key, values[key])
                if key in ('QueueCapacity', 'MaxAcceptedJobLength', 'MaxAcceptedRunningTime'):
                    try:
                        PRINT_QUEUE_INTERFACE.set(key, abs(int(values[key])))
                    except ValueError:  # Needs to be an integer.
                        sg.popup(f'Setting {key} failed to save due to being an invalid value. It must be a whole number.', title='For your information')
                if key in ('NumberOfPrinters', 'PrintSpeed'):
                    try:
                        PRINTER_INTERFACE.set(key, abs(int((values[key]))))
                    except ValueError:
                        sg.popup(f'Setting {key} failed to save due to being a invalid value. It must be a whole number.', title='For your information')
                if key in ('MinLength', 'MaxLength', 'AverageJobFrequency'):
                    try:
                        JOB_INTERFACE.set(key, abs(int(values[key])))
                    except ValueError:
                        sg.popup(f'Setting {key} failed to save due to being a invalid value. It must be a whole number.', title='For your information')
                if key in ('SimulationTime'):
                    try:
                        SIMULATION_INTERFACE.set(key, abs(int(values[key])))
                    except ValueError:
                        sg.popup(f'Setting {key} failed to save due to being a invalid value. It must be a whole number.')
            if JOB_INTERFACE['MaxLength'] < JOB_INTERFACE['MinLength']:
                temp = JOB_INTERFACE['MaxLength']
                JOB_INTERFACE.set('MaxLength', int(JOB_INTERFACE['MinLength']))
                JOB_INTERFACE.set('MinLength', int(temp))
                sg.Popup('MinLength was detected to be larger than MaxLength and so these have been swapped.', title='For your information:')
            sg.Popup('Settings Saved Successfully!', title='Success!')
            configuring = False
            window.close()
            break


def make_home_window():  # Home menu...
    home_layout = [[text('Welcome to the Print Queue Simulator!')],
                   [button('Start Simulation'), button('Help'), button('Settings'), button('Exit')]]

    return sg.Window('Print Queue Simulator', home_layout, finalize=True)


def make_help_window():  # Help menu.
    wrapper = textwrap.TextWrapper(width=100)  # Ensures window isn't too wide.
    col_layout = []
    for help_text in help_text_raw:
        help_text = '\n'.join(wrapper.wrap(help_text))
        col_layout.append([text(help_text)])
    help_layout = [[sg.Column(col_layout, scrollable=True, vertical_scroll_only=True, pad=(0, 0))]]
    return sg.Window('Help - Print Queue Simulator', layout=help_layout, resizable=False, finalize=True, size=(650, 400))


def main():  # Main function.
    help_window = None
    simulation_window = None
    settings_window = None
    running = True
    while running:
        home_window = make_home_window()
        window, event, values = sg.read_all_windows()
        if event in (X, 'Exit'):  # if user closes window or clicks Exit
            running = False
            break
        if event == 'Start Simulation' and not simulation_window:
            simulation_window = simulation()
            home_window.close()
            simulation_window = None
        if event == 'Help' and not help_window:
            help_window = make_help_window().read()
            home_window.close()
            help_window = None
        if event == 'Settings' and not settings_window:
            settings_window = configuration()
            home_window.close()
            settings_window = None


main()
