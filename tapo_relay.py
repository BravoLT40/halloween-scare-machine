import asyncio
from aiohttp import web
import tapo

client = tapo.ApiClient('billyosborn@gmail.com', 'Kalamazoo44!')
plug = None

async def handle_on(request):
    global plug
    if not plug:
        plug = await client.p125('192.168.1.105')
    await plug.on()
    return web.Response(text='ON')

async def handle_off(request):
    global plug
    if not plug:
        plug = await client.p125('192.168.1.105')
    await plug.off()
    return web.Response(text='OFF')

app = web.Application()
app.router.add_get('/on', handle_on)
app.router.add_get('/off', handle_off)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8088)
