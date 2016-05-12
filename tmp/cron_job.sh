#!/bin/bash
cd /root/projects/scrapy-spiders/lj
scrapyd-deploy -p lj_pudong
#sleep 60
curl http://localhost:6800/schedule.json -d project=lj_pudong -d spider=lj_ny
