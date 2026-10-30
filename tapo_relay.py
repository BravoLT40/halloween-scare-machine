import asyncio
from aiohttp import web
import tapo

client = tapo.ApiClient('billyosborn@gmail.com', 'Kalamazoo44!')
plug = None

async def handle_on(request):
    global plug
    try:
        if not plug:
            plug = await client.p125('192.168.1.105')
        await plug.on()
        return web.Response(text='ON')
    except Exception as e:
        plug = None
        return web.Response(text=f'ERR: {e}', status=500)

async def handle_off(request):
    global plug
    try:
        if not plug:
            plug = await client.p125('192.168.1.105')
        await plug.off()
        return web.Response(text='OFF')
    except Exception as e:
        plug = None
        return web.Response(text=f'ERR: {e}', status=500)

async def app_factory():
    global plug
    print('Connecting to Tapo plug...')
    plug = await client.p125('192.168.1.105')
    print('Plug connected!')
    app = web.Application()
    app.router.add_get('/on', handle_on)
    app.router.add_get('/off', handle_off)
    return app

if __name__ == '__main__':
    web.run_app(app_factory(), host='127.0.0.1', port=8088)
