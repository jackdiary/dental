#!/usr/bin/env python
"""
실제 네이버 플레이스 리뷰 크롤러 (실제 링크 기반)
제공된 네이버 플레이스 링크에서 실제 리뷰를 크롤링합니다.
"""
import os
import sys
import django
import time
import random
import requests
from selenium import web