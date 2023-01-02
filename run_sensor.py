import asyncio
import concurrent
from threading import Thread, active_count
from dax.hal_mlb import HAL_MLB

LED_TYPE_WHITE = 2
hardware_loop = None


async def show_threads_tasks():
    try:
        while True:
            print(f"Threads: {active_count()}, tasks: {len(asyncio.all_tasks())}")
            await asyncio.sleep(5)
    except asyncio.exceptions.CancelledError:
        pass


async def show_sensor_light(hal_mlb: HAL_MLB):
    try:
        while True:
            if hal_mlb.is_functioning:
                print(f"ALS level: {hal_mlb.light_sensor_get_ambient_light()}")
                await asyncio.sleep(3)
            pass
    except asyncio.exceptions.CancelledError:
        pass


async def update_light_percent(hal_mlb: HAL_MLB, queue: asyncio.Queue):
    try:
        while True:
            light_percent = await queue.get()
            hal_mlb.leds_all_set(LED_TYPE_WHITE, light_percent)
            print(f"Updated light to {light_percent}%")
    except asyncio.exceptions.CancelledError:
        pass


async def stop_task_threadsafe():
    for task in asyncio.all_tasks(hardware_loop):
        task.cancel()


def stop_tasks():
    """Coroutine thread safe"""
    print("Stopping tasks")
    try:
        if hardware_loop is not None:
            future = asyncio.run_coroutine_threadsafe(
                coro=stop_task_threadsafe(), loop=hardware_loop
            )
            future.result()
    except concurrent.futures._base.CancelledError:  # type: ignore
        pass


def hardware_entrypoint(queue):
    hal_mlb = HAL_MLB()
    hal_mlb.leds_all_set(LED_TYPE_WHITE, 0)
    global hardware_loop
    hardware_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(hardware_loop)
    hardware_loop.run_until_complete(
        asyncio.gather(
            show_sensor_light(hal_mlb), show_threads_tasks(), update_light_percent(hal_mlb, queue)
        )
    )


async def main():
    light_percent_queue = asyncio.Queue(maxsize=10)
    hardware_thread = Thread(target=hardware_entrypoint, args=[light_percent_queue])
    hardware_thread.start()
    try:
        while True:
            desired_light_percent = input("Enter Desired Light Percent: \n")
            await light_percent_queue.put(int(desired_light_percent))
    except KeyboardInterrupt:
        stop_tasks()
        hardware_thread.join()
        print("Program Ended")


if __name__ == "__main__":
    asyncio.run(main())
