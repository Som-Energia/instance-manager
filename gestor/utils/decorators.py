import asyncio

LOOP_WAIT = 2


def loop(func):
    async def looped(*args):
        while True:
            await func(*args)
            await asyncio.sleep(LOOP_WAIT)

    return looped
