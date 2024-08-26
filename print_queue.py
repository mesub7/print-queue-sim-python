import PySimpleGUI as sg

print = sg.cprint


class Queue:

    def __init__(self, capacity, max_length, max_time, logger):
        self.size = 0  # This measures how many jobs are in the queue at any given moment.
        self.front = self.rear = -1  # Will be changed later.
        self.jobs = [None]*capacity  # Setting up the actual implementation of the queue, based on size.
        self.capacity = capacity  # The max number of jobs the queue can hold.
        self.max_length = max_length  # The maximum (poge) length of a job before it MUST be rejected.
        self.max_time = max_time  # The maximum EPT that a job should have before it MUST be rejected.
        self.logger = logger

    def isFull(self):  # Function to check if the queue is full or not.
        return self.size == self.capacity

    def isEmpty(self):  # Function to check if the queue is empty or not.
        return self.size == 0

    def enqueue(self, job):  # Add a job to the queue, if eligibile.
        if self.isFull():  # If the queue is full...
            self.logger.log('r', 1)  # Log (stats based) that the job has been rejected.
            return print(f'ERROR:\t Queue full. Job with ID {job.ID} failed to enqueue.')
        elif job.pages > self.max_length:  # Too large of a job. BLOCKED.
            self.logger.log('r', 1)
            return print(f'ERROR:\t Page Length of job {job.ID} [{job.pages}] exceeds max length allowed by queue [{self.max_length}]).')
        elif job.EPT > self.max_time:  # Job is too time expensive. BLOCKED.
            self.logger.log('r', 1)
            return print(f'ERROR:\t Estimated time to print job {job.ID} [{job.EPT} secs] exceeds maximum continous printing time [{self.max_time} secs]')
        elif self.front == -1:  # Adding a job for the very first time.
            self.front = self.rear = 0
            self.jobs[self.rear] = job
            self.size += 1  # Increasing the size of the queue.
        else:  # For most cases.
            self.rear = (self.rear + 1) % self.capacity  # Looping back round if needed.
            self.jobs[self.rear] = job  # Placing the job at the end of the queue.
            self.size += 1  # Increasing the size of the queue.
        self.logger.log('a', 1)
        self.logger.log('l', job.pages)
        self.logger.log('p', job.EPT)
        return print(f'INFO:\t Job with ID {job.ID} added to queue.')

    def dequeue(self):  # Removing a job from the queue.
        if self.isEmpty():  # If the queue is empty.
            return print('Error: Queue empty: no job to remove.')
        elif self.front == self.rear:  # If it's the only job in the queue.
            job = self.jobs[self.front]
            self.front = self.rear = -1  # Reset to inital state.
            self.size = 0  # The queue is empty...
            print(f'INFO:\t Job with ID {job.ID} removed from queue - sent to printer.')
            return job
        else:  # Most other cases.
            job = self.jobs[self.front]
            self.front = (self.front + 1) % self.capacity  # Again, looping back round if needed.
            print(f'INFO:\t Job with ID {job.ID} removed from queue - sent to printer.')
            self.size -= 1  # Reduce the size of the queue by one.
            return job

    def queue_front(self):  # For the end of the simulation.
        if self.isEmpty():  # Checking the queue.
            print('This queue is empty.')
        else:
            print(f'The front of the queue is: {self.jobs[self.front]}.')

    def queue_rear(self):  # For the end of the simulation.
        if self.isEmpty():  # Checking the queue.
            print('This queue is empty.')
        else:
            print(f'The rear of the queue is: {self.jobs[self.rear]}')


class PriorityQueue(Queue):  # Inherits most of the attributes and methods from the main class, with some overriding.

    def __init__(self, capacity, max_length, max_time, logger, criteria):
        super().__init__(capacity, max_length, max_time, logger)
        self.priority_queue = []  # NEW to priority queue.
        self.criteria = criteria  # NEW to priority queue.

    def enqueue(self, job):  # Enquing with priority checks. Todo: If there's time, move the checking function to one place so it isn't repeated.
        if job.pages > self.max_length:  # Too large of a job. BLOCKED.
            self.logger.log('r', 1)
            return print(f'ERROR:\t Page Length of job {job.ID} [{job.pages}] exceeds max length allowed by queue [{self.max_length}].')
        elif job.EPT > self.max_time:  # Job is too time expensive. BLOCKED.
            self.logger.log('r', 1)
            return print(f'ERROR:\t Estimated time to print job {job.ID} [{job.EPT} secs] exceeds maximum continous printing time [{self.max_time} secs].')
        elif job.type in self.criteria:  # TODO: Change this to import from settings.
            self.priority_queue.append(job)  # Added to priority queue.
            self.logger.log('a', 1)
            self.logger.log('l', job.pages)
            return print(f'INFO:\t Job with ID {job.ID} added to priority queue.')
        else:
            super().enqueue(job)  # Continue the process to add to the standard queue.

    def dequeue(self):
        if self.priority_queue:  # Check the priority queue first.
            job = self.priority_queue.pop(0)
            print(f'INFO:\t Job with ID {job.ID} removed from priority queue - sent to printer.')
            return job
        else:
            return super().dequeue()  # Continue the standard process to add to the queue.

    def queue_front(self):  # For the end of the simulation.
        if not self.priority_queue:  # Checking the queue.
            print('This priority queue is empty.')
        else:
            print(f'The front of the priority queue is: {self.priority_queue[0]}.')
        super().queue_front()  # Get the normal queue info as well.

    def queue_rear(self):  # For the end of the simulation.
        if not self.priority_queue:  # Checking the queue.
            print('This priority queue is empty.')
        else:
            print(f'The rear of the priority queue is: {self.priority_queue[-1]}.')
        super().queue_rear()  # Get the normal queue info as well.
