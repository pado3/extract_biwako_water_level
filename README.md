# extract_biwako_water_level
Extract lake Biwa water level data from MILT database

usage:<br />
mkdir _bl_data<br />
pip install beautifulsoup4, pandas, python-dateutil<br />

get csv data from MILT database:<br />
python3 bl.py start [finish]<br />
 ex1. python3 bl.py 199301 202604<br />
 ex2. python3 bl.py 202604<br />

extract specified date and hour data from CSV file:<br />
python3 ebl.py MMDD HH<br />
 ex. python3 ebl.py 0424 09<br />

For more information, please refer to my Japanese blog:<br />
https://pado.tea-nifty.com/top/2026/04/post-f2a39e.html<br />
