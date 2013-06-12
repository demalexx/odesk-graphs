odesk-graphs
============

Shows graphs about working on oDesk. Included graphs:

- Workload by days;
- Workload by weeks;
- Workload by months;
- Earnings by weeks;
- Earnings by months;
- Total workload by teams;
- Total earnings by teams.

odesk-graphs is a small web-server with few pages. Just run `odesk-graphs.py` and open `http://127.0.0.1:8080/` in browser.

To be able to see graphs first you need to create API keys and authorize odesk-graphs. There is setup page where you could do configuration.

Sample graphs page:

![](https://raw.github.com/demalexx/odesk-graphs/master/docs/sample.png)

Requirements:

- [bottle](http://bottlepy.org/docs/dev/);
- [Highcharts](http://www.highcharts.com/) (included);
- [jQuery Datepicker](http://keith-wood.name/datepick.html) (included).

Notes:

Original [odesk-python](https://github.com/odesk/python-odesk) library doesn't work, patched `odesk` library is included.