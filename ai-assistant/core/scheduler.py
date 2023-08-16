from asyncio import Queue, create_task

from .gen import generator
from .classes import Input, Output

async def infinite_loop(in_queue: Queue):
    while True:
        (input, out_queue) = await in_queue.get()
        output = generator(input)
        await out_queue.put(output)

class Scheduler:
    def __init__(self):
        self.in_queue = Queue()

    def start(self):
        self.task = create_task(infinite_loop(self.in_queue))

    def stop(self):
        self.task.cancel()

    async def process(self, input: Input) -> Output:
        out_queue = Queue()
        await self.in_queue.put((input, out_queue))
        return await out_queue.get()
