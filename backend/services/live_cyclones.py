"""Real-time tropical cyclone feed with a GDACS API + RSS fallback."""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from typing import Any
import requests
GDACS_URL=("https://www.gdacs.org/gdacsapi/api/events/geteventlist/MAP?eventtype=TC")
GDACS_RSS_URL="https://data.gdacs.org/xml/rss_tc_7d.xml"
INDIAN_OCEAN_BBOX=(35.0,-5.0,110.0,35.0)
HEADERS={"User-Agent":"CycloneShieldAI/3.0 (disaster-risk research)"}

def _number(value: Any):
    try:
        n=float(value); return n if n==n else None
    except (TypeError,ValueError): return None

def _properties(feature: dict)->dict:
    p=feature.get("properties"); return p if isinstance(p,dict) else {}

def _point(feature: dict):
    geometry=feature.get("geometry") or {}; coords=geometry.get("coordinates")
    if isinstance(coords,list) and len(coords)>=2:
        lon,lat=_number(coords[0]),_number(coords[1])
        if lon is not None and lat is not None: return lat,lon
    p=_properties(feature); lat=_number(p.get("lat") or p.get("latitude")); lon=_number(p.get("lon") or p.get("longitude"))
    return (lat,lon) if lat is not None and lon is not None else None

def _severity(props:dict)->str:
    raw=str(props.get("episodealertlevel") or props.get("alertlevel") or props.get("severity") or "unknown").lower()
    if raw in {"red","orange","green","yellow"}: return raw
    if raw in {"3","high"}: return "red"
    if raw in {"2","medium"}: return "orange"
    if raw in {"1","low"}: return "yellow"
    return "unknown"

def _filter_events(raw_features:list[dict],source:str,source_url:str)->dict:
    west,south,east,north=INDIAN_OCEAN_BBOX; events=[]
    for feature in raw_features:
        if not isinstance(feature,dict): continue
        point=_point(feature)
        if point is None: continue
        lat,lon=point
        if not(south<=lat<=north and west<=lon<=east): continue
        props=_properties(feature)
        events.append({"id":props.get("eventid") or props.get("eventId") or feature.get("id"),"name":props.get("name") or props.get("eventname") or "Unnamed tropical cyclone","latitude":lat,"longitude":lon,"severity":_severity(props),"alert_level":props.get("alertlevel"),"event_type":props.get("eventtype") or "TC","country":props.get("country"),"from_date":props.get("fromdate"),"to_date":props.get("todate"),"modified":props.get("datemodified"),"source":source,"source_url":source_url})
    return {"source":source,"source_url":source_url,"coverage":{"west":west,"south":south,"east":east,"north":north},"count":len(events),"events":events}

def _xml_child_text(node:ET.Element,local_names:set[str])->str|None:
    for child in list(node):
        if child.tag.rsplit("}",1)[-1].lower() in local_names and child.text: return child.text.strip()
    return None

def _parse_rss(content:bytes)->list[dict]:
    root=ET.fromstring(content); features=[]
    for item in root.iter():
        if item.tag.rsplit("}",1)[-1].lower()!="item": continue
        title=_xml_child_text(item,{"title"}) or "Unnamed tropical cyclone"
        guid=_xml_child_text(item,{"guid","id"}); pub_date=_xml_child_text(item,{"pubdate","updated","datemodified"}); description=_xml_child_text(item,{"description","summary"}) or ""; point_text=_xml_child_text(item,{"point"}); lat=lon=None
        if point_text:
            nums=re.findall(r"[-+]?\d+(?:\.\d+)?",point_text)
            if len(nums)>=2: lat,lon=_number(nums[0]),_number(nums[1])
        if lat is None or lon is None:
            nums=re.findall(r"[-+]?\d{1,3}\.\d+",description)
            if len(nums)>=2: lat,lon=_number(nums[0]),_number(nums[1])
        props={"eventid":guid,"name":title,"datemodified":pub_date,"description":description}
        level=re.search(r"alert(?:level)?\s*[:=]\s*(red|orange|yellow|green)",description,re.I)
        if level: props["alertlevel"]=level.group(1)
        if lat is not None and lon is not None: features.append({"id":guid,"geometry":{"coordinates":[lon,lat]},"properties":props})
    return features

def get_live_cyclones(timeout:int=8)->dict:
    api_error=None
    try:
        r=requests.get(GDACS_URL,headers=HEADERS,timeout=timeout); r.raise_for_status(); payload=r.json(); features=payload.get("features",[]) if isinstance(payload,dict) else []
        if not isinstance(features,list): raise ValueError("GDACS returned an invalid feature collection")
        return _filter_events(features,"GDACS API",GDACS_URL)
    except Exception as exc: api_error=exc
    try:
        r=requests.get(GDACS_RSS_URL,headers=HEADERS,timeout=timeout); r.raise_for_status(); result=_filter_events(_parse_rss(r.content),"GDACS RSS",GDACS_RSS_URL); result["fallback_used"]=True; result["api_error"]=str(api_error); return result
    except Exception as rss_exc:
        west,south,east,north=INDIAN_OCEAN_BBOX
        return {"source":"GDACS API + RSS","source_url":GDACS_RSS_URL,"coverage":{"west":west,"south":south,"east":east,"north":north},"count":0,"events":[],"available":False,"fallback_used":True,"error":f"GDACS API unavailable: {api_error}; RSS unavailable: {rss_exc}"}
