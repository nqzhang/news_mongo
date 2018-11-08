import sys
from tornado.ioloop import IOLoop
import tornado
from app import Application
import motor.motor_tornado
import config
from tornado.httpserver import HTTPServer
from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from cron import cron
import asyncio
from tornado.platform.asyncio import AsyncIOMainLoop
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    AsyncIOMainLoop().install()
except:
    pass

if __name__ == "__main__":
    #asyncio.set_event_loop(asyncio.new_event_loop())
    db = motor.motor_tornado.MotorClient(config.mongo['url'],maxPoolSize=200,readPreference='secondaryPreferred')[config.mongo['db_name']]
    #cron = cron(db)
    #scheduler = TornadoScheduler()
    #scheduler = AsyncIOScheduler()
    #scheduler.add_job(cron.count_category, 'interval', seconds=300)
    #scheduler.add_job(cron.count_category, 'date', run_date=datetime(2018, 8, 17, 4, 54, 0))
    #scheduler.start()
    app = Application(db)
    app.listen(48000)
    loop = asyncio.get_event_loop()
    app.init_with_loop(loop)
    #loop.set_blocking_log_threshold(0.5)
    loop.run_forever()
