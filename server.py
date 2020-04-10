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
import asyncio,time,logging,signal
from functools import partial
from tornado.platform.asyncio import AsyncIOMainLoop
from aioelasticsearch import Elasticsearch

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    AsyncIOMainLoop().install()
except:
    pass

#import logging
#logging.getLogger().setLevel(logging.DEBUG)

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

def sig_handler(app,sig,frame):
    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(deadline):
        now = time.time()
        if now < deadline:
            logging.info('Waiting for next tick')
            io_loop.call_later(1, stop_loop,deadline)
        else:
            if len(asyncio.Task.all_tasks(io_loop)) == 0:
                io_loop.stop()
                logging.info('Shutdown finally')

    def shutdown():
        logging.info('Stopping http server')
        server = tornado.httpserver.HTTPServer(app)
        server.stop()
        logging.info('Will shutdown in %s seconds ...',
                     MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        stop_loop(time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)

    io_loop.add_callback_from_signal(shutdown)
async def get_dbs():
    dbs={}
    async for x in news_mongo_db.settings.find():
        db = motor.motor_tornado.MotorClient(config.mongo['url'],maxPoolSize=200)[x['db']]
        x['db_conn'] = db
        if x['es_db'] != "no":
            x['es_conn'] =  Elasticsearch(host=x['es_db'],retry_on_timeout=True,loop=loop)
        dbs[x['domain']] = x
    return dbs

if __name__ == "__main__":
    #asyncio.set_event_loop(asyncio.new_event_loop())
    #db = motor.motor_tornado.MotorClient(config.mongo['url'],maxPoolSize=200,readPreference='secondaryPreferred')[config.mongo['db_name']]
    news_mongo_db = motor.motor_tornado.MotorClient(config.mongo['url'],maxPoolSize=200)['news_mongo']
    loop = asyncio.get_event_loop()
    dbs = IOLoop.current().run_sync(get_dbs)
    #cron = cron(db)
    #scheduler = TornadoScheduler()
    #scheduler = AsyncIOScheduler()
    #scheduler.add_job(cron.count_category, 'interval', seconds=300)
    #scheduler.add_job(cron.count_category, 'date', run_date=datetime(2018, 8, 17, 4, 54, 0))
    #scheduler.start()
    app = Application(dbs)
    if config.env == 'dev':
        app.listen(80)
    elif config.env == 'test':
        app.listen(sys.argv[1])
    elif config.env == 'production':
        app.listen(sys.argv[1])
    signal.signal(signal.SIGTERM, partial(sig_handler, app))
    signal.signal(signal.SIGINT, partial(sig_handler, app))
    app.init_with_loop(loop)
    #loop.set_blocking_log_threshold(0.5)
    loop.run_forever()

