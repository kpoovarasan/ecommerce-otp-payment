"""SQLAlchemy Models + 105-product seed — NexusShop"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

def _img(pid): return f"https://images.unsplash.com/{pid}?w=700&q=80"
def _imgs(*pids): return json.dumps([_img(p) for p in pids])
def _h(*args): return json.dumps(list(args))
def _s(**kw):  return json.dumps(kw)

# ── Models ────────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    phone=db.Column(db.String(15))
    password=db.Column(db.String(256),nullable=False)
    address=db.Column(db.Text)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    def set_password(self,p): self.password=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password,p)
    def to_dict(self): return {"id":self.id,"name":self.name,"email":self.email,"phone":self.phone,"address":self.address}

class Product(db.Model):
    __tablename__ = "products"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    brand=db.Column(db.String(60),default="NexusShop")
    category=db.Column(db.String(60),nullable=False)
    price=db.Column(db.Float,nullable=False)
    original_price=db.Column(db.Float)
    description=db.Column(db.Text)
    highlights=db.Column(db.Text)
    specs_json=db.Column(db.Text)
    image_url=db.Column(db.Text)
    images_json=db.Column(db.Text)
    image_emoji=db.Column(db.String(10),default="📦")
    image_color=db.Column(db.String(20),default="#6366f1")
    stock=db.Column(db.Integer,default=50)
    rating=db.Column(db.Float,default=4.5)
    reviews=db.Column(db.Integer,default=100)
    badge=db.Column(db.String(30))
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    @property
    def highlights_list(self): return json.loads(self.highlights) if self.highlights else []
    @property
    def specs(self): return json.loads(self.specs_json) if self.specs_json else {}
    @property
    def gallery(self): return json.loads(self.images_json) if self.images_json else []
    def to_dict(self):
        disc=int((1-self.price/self.original_price)*100) if self.original_price else 0
        return {"id":self.id,"name":self.name,"brand":self.brand,"category":self.category,
                "price":self.price,"original_price":self.original_price,"description":self.description,
                "image_url":self.image_url,"image_emoji":self.image_emoji,"image_color":self.image_color,
                "stock":self.stock,"rating":self.rating,"reviews":self.reviews,"badge":self.badge,"discount":disc}

class Order(db.Model):
    __tablename__ = "orders"
    id=db.Column(db.Integer,primary_key=True)
    order_id=db.Column(db.String(20),unique=True,nullable=False)
    customer_name=db.Column(db.String(120),nullable=False)
    customer_email=db.Column(db.String(120),nullable=False)
    customer_phone=db.Column(db.String(15),nullable=False)
    address=db.Column(db.Text,nullable=False)
    payment_method=db.Column(db.String(30),nullable=False)
    payment_detail=db.Column(db.String(120))
    items_json=db.Column(db.Text,nullable=False)
    subtotal=db.Column(db.Float,nullable=False)
    tax=db.Column(db.Float,nullable=False)
    total=db.Column(db.Float,nullable=False)
    status=db.Column(db.String(30),default="Confirmed")
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    @property
    def items(self):
        try: return json.loads(self.items_json) if self.items_json else []
        except: return []
    def to_dict(self):
        return {"order_id":self.order_id,"customer_name":self.customer_name,
                "customer_email":self.customer_email,"customer_phone":self.customer_phone,
                "address":self.address,"payment_method":self.payment_method,
                "payment_detail":self.payment_detail,"items":self.items,
                "subtotal":self.subtotal,"tax":self.tax,"total":self.total,
                "status":self.status,"created_at":self.created_at.isoformat()}

class Review(db.Model):
    __tablename__ = "reviews"
    id=db.Column(db.Integer,primary_key=True)
    product_id=db.Column(db.Integer,db.ForeignKey("products.id"),nullable=False)
    user_name=db.Column(db.String(80),nullable=False)
    rating=db.Column(db.Integer,nullable=False)
    title=db.Column(db.String(120))
    body=db.Column(db.Text)
    verified=db.Column(db.Boolean,default=False)
    helpful=db.Column(db.Integer,default=0)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    def to_dict(self):
        return {"id":self.id,"user_name":self.user_name,"rating":self.rating,
                "title":self.title,"body":self.body,"verified":self.verified,
                "helpful":self.helpful,"created_at":self.created_at.strftime("%d %b %Y")}

class Wishlist(db.Model):
    __tablename__ = "wishlists"
    id=db.Column(db.Integer,primary_key=True)
    session_id=db.Column(db.String(60),nullable=False)
    product_id=db.Column(db.Integer,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

# ── Seed Data ─────────────────────────────────────────────────────────────────

SEED_PRODUCTS = [
# ── ELECTRONICS ───────────────────────────────────────────────────────────────
dict(name="Wireless Noise-Cancelling Headphones",brand="SoundMax",category="Electronics",
     price=2499,original_price=4999,stock=45,rating=4.8,reviews=2341,badge="Bestseller",
     image_emoji="🎧",image_color="#6366f1",
     description="Studio-quality audio with industry-leading ANC, 40mm dynamic drivers, and 30-hour battery life. Foldable and perfect for travel, work, or home.",
     highlights=_h("ANC blocks 99% of ambient sound","30-hour battery (ANC on), 40-hour (ANC off)","40mm Hi-Res Audio certified drivers","Bluetooth 5.3 multipoint — connect 2 devices","Quick charge: 10 min = 3 hrs playback","Foldable with premium carry case"),
     specs_json=_s(Brand="SoundMax",Driver="40mm Dynamic",Connectivity="Bluetooth 5.3",Battery="30/40 hrs",Charging="USB-C 10min=3hrs",Weight="248g",Colors="Black, White, Navy",Warranty="1 Year"),
     image_url=_img("photo-1505740420928-5e560c06d30e"),
     images_json=_imgs("photo-1524678606370-a47ad25cb82a","photo-1546435770-a3e426bf472b","photo-1505751171710-1f6d0ace5a85")),

dict(name="Smart LED Desk Lamp",brand="LumiTech",category="Electronics",
     price=899,original_price=1499,stock=78,rating=4.6,reviews=1120,badge="Hot",
     image_emoji="💡",image_color="#fbbf24",
     description="Touch-controlled smart lamp with 3 color modes, 10 brightness levels, built-in USB-C 18W charging port and blue-light eye-care mode.",
     highlights=_h("3 color modes: Warm / Neutral / Cool white","10 brightness levels via touch dimmer","Built-in USB-C 18W charging port","Eye-care mode reduces blue light by 70%","360° flexible neck — perfect positioning","Memory function saves last setting"),
     specs_json=_s(Brand="LumiTech",Power="12W LED",ColorTemp="3000K–6500K",Brightness="500 lux max",USB="USB-C 18W",Neck="360° Flexible",Warranty="1 Year"),
     image_url=_img("photo-1534088568595-a066f410bcda"),
     images_json=_imgs("photo-1507473885765-e6ed057f782c","photo-1550399105-c4db5fb85c18","photo-1518481852452-9415b262eba4")),

dict(name="Mechanical Gaming Keyboard",brand="TechPulse",category="Electronics",
     price=3299,original_price=5999,stock=30,rating=4.7,reviews=876,badge="New",
     image_emoji="⌨️",image_color="#f97316",
     description="Dominate your gameplay with Blue tactile switches, per-key RGB, detachable wrist rest, and full N-key rollover anti-ghosting.",
     highlights=_h("Blue Tactile switches — 50M keystroke lifespan","Per-key RGB 16.8M colors","Detachable magnetic wrist rest","N-key rollover + 100% anti-ghosting","USB passthrough on keyboard","Windows / Mac / Linux compatible"),
     specs_json=_s(Brand="TechPulse",Switch="Blue Tactile",Layout="Full 104-key",RGB="Per-key 16.8M",AntiGhosting="N-Key Rollover",WristRest="Detachable Magnetic",Weight="1.1kg",Warranty="2 Years"),
     image_url=_img("photo-1541140532154-b024d705b90a"),
     images_json=_imgs("photo-1587829741301-dc798b83add3","photo-1595044426077-d36d9236d54a","photo-1616489953021-93e20c8ecc10")),

dict(name="10000mAh Slim Power Bank",brand="ChargeX",category="Electronics",
     price=1199,original_price=1999,stock=112,rating=4.5,reviews=3420,badge="Sale",
     image_emoji="🔋",image_color="#22c55e",
     description="Ultra-slim 10000mAh power bank with 20W USB-C PD fast charging. Charges smartphones 2.5× on a single charge. Airline carry-on approved.",
     highlights=_h("20W USB-C PD — charges phone in 1.5 hrs","10000mAh = 2.5 full charges for most phones","Dual output: USB-C + USB-A simultaneously","LED indicator for remaining charge","Airline approved — carry-on safe","Universal: iPhone, Samsung, OnePlus, etc."),
     specs_json=_s(Capacity="10000mAh",Input="USB-C 18W",Output1="USB-C PD 20W",Output2="USB-A 12W",Dimensions="140×65×14mm",Weight="215g",Warranty="1 Year"),
     image_url=_img("photo-1585771724684-38269d6639fd"),
     images_json=_imgs("photo-1609091839311-d5365f9ff1c5","photo-1526289034009-0240ddb68ce3","photo-1620138546344-7b2c38516edf")),

dict(name="NexusPhone 5G Pro Smartphone",brand="NexusPhone",category="Electronics",
     price=29999,original_price=44999,stock=25,rating=4.8,reviews=5432,badge="Bestseller",
     image_emoji="📱",image_color="#6366f1",
     description="Flagship smartphone powered by Snapdragon 8 Gen 2, 6.7\" 120Hz AMOLED display, 50MP triple camera, 5000mAh battery with 65W fast charge.",
     highlights=_h("Snapdragon 8 Gen 2 — world's fastest mobile chip","6.7\" AMOLED 120Hz display, 1800 nits peak brightness","50MP + 12MP + 10MP triple rear camera + 32MP selfie","5000mAh battery + 65W charging = 100% in 45 min","256GB + 12GB RAM, 5G ready on all bands","IP68: 30-min waterproof up to 1.5m depth"),
     specs_json=_s(Processor="Snapdragon 8 Gen 2",Display="6.7\" AMOLED 120Hz",Camera="50+12+10MP rear / 32MP front",Battery="5000mAh 65W",RAM="12GB",Storage="256GB",OS="Android 14",Network="5G/4G",Rating="IP68"),
     image_url=_img("photo-1511707171634-5f897ff02aa9"),
     images_json=_imgs("photo-1512054502232-10a0a035d672","photo-1601972602237-96517cdb4d56","photo-1585060544812-6b45742d762f")),

dict(name="AirSound TWS Wireless Earbuds Pro",brand="AirSound",category="Electronics",
     price=1799,original_price=3499,stock=67,rating=4.6,reviews=3210,badge="Hot",
     image_emoji="🎵",image_color="#a855f7",
     description="True wireless earbuds with 6mm dynamic drivers, 28-hour total battery life, IPX5 sweat resistance, and one-tap transparency mode.",
     highlights=_h("6mm dynamic drivers with deep bass","28-hour total battery (7hr buds + 21hr case)","IPX5 sweat and water resistant","One-tap transparency / ANC mode switching","Bluetooth 5.3 low-latency gaming mode","Fast pair: open case to connect instantly"),
     specs_json=_s(Brand="AirSound",Driver="6mm Dynamic",Battery="7hr+21hr case",Resistance="IPX5",Connectivity="Bluetooth 5.3",LatencyMode="Gaming <50ms",ChargingCase="USB-C",Warranty="1 Year"),
     image_url=_img("photo-1590658268037-6bf12165a8df"),
     images_json=_imgs("photo-1606220945770-b5b6c2c55bf1","photo-1592921451044-ac7a3b62484c","photo-1613040809024-b4ef7ba99bc3")),

dict(name="FitPro Smart Fitness Watch",brand="FitPro",category="Electronics",
     price=4999,original_price=8999,stock=43,rating=4.5,reviews=2103,badge="New",
     image_emoji="⌚",image_color="#0ea5e9",
     description="Advanced health tracker with 24/7 heart rate, SpO2, sleep tracking, 100+ workout modes, and 14-day battery. Always-on AMOLED display.",
     highlights=_h("Always-on 1.4\" AMOLED display","24/7 heart rate + SpO2 blood oxygen sensor","14-day battery life in standard mode","100+ workout modes with auto-detect","GPS built-in — no phone needed for runs","5ATM water resistant — swim safe"),
     specs_json=_s(Display="1.4\" AMOLED Always-On",Battery="14 days",HeartRate="24/7 optical sensor",SpO2="Yes",GPS="Built-in",WorkoutModes="100+",WaterResistance="5ATM",Compatibility="Android/iOS"),
     image_url=_img("photo-1523275335684-37898b6baf30"),
     images_json=_imgs("photo-1579586337278-3befd40fd17a","photo-1617625802912-cde586faf749","photo-1575311373937-040b8058069f")),

dict(name="BoomBox Portable Bluetooth Speaker",brand="BoomBox",category="Electronics",
     price=1599,original_price=2999,stock=55,rating=4.4,reviews=1567,badge=None,
     image_emoji="🔊",image_color="#f97316",
     description="360° surround sound, 24-hour battery, IPX7 waterproof rating, and built-in powerbank — the ultimate outdoor speaker.",
     highlights=_h("360° surround sound with 20W peak output","24-hour battery life at 70% volume","IPX7 fully waterproof — drop it in water","Built-in 3000mAh powerbank for device charging","TWS pairing: link two speakers for stereo","Integrated carabiner clip for adventures"),
     specs_json=_s(Power="20W",Battery="24 hours",Waterproof="IPX7",Powerbank="3000mAh",Pairing="TWS Stereo Link",Connectivity="Bluetooth 5.0",Weight="540g",Warranty="1 Year"),
     image_url=_img("photo-1608043152269-423dbba4e7e1"),
     images_json=_imgs("photo-1545454675-3531b543be5d","photo-1563862810-c66e5fb31c0e","photo-1589561253898-768105ca91a8")),

dict(name="ClearVue 4K HD Webcam",brand="ClearVue",category="Electronics",
     price=3299,original_price=5499,stock=38,rating=4.5,reviews=876,badge=None,
     image_emoji="📷",image_color="#0ea5e9",
     description="Professional 4K webcam with autofocus, dual noise-cancelling microphones, and plug-and-play USB-C. Perfect for streaming, video calls, and content creation.",
     highlights=_h("4K 30fps / 1080p 60fps ultra-clear video","Dual built-in noise-cancelling microphones","AI-powered autofocus + auto light correction","Plug-and-play USB-C — no drivers needed","Compatible: Zoom, Teams, OBS, YouTube","90° wide-angle field of view"),
     specs_json=_s(Resolution="4K 30fps / 1080p 60fps",Microphone="Dual noise-cancelling",Autofocus="AI-powered",FOV="90°",Connection="USB-C",Compatibility="Windows/Mac/Linux",Warranty="1 Year"),
     image_url=_img("photo-1587825140708-dfaf72ae4b04"),
     images_json=_imgs("photo-1613490493576-7fde63acd811","photo-1598743400863-f2b6bdf0c5a0","photo-1591238372338-7ca42c89b8a3")),

dict(name="HyperGlide Wireless Gaming Mouse",brand="HyperGlide",category="Electronics",
     price=2199,original_price=3999,stock=47,rating=4.7,reviews=1345,badge=None,
     image_emoji="🖱️",image_color="#ef4444",
     description="Ultra-lightweight wireless gaming mouse at just 63g, with 25600 DPI optical sensor, 70-hour battery, and 2.4GHz low-latency dongle.",
     highlights=_h("Only 63g ultra-lightweight paracord-style build","25600 DPI adjustable optical sensor","70-hour battery on single charge","2.4GHz wireless = 1ms latency (same as wired)","6 programmable buttons with onboard memory","RGB underglow with 16.8M color options"),
     specs_json=_s(Weight="63g",DPI="100–25600 adjustable",Battery="70 hours",Wireless="2.4GHz 1ms",Buttons="6 programmable",Sensor="Optical PAW3395",RGB="Yes",Warranty="2 Years"),
     image_url=_img("photo-1527814050087-3793815479db"),
     images_json=_imgs("photo-1600861194942-f883de0dfe96","photo-1607345366928-199ea26cfe3e","photo-1560472354-b33ff0c44a43")),

dict(name="USB 7-Port Powered Hub",brand="HubMax",category="Electronics",
     price=599,original_price=999,stock=134,rating=4.3,reviews=2301,badge="Sale",
     image_emoji="🔌",image_color="#64748b",
     description="7-port USB hub with 5 × USB-A 3.0 + 2 × USB-C ports, 60W power delivery, and individual LED power switches per port.",
     highlights=_h("5× USB-A 3.0 (5Gbps) + 2× USB-C ports","60W total power delivery — charge laptop + devices","Individual LED switch for each port","Aluminum heat-dissipating shell","4ft braided cable — reach any corner","Plug-and-play, driver-free"),
     specs_json=_s(Ports="5×USB-A 3.0 + 2×USB-C",PowerDelivery="60W total",Speed="USB 3.0 = 5Gbps",Cable="4ft braided",Shell="Aluminum",Compatibility="Windows/Mac/Linux"),
     image_url=_img("photo-1591370874773-6702e8f12fd8"),
     images_json=_imgs("photo-1581091012184-7c85d72b2d62","photo-1518770660439-4636190af475","photo-1593642632559-0c6d3fc62b89")),

dict(name="ErgoDesk Adjustable Laptop Stand",brand="ErgoDesk",category="Electronics",
     price=1299,original_price=2199,stock=89,rating=4.6,reviews=1890,badge=None,
     image_emoji="💻",image_color="#6366f1",
     description="6-angle adjustable aluminium laptop stand with heat-venting design, foldable for travel, fits all laptops 10–17 inches.",
     highlights=_h("6 adjustable height & angle positions","Solid aluminium alloy — holds up to 20kg","Heat-venting slots prevent overheating","Folds flat — fits in laptop bag","Anti-slip silicone pads protect your desk","Fits 10\" to 17\" laptops & tablets"),
     specs_json=_s(Material="Aluminium alloy",Angles="6 positions",MaxLoad="20kg",Compatibility="10\"–17\" laptops",Folded="280×10mm slim",Weight="480g",Warranty="1 Year"),
     image_url=_img("photo-1593642702821-c8da6771f0c6"),
     images_json=_imgs("photo-1484788984921-03950022c38b","photo-1575330933415-fd8e7defe2ed","photo-1593642632559-0c6d3fc62b89")),

dict(name="SafeView 1080p Smart Security Camera",brand="SafeView",category="Electronics",
     price=2499,original_price=3999,stock=62,rating=4.5,reviews=987,badge=None,
     image_emoji="📹",image_color="#1d4ed8",
     description="Indoor/outdoor 1080p smart camera with night vision, motion alerts, 360° PTZ rotation, and 30-day cloud storage. Works with Alexa and Google Home.",
     highlights=_h("1080p Full HD with colour night vision up to 8m","360° pan + 90° tilt remote control via app","Motion detection with real-time push alerts","30-day free cloud storage included","Two-way audio — speak through the camera","Works with Alexa & Google Home"),
     specs_json=_s(Resolution="1080p Full HD",NightVision="Colour up to 8m",PTZ="360° pan / 90° tilt",Storage="Cloud 30-day + SD card",Audio="Two-way",SmartHome="Alexa / Google Home",Warranty="1 Year"),
     image_url=_img("photo-1608267165496-fc5f9e3ba7ed"),
     images_json=_imgs("photo-1563412545-f47bd28a26c9","photo-1556742521-9713bf272865","photo-1571171637578-41bc2dd41cd2")),

dict(name="ChargeFast 15W Wireless Charging Pad",brand="ChargeFast",category="Electronics",
     price=899,original_price=1499,stock=98,rating=4.4,reviews=1543,badge="Sale",
     image_emoji="⚡",image_color="#fbbf24",
     description="15W ultra-fast wireless charging pad with foreign object detection, sleep-friendly breathing LED, and anti-slip surface. Charge through cases up to 3mm.",
     highlights=_h("15W max for Samsung / 12W MagSafe compatible","Charges through covers up to 3mm thick","Foreign object & temperature protection","Breathing LED indicator — sleep friendly","Anti-slip silicone base — stays in place","Includes 5A USB-C cable"),
     specs_json=_s(MaxPower="15W",Compatible="Qi + MagSafe",CaseSupport="Up to 3mm",Protection="FOD + temp + overcharge",LED="Breathing (dimmable)",Input="USB-C 5A",Warranty="1 Year"),
     image_url=_img("photo-1610438235354-a6ae5528a0dd"),
     images_json=_imgs("photo-1600490036275-3c6f0e41e1e3","photo-1586953208448-b95a79798f07","photo-1629131726692-1accd0c53ce0")),

dict(name="SoundWar Gaming Headset 7.1",brand="SoundWar",category="Electronics",
     price=2499,original_price=4499,stock=41,rating=4.6,reviews=1234,badge=None,
     image_emoji="🎮",image_color="#7c3aed",
     description="7.1 virtual surround headset with 50mm neodymium drivers, detachable noise-cancelling mic, memory foam earcups, and RGB lighting.",
     highlights=_h("7.1 virtual surround sound for positional audio","50mm neodymium drivers — deep bass, crisp highs","Detachable flexible noise-cancelling microphone","Memory foam + leatherette earcups — 8hr comfort","RGB lighting with 4 preset modes","Compatible: PC, PS5, Xbox, Switch"),
     specs_json=_s(Drivers="50mm neodymium",Surround="7.1 Virtual",Microphone="Detachable noise-cancelling",Connection="USB + 3.5mm",EarcupPadding="Memory foam",RGB="Yes",Compatibility="PC/PS5/Xbox/Switch",Warranty="1 Year"),
     image_url=_img("photo-1599658880436-c61792e70672"),
     images_json=_imgs("photo-1617897903246-719242758050","photo-1616588589f87-fe69aaeb47da","photo-1563297007-0686b7003af7")),

dict(name="SpeedDrive External SSD 1TB",brand="SpeedDrive",category="Electronics",
     price=6999,original_price=9999,stock=28,rating=4.8,reviews=678,badge="New",
     image_emoji="💾",image_color="#0f172a",
     description="Compact external SSD with read speeds up to 1050MB/s and write 1000MB/s. Drop-proof, dust-proof, 300G shock resistant. Ideal for creative pros.",
     highlights=_h("Read 1050MB/s / Write 1000MB/s — 10× faster than HDD","300G shock resistant + IP55 dust/splash proof","USB 3.2 Gen 2 — backward compatible","1TB capacity — store 200,000 photos or 500 hours of video","Works with PC, Mac, Android, iPad","3-year manufacturer warranty"),
     specs_json=_s(Capacity="1TB",ReadSpeed="1050MB/s",WriteSpeed="1000MB/s",Interface="USB 3.2 Gen 2",ShockResistance="300G",Protection="IP55",Compatibility="PC/Mac/Android/iPad",Warranty="3 Years"),
     image_url=_img("photo-1601737487795-dab272f52420"),
     images_json=_imgs("photo-1558618666-fcd25c85cd64","photo-1597372284741-4e0c86bd30b1","photo-1591488320449-011701bb6704")),

dict(name="GlowStrip RGB Smart LED Strip 5M",brand="GlowStrip",category="Electronics",
     price=799,original_price=1499,stock=156,rating=4.4,reviews=3456,badge="Hot",
     image_emoji="🌈",image_color="#ec4899",
     description="Music-sync smart LED strip, 5 metres, 16 million colours, app + voice control (Alexa/Google), cuttable and extendable up to 10M.",
     highlights=_h("16.8M colours + 20 dynamic music-sync modes","App control via iOS/Android + Alexa/Google Home","5 metre strip, cuttable every 3 LEDs","Self-adhesive 3M tape backing — stick anywhere","Extendable up to 10M with connector kit","Timer & schedule functions in app"),
     specs_json=_s(Length="5 metres (extendable to 10M)",Colors="16.8M RGB+W",SmartHome="Alexa / Google Home",MusicSync="Yes — mic built-in",Power="USB-C 5V",CuttingInterval="Every 3 LEDs",Warranty="1 Year"),
     image_url=_img("photo-1558618047-fcd16d746a8b"),
     images_json=_imgs("photo-1565193566173-7a0ee3dbe261","photo-1568827999250-f2f66a608b21","photo-1555086079-b997cd6a0d56")),

dict(name="ArtPad Digital Drawing Tablet",brand="ArtPad",category="Electronics",
     price=4499,original_price=7999,stock=22,rating=4.7,reviews=891,badge=None,
     image_emoji="🎨",image_color="#8b5cf6",
     description="Professional drawing tablet with 8192 levels of pen pressure, 10×6 inch active area, tilt recognition, and 8 express keys. Perfect for digital art & Photoshop.",
     highlights=_h("8192 levels pen pressure — ultra natural drawing","10×6\" large active drawing area","Tilt recognition ±60° for realistic brush strokes","8 programmable express keys","Battery-free pen — no charging ever","Compatible with Photoshop, Illustrator, Krita, Clip Studio"),
     specs_json=_s(ActiveArea="10×6 inches",PressureLevels="8192",TiltRecognition="±60°",ExpressKeys="8",Pen="Battery-free EMR",Resolution="5080 LPI",Compatibility="Windows/Mac/Linux",Warranty="1 Year"),
     image_url=_img("photo-1626785774573-4b799315345d"),
     images_json=_imgs("photo-1611532736597-de2d4265fba3","photo-1608054791095-e0482903048e","photo-1498050108023-c5249f4df085")),

dict(name="CineMax Mini Projector HD",brand="CineMax",category="Electronics",
     price=8999,original_price=14999,stock=15,rating=4.4,reviews=345,badge="New",
     image_emoji="🎬",image_color="#1e3a5f",
     description="Portable 1080p native projector, 300 ANSI lumens, built-in Android TV 11, dual 10W speakers, and keystone correction. Up to 120-inch screen.",
     highlights=_h("1080p native resolution — crisp, vibrant display","300 ANSI lumens — bright even in ambient light","Built-in Android TV 11 with Google Play Store","120-inch projection from just 2.5 metres","Dual 10W stereo speakers — room-filling sound","HDMI + USB-A + AUX + WiFi 6 + Bluetooth"),
     specs_json=_s(Resolution="1080p Native",Brightness="300 ANSI lumens",OS="Android TV 11",MaxScreen="120 inches",Speakers="10W×2 stereo",Ports="HDMI/USB-A/AUX",Connectivity="WiFi 6 + BT 5.0",Warranty="1 Year"),
     image_url=_img("photo-1478720568477-152d9b164e26"),
     images_json=_imgs("photo-1489599849927-2ee91cede3ba","photo-1593078166039-c9878df5c520","photo-1585386959984-a4155224a1ad")),

# ── MEN'S FASHION ─────────────────────────────────────────────────────────────
dict(name="ClassicWear Premium Oxford Shirt",brand="ClassicWear",category="Men's Fashion",
     price=899,original_price=1699,stock=78,rating=4.5,reviews=1234,badge=None,
     image_emoji="👔",image_color="#1e40af",
     description="100% premium Egyptian cotton Oxford shirt with slim fit, button-down collar, and wrinkle-resistant finish. Available in 6 colours.",
     highlights=_h("100% Egyptian cotton — ultra breathable & soft","Slim fit with button-down collar","Wrinkle-resistant — iron-free all day","Reinforced stitching at stress points","Machine washable, colour-fast","Sizes: XS to XXL in 6 colours"),
     specs_json=_s(Material="100% Egyptian Cotton",Fit="Slim",Collar="Button-down",Sizes="XS–XXL",Colors="6 colors",Care="Machine wash cold",Origin="India"),
     image_url=_img("photo-1602810316498-ab67cf68c8e1"),
     images_json=_imgs("photo-1596755094514-f87e34085b2c","photo-1489987707025-afc232f7ea0f","photo-1521572163474-6864f9cf17ab")),

dict(name="FitStyle Slim Fit Chino Pants",brand="FitStyle",category="Men's Fashion",
     price=1199,original_price=2199,stock=62,rating=4.4,reviews=876,badge=None,
     image_emoji="👖",image_color="#b45309",
     description="Stretch slim-fit chino pants with 4-way flex fabric, hidden stretch waistband, and crease-resistant finish — smart casual perfection.",
     highlights=_h("4-way stretch fabric — full range of motion","Hidden elasticated waistband for comfort","Crease and fade resistant","Slim fit — tapered from thigh to ankle","5-pocket design with zip fly","Sizes: 28W–40W in 8 colours"),
     specs_json=_s(Material="97% Cotton 3% Elastane",Fit="Slim tapered",Waist="28W–40W",Colors="8 colors",Care="Machine wash",Feature="Crease resistant",Origin="India"),
     image_url=_img("photo-1473966968600-fa801b869a1a"),
     images_json=_imgs("photo-1624378439575-d8705ad7ae80","photo-1547935706-d5f49571d8c3","photo-1581044777550-4cfa60707c03")),

dict(name="DenimCraft Men's Denim Jacket",brand="DenimCraft",category="Men's Fashion",
     price=2299,original_price=4499,stock=34,rating=4.6,reviews=654,badge=None,
     image_emoji="🧥",image_color="#1e3a5f",
     description="Classic slim-fit denim jacket in 100% stonewashed cotton with contrast stitching, chest and side pockets, and adjustable cuff buttons.",
     highlights=_h("100% stonewashed premium cotton denim","Slim fit — tailored for modern silhouette","2 chest pockets + 2 side pockets","Adjustable button cuffs for perfect fit","Pre-washed for that authentic worn look","Sizes: S to 3XL in 3 washes"),
     specs_json=_s(Material="100% Stonewashed Cotton",Fit="Slim",Pockets="4 total",Wash="Blue/Dark/Light",Sizes="S–3XL",Care="Machine wash cold",Origin="India"),
     image_url=_img("photo-1551537482-f2075a1d41f2"),
     images_json=_imgs("photo-1591047139829-d91aecb6caea","photo-1559551409-dadc959f76b8","photo-1516762689617-e1cffcef479d")),

dict(name="LuxWear Premium Genuine Leather Belt",brand="LuxWear",category="Men's Fashion",
     price=599,original_price=999,stock=145,rating=4.3,reviews=1543,badge=None,
     image_emoji="👗",image_color="#92400e",
     description="Full-grain genuine leather belt with antique brass buckle, 1.5\" width, and punched holes for perfect adjustability. Ages beautifully with wear.",
     highlights=_h("Full-grain genuine leather — ages beautifully","Classic antique brass buckle — tarnish resistant","1.5\" width fits all standard belt loops","Sizes 28\" to 46\" — each size adjustable","Stitched edges for shape retention","Suitable for formal and casual wear"),
     specs_json=_s(Material="Full-grain leather",Buckle="Antique Brass",Width="1.5 inches",Sizes="28\"–46\"",Colors="Brown / Black / Tan",Warranty="6 months"),
     image_url=_img("photo-1553062407-98eeb64c6a62"),
     images_json=_imgs("photo-1624222525064-27b5d6c0e0d6","photo-1533227268428-f9ed0900fb3b","photo-1617952236317-0bd127407984")),

dict(name="PoloClub Men's Polo T-Shirt Pack of 3",brand="PoloClub",category="Men's Fashion",
     price=999,original_price=1799,stock=98,rating=4.5,reviews=2345,badge="Sale",
     image_emoji="👕",image_color="#0891b2",
     description="Pack of 3 premium piqué cotton polo shirts with ribbed collar, 2-button placket, and side vents. Perfect for casual and semi-formal occasions.",
     highlights=_h("Pack of 3 polo shirts — great value","100% piqué cotton — cool and breathable","Ribbed collar + cuffs retain shape","2-button placket with matching buttons","Side vents for ease of movement","Available in 10 colour combinations"),
     specs_json=_s(Material="100% Piqué Cotton",Collar="Ribbed",Placket="2-button",Sizes="S–3XL",Pack="3 polos",Colors="10 combo packs",Care="Machine wash"),
     image_url=_img("photo-1576566588028-4147f3842f27"),
     images_json=_imgs("photo-1618354691373-d851c5c3a990","photo-1536992266094-82847e1fd431","photo-1503341338985-c0477be52513")),

dict(name="SlimCarry Minimalist Leather Wallet",brand="SlimCarry",category="Men's Fashion",
     price=699,original_price=1299,stock=167,rating=4.4,reviews=1876,badge=None,
     image_emoji="👛",image_color="#78350f",
     description="Ultra-slim 6mm bifold wallet in genuine leather, holds 12 cards + cash, RFID blocking, and fits perfectly in front pockets.",
     highlights=_h("Only 6mm thick — fits in front pocket comfortably","RFID blocking — protects contactless cards","Holds 12 cards + folded cash","Genuine leather exterior — ages beautifully","Stitched bill pocket with full-length slot","Available in 5 colours"),
     specs_json=_s(Material="Genuine Leather",Thickness="6mm",CardSlots="12 cards + cash",RFID="Blocked",Size="9.5×11.5cm",Colors="Black/Brown/Tan/Navy/Olive"),
     image_url=_img("photo-1627123424574-724758594785"),
     images_json=_imgs("photo-1559586272-9070b383f5d7","photo-1553062407-98eeb64c6a62","photo-1650025618099-fd95d60c3e17")),

dict(name="TimeCraft Classic Chronograph Watch",brand="TimeCraft",category="Men's Fashion",
     price=3499,original_price=6999,stock=19,rating=4.7,reviews=987,badge="Hot",
     image_emoji="⌚",image_color="#1c1917",
     description="Japanese Miyota quartz chronograph with stainless steel case, sapphire crystal glass, 5ATM water resistance, and genuine leather strap.",
     highlights=_h("Japanese Miyota quartz movement — ±10 sec/year accuracy","Sapphire crystal glass — scratch resistant","Stainless steel 40mm case","5ATM water resistant — splash & rain proof","Genuine leather strap with deployment clasp","Chronograph + date display"),
     specs_json=_s(Movement="Japanese Miyota Quartz",Crystal="Sapphire",CaseSize="40mm",CaseMaterial="Stainless Steel",Strap="Genuine Leather",WaterResistance="5ATM",Functions="Time/Date/Chronograph",Warranty="2 Years"),
     image_url=_img("photo-1508685096489-7aacd43bd3b1"),
     images_json=_imgs("photo-1547996160-81dfa63595aa","photo-1611591437281-460bfbe1220a","photo-1619980559765-5e21a63e8687")),

dict(name="StreetStep Men's Casual Sneakers",brand="StreetStep",category="Men's Fashion",
     price=1799,original_price=2999,stock=53,rating=4.5,reviews=2134,badge=None,
     image_emoji="👟",image_color="#374151",
     description="Minimalist all-white sneakers with vulcanised rubber sole, canvas upper, and memory foam insole. The everyday essential that goes with everything.",
     highlights=_h("Premium canvas upper — breathable and durable","Vulcanised rubber sole — flexible and grippy","Memory foam cushioned insole","Minimalist all-white design — pairs with anything","Machine washable canvas","Sizes UK 6 to 12"),
     specs_json=_s(Upper="Canvas",Sole="Vulcanised Rubber",Insole="Memory Foam",Sizes="UK 6–12",Colors="White/Black/Navy",Care="Machine washable",Warranty="3 months"),
     image_url=_img("photo-1600185365483-26d0a7fc57d5"),
     images_json=_imgs("photo-1542291026-7eec264c27ff","photo-1491553895911-0055eca6402d","photo-1597248881519-db089e3e0346")),

dict(name="TrekWay Men's Laptop Backpack 30L",brand="TrekWay",category="Men's Fashion",
     price=1499,original_price=2499,stock=71,rating=4.5,reviews=1567,badge=None,
     image_emoji="🎒",image_color="#064e3b",
     description="Water-resistant 30L backpack with dedicated padded laptop compartment (fits up to 17\"), USB-A charging port, and 8 organised pockets.",
     highlights=_h("Fits up to 17\" laptop — padded dedicated sleeve","Water-resistant nylon 600D exterior","External USB-A charging port with cable routing","8 pockets including hidden anti-theft back pocket","Padded adjustable shoulder straps with sternum strap","TSA-friendly clamshell opening"),
     specs_json=_s(Capacity="30 litres",LaptopFit="Up to 17\"",Material="Nylon 600D water-resistant",Pockets="8 total",USB="External USB-A port",Colors="Black/Grey/Navy",Weight="980g",Warranty="1 Year"),
     image_url=_img("photo-1553062407-98eeb64c6a45"),
     images_json=_imgs("photo-1622560480605-d83c853bc5c3","photo-1491553895911-0055eca6402d","photo-1553062407-98eeb64c6a62")),

dict(name="FlexFit Men's Sports Jogger Pants",brand="FlexFit",category="Men's Fashion",
     price=799,original_price=1499,stock=102,rating=4.4,reviews=1234,badge=None,
     image_emoji="🩱",image_color="#1e3a5f",
     description="Premium slim-taper joggers in 4-way stretch fleece fabric. Moisture-wicking, pockets with zip, and elasticated drawstring waist.",
     highlights=_h("4-way stretch fleece — maximum mobility","Moisture-wicking inner layer keeps you dry","Zip side pockets — secure during workouts","Elasticated drawstring waist for perfect fit","Slim taper fit — looks great at the gym or casually","Sizes XS to 3XL in 6 colours"),
     specs_json=_s(Material="78% Polyester 22% Spandex Fleece",Fit="Slim taper",Pockets="2 zip side pockets",Waist="Elasticated + drawstring",Sizes="XS–3XL",Colors="6 colors",Care="Machine wash"),
     image_url=_img("photo-1624378441340-1c0c8fd900f1"),
     images_json=_imgs("photo-1542291026-7eec264c27ff","photo-1506629082955-511b1aa562c8","photo-1517838277536-f5f99be501cd")),

# ── WOMEN'S FASHION ───────────────────────────────────────────────────────────
dict(name="FloralStyle Floral Wrap Summer Dress",brand="FloralStyle",category="Women's Fashion",
     price=1099,original_price=2199,stock=47,rating=4.6,reviews=1345,badge="Trending",
     image_emoji="👗",image_color="#ec4899",
     description="Flowy midi wrap dress in printed chiffon with adjustable waist tie, V-neck, and flutter sleeves. Perfect for summer, beach, or brunch.",
     highlights=_h("Lightweight printed chiffon — flowy and breathable","Adjustable wrap tie waist — flatters every body type","V-neckline with flutter sleeves","Midi length — knee to calf","Unlined fabric for summer lightness","Hand wash or delicate machine cycle"),
     specs_json=_s(Material="100% Chiffon",Style="Wrap Midi",Neckline="V-neck",Sleeves="Flutter",Sizes="XS–XXL",Colors="6 floral prints",Care="Handwash / delicate"),
     image_url=_img("photo-1515886657613-9f3515b0c78f"),
     images_json=_imgs("photo-1469334031218-e382a71b716b","photo-1572804013309-59a88b7e92f1","photo-1485231183945-fffde7f6b8e8")),

dict(name="FlexWear High-Waist Yoga Leggings",brand="FlexWear",category="Women's Fashion",
     price=799,original_price=1499,stock=88,rating=4.7,reviews=2345,badge="Bestseller",
     image_emoji="🩲",image_color="#7c3aed",
     description="High-waist compressive yoga leggings with squat-proof double-layer waistband, 4-way stretch, and moisture-wicking finish. Buttery soft feel.",
     highlights=_h("Buttery soft 4-way stretch fabric","High waistband — no rolling, stays in place","Squat-proof double-layer — 100% opaque","Moisture-wicking + quick-dry","Hidden waistband pocket fits phone","Sizes XS to 3XL — inclusive sizing"),
     specs_json=_s(Material="88% Nylon 12% Spandex",Waist="High-rise",Opacity="Squat-proof",Pocket="Hidden waistband",Sizes="XS–3XL",Colors="12 colors",Care="Machine wash cold"),
     image_url=_img("photo-1506629082955-511b1aa562c8"),
     images_json=_imgs("photo-1518310383802-640c2de311b2","photo-1571019613454-1cb2f99b2d8b","photo-1595078475328-1ab05d0a6a0e")),

dict(name="FitFashion Women's Sports Crop Top",brand="FitFashion",category="Women's Fashion",
     price=499,original_price=999,stock=113,rating=4.4,reviews=876,badge=None,
     image_emoji="👙",image_color="#f43f5e",
     description="Compression sports crop top with built-in shelf bra, removable pads, racerback design, and moisture-wicking fabric for all-day workouts.",
     highlights=_h("Built-in shelf bra with removable padding","Racerback design — maximise range of motion","Moisture-wicking + 4-way stretch fabric","Quick-dry — back in the game faster","Medium support for yoga, pilates, HIIT","Sizes XS to 2XL"),
     specs_json=_s(Material="85% Nylon 15% Spandex",Support="Medium (built-in shelf bra)",Padding="Removable",Design="Racerback",Sizes="XS–2XL",Colors="8 colors",Care="Machine wash cold"),
     image_url=_img("photo-1544377193-33dcf4d68fb5"),
     images_json=_imgs("photo-1524163429-a0d7d1c37f37","photo-1518310383802-640c2de311b2","photo-1571019613454-1cb2f99b2d8b")),

dict(name="EcoStyle Canvas Shoulder Tote Bag",brand="EcoStyle",category="Women's Fashion",
     price=799,original_price=1499,stock=134,rating=4.5,reviews=1234,badge="Eco",
     image_emoji="👜",image_color="#15803d",
     description="Large organic canvas tote with zip-top closure, inner zip pocket, laptop sleeve, and natural cotton webbing handles. Eco-friendly and machine washable.",
     highlights=_h("Organic cotton canvas — sustainable choice","Zip-top closure keeps belongings secure","Inner zip pocket + open slip pockets","Laptop sleeve fits up to 15\"","Machine washable — stays looking fresh","Reinforced stitching at handle base"),
     specs_json=_s(Material="Organic Cotton Canvas",Capacity="35 litres",LaptopFit="Up to 15\"",Closure="Zip-top",Pockets="2 inner + 2 outer",Handles="Natural cotton webbing",Colors="Natural/Black/Navy"),
     image_url=_img("photo-1544816155-12df9643f363"),
     images_json=_imgs("photo-1583623025817-d180a2221d0a","photo-1566150905458-1bf1fc113f0d","photo-1490481651871-ab68de25d43d")),

dict(name="StepStyle Women's Ankle Fashion Boots",brand="StepStyle",category="Women's Fashion",
     price=2499,original_price=4499,stock=29,rating=4.5,reviews=789,badge=None,
     image_emoji="👢",image_color="#292524",
     description="Classic ankle boots in PU leather with block heel, side zip, cushioned insole, and non-slip rubber sole. Elegant and comfortable all-day wear.",
     highlights=_h("Premium PU leather — easy to clean","Side zip entry for easy on/off","5cm block heel — elevated without discomfort","Cushioned footbed for all-day comfort","Non-slip rubber outsole","Pairs with jeans, dresses, or midi skirts"),
     specs_json=_s(Material="PU Leather",HeelHeight="5cm block heel",Closure="Side zip",Sole="Non-slip rubber",Insole="Cushioned foam",Sizes="UK 3–8",Colors="Black/Brown/Tan"),
     image_url=_img("photo-1543163521-1bf539c55dd2"),
     images_json=_imgs("photo-1512436991641-6745cdb1723f","photo-1614252369475-531eba835eb1","photo-1491553895911-0055eca6402d")),

dict(name="SilkLux Luxury Silk Scarf",brand="SilkLux",category="Women's Fashion",
     price=599,original_price=1099,stock=89,rating=4.3,reviews=523,badge=None,
     image_emoji="🧣",image_color="#c026d3",
     description="Pure mulberry silk scarf (90×90cm) with hand-rolled edges and vibrant printed pattern. Wear as neck scarf, headband, bag accessory, or wrap.",
     highlights=_h("100% pure mulberry silk — supremely smooth","Hand-rolled and hand-stitched edges","90×90cm generous size — versatile styling","Vibrant print — won't fade with care","Wear 10+ ways: neck, head, wrist, bag, top","Comes in gift-ready box"),
     specs_json=_s(Material="100% Mulberry Silk",Size="90×90 cm",Edges="Hand-rolled & stitched",Care="Dry clean / hand wash cold",Prints="12 designs",Packaging="Gift box",Warranty="30-day return"),
     image_url=_img("photo-1607081692251-5f0c30d1e6d9"),
     images_json=_imgs("photo-1576078766891-f4cdcd93a16e","photo-1493932484895-752d1471eab5","photo-1567226475328-9e1dd1f15be8")),

dict(name="ElegantTime Women's Rose Gold Watch",brand="ElegantTime",category="Women's Fashion",
     price=3999,original_price=6999,stock=21,rating=4.7,reviews=1123,badge="Hot",
     image_emoji="⌚",image_color="#d97706",
     description="Slim minimalist rose gold watch with Japanese quartz movement, stainless steel mesh strap, mineral crystal glass, and 3ATM water resistance.",
     highlights=_h("Japanese quartz — precise, reliable timekeeping","Slim 8mm rose gold PVD stainless steel case","Adjustable mesh strap — fits all wrist sizes","Mineral crystal glass — scratch resistant","3ATM water resistant — everyday splash proof","Classical round 36mm face"),
     specs_json=_s(Movement="Japanese Quartz",CaseSize="36mm",CaseMaterial="Rose Gold PVD Steel",Strap="Adjustable Mesh",Crystal="Mineral",WaterResistance="3ATM",Warranty="1 Year"),
     image_url=_img("photo-1524592094714-0f0654e359b2"),
     images_json=_imgs("photo-1547996160-81dfa63595aa","photo-1612817288484-6f916006741a","photo-1507003211169-0a1dd7228f2d")),

dict(name="LuxCarry Women's Structured Handbag",brand="LuxCarry",category="Women's Fashion",
     price=2999,original_price=5499,stock=18,rating=4.6,reviews=643,badge=None,
     image_emoji="👜",image_color="#a16207",
     description="Structured top-handle handbag in vegan leather with gold-tone hardware, zip-top closure, detachable crossbody strap, and 4 inner compartments.",
     highlights=_h("Premium vegan leather — cruelty-free","Structured shape — holds its form","Gold-tone premium zip + turnlock closure","Detachable adjustable crossbody strap","4 inner compartments + zip back pocket","Fits: tablet, wallet, cosmetics, umbrella"),
     specs_json=_s(Material="Vegan Leather",Hardware="Gold-tone",Closure="Zip + turnlock",Strap="Detachable crossbody",Dimensions="30×22×12cm",Pockets="4 interior + 1 back zip",Colors="Black/Camel/Burgundy"),
     image_url=_img("photo-1584917865442-de89df76afd3"),
     images_json=_imgs("photo-1548036328-c9fa89d128fa","photo-1590874103328-eac38a683ce7","photo-1566150905458-1bf1fc113f0d")),

dict(name="CozyWrap Women's Cable Knit Cardigan",brand="CozyWrap",category="Women's Fashion",
     price=1299,original_price=2499,stock=56,rating=4.6,reviews=987,badge=None,
     image_emoji="🧶",image_color="#d97706",
     description="Cosy oversized cable knit cardigan in thick acrylic blend with deep pockets, longline hem, and open-front design. Perfect for autumn and winter.",
     highlights=_h("Thick cable knit — genuinely warm","Oversized longline cut — stylish and cosy","Two deep side pockets","Open-front — no fuss styling","Pairs with jeans, leggings, or dresses","Sizes XS–3XL in 8 colours"),
     specs_json=_s(Material="60% Acrylic 40% Wool Blend",Style="Oversized longline",Pockets="2 deep side pockets",Front="Open-front",Sizes="XS–3XL",Colors="8 colors",Care="Handwash / dry flat"),
     image_url=_img("photo-1434389677669-e08b4cac3105"),
     images_json=_imgs("photo-1617952236317-0bd127407984","photo-1515372039744-b8f02a3ae446","photo-1516762689617-e1cffcef479d")),

dict(name="GlamHair Women's Hair Accessories Set",brand="GlamHair",category="Women's Fashion",
     price=399,original_price=699,stock=198,rating=4.4,reviews=1567,badge="Sale",
     image_emoji="💇",image_color="#f9a8d4",
     description="20-piece hair accessory set including claw clips, scrunchies, butterfly clips, bobby pins, and headbands. Damage-free and suitable for all hair types.",
     highlights=_h("20 pieces — scrunchies, claw clips, headbands, pins","Damage-free — no pulling or snagging","Suitable for thick, thin, curly, or straight hair","Premium elastic scrunchies — won't stretch out","Claw clips with strong spring mechanism","Presented in an organiser pouch"),
     specs_json=_s(Pieces="20 total",Includes="4 scrunchies + 3 claw clips + 4 butterfly clips + 5 bobby pins + 4 mini clips",HairType="All hair types",Material="Acrylic + elastic",Includes2="Organiser pouch"),
     image_url=_img("photo-1522337360788-8b13dee7a37e"),
     images_json=_imgs("photo-1499557354967-2b2d8910bcca","photo-1580618672524-41e6ff1e19f5","photo-1620833082012-879bbea9f9a4")),

# ── HOME & LIVING ─────────────────────────────────────────────────────────────
dict(name="EcoKitchen Bamboo Cutting Board Set",brand="EcoKitchen",category="Home & Living",
     price=699,original_price=1299,stock=56,rating=4.5,reviews=523,badge="Eco",
     image_emoji="🍽️",image_color="#65a30d",
     description="Set of 3 FSC-certified organic bamboo cutting boards (S/M/L), naturally antimicrobial, non-slip rubber feet, and dishwasher safe.",
     highlights=_h("100% organic bamboo — stronger than plastic","Naturally antimicrobial surface","Set of 3: Small, Medium, Large boards","Dishwasher safe and easy to clean","Non-slip rubber feet prevent sliding","Juice groove on large board"),
     specs_json=_s(Material="Organic Bamboo (FSC)",Set="3 boards S/M/L",SmallBoard="25×18cm",MediumBoard="35×25cm",LargeBoard="45×30cm",DishwasherSafe="Yes",Certification="FSC Certified"),
     image_url=_img("photo-1588165171080-c89acfa5ee83"),
     images_json=_imgs("photo-1584568694244-14fbdf83bd30","photo-1556909114-f6e7ad7d3136","photo-1600585152220-90363fe7e115")),

dict(name="ZenAir Aromatherapy Diffuser 500ml",brand="ZenAir",category="Home & Living",
     price=1099,original_price=1799,stock=41,rating=4.7,reviews=789,badge="Hot",
     image_emoji="🕯️",image_color="#d946ef",
     description="500ml ultrasonic aromatherapy diffuser, 10-hour continuous run, 7 LED colour modes, whisper-quiet BPA-free operation, auto shut-off.",
     highlights=_h("500ml large tank — runs up to 10 hours","7 LED colour modes with brightness control","Ultra-quiet BPA-free operation (<25dB)","3 mist modes: continuous / intermittent / off","Auto shut-off when water runs low","Works with all essential oils"),
     specs_json=_s(Tank="500ml",RunTime="10 hours",LED="7 colors",Noise="<25dB",Power="15W 110–240V",Coverage="30 sq.m",BPA="BPA-free",Warranty="1 Year"),
     image_url=_img("photo-1608571423902-eed4a5ad8108"),
     images_json=_imgs("photo-1571781926291-c477ebfd024b","photo-1549488344-cbb6c34484ac","photo-1602928321679-560bb453f190")),

dict(name="DreamRest Cervical Memory Foam Pillow Set",brand="DreamRest",category="Home & Living",
     price=1299,original_price=2199,stock=38,rating=4.8,reviews=1234,badge="Bestseller",
     image_emoji="🛏️",image_color="#94a3b8",
     description="Set of 2 CertiPUR-US certified memory foam pillows with ergonomic cervical contour, removable bamboo cover, and OEKO-TEX certification.",
     highlights=_h("Cervical contour design — aligns spine naturally","CertiPUR-US certified memory foam — safe, non-toxic","Bamboo cover — hypoallergenic, moisture-wicking","Removable, machine-washable cover","Suitable for all sleeping positions","Set of 2 premium pillows"),
     specs_json=_s(Fill="CertiPUR-US Memory Foam",Cover="Bamboo-derived",Size="60×40×12cm",Set="2 pillows",Care="Machine wash cover",Hypoallergenic="Yes",Certifications="CertiPUR-US + OEKO-TEX",Warranty="2 Years"),
     image_url=_img("photo-1631049307264-da0ec9d70304"),
     images_json=_imgs("photo-1586105251261-72a756497a11","photo-1567016432779-094069958ea5","photo-1592789705501-f9ae4287c4cf")),

dict(name="PureAir HEPA H13 Air Purifier",brand="PureAir",category="Home & Living",
     price=8999,original_price=14999,stock=14,rating=4.7,reviews=1234,badge="Hot",
     image_emoji="💨",image_color="#0369a1",
     description="True HEPA H13 air purifier covering 400 sq.ft, removes 99.97% of particles including dust, pollen, pet dander, smoke, and PM2.5 pollutants.",
     highlights=_h("True HEPA H13 — captures 99.97% of 0.1-micron particles","Removes PM2.5, pollen, smoke, pet dander, mould","Covers 400 sq.ft in 30 minutes","4-stage filtration: Pre-filter + HEPA + Activated Carbon + UV","Auto mode — adjusts fan speed to air quality","Sleep mode: whisper-quiet 22dB + dim display"),
     specs_json=_s(Filter="True HEPA H13",Efficiency="99.97%",Coverage="400 sq.ft",Stages="4-stage filtration",Noise="22dB (sleep mode)",CADR="300 m³/hr",Warranty="2 Years"),
     image_url=_img("photo-1585771724684-38269d6639fd"),
     images_json=_imgs("photo-1497436072909-60f360e1d4b1","photo-1563170351-be54709099cb","photo-1558618666-fcd25c85cd64")),

dict(name="BrewPerfect Pour Over Coffee Maker",brand="BrewPerfect",category="Home & Living",
     price=1899,original_price=3499,stock=48,rating=4.6,reviews=876,badge=None,
     image_emoji="☕",image_color="#78350f",
     description="Precision pour-over coffee dripper set with heat-resistant borosilicate glass carafe, stainless steel filter, and temperature-keeping base.",
     highlights=_h("Heat-resistant borosilicate glass carafe — 600ml","Reusable stainless steel mesh filter — no paper wastage","Precision flow control for perfect extraction","Glass + stainless steel — no plastic taste","Dishwasher safe (filter + carafe)","Easy to clean — remove filter, rinse, done"),
     specs_json=_s(Carafe="Borosilicate Glass 600ml",Filter="Reusable SS mesh",Material="Glass + Stainless Steel",Capacity="2–4 cups",DishwasherSafe="Yes",Includes="Carafe + filter + stand",Warranty="1 Year"),
     image_url=_img("photo-1495474472287-4d71bcdd2085"),
     images_json=_imgs("photo-1509042239860-f550ce710b93","photo-1447933601403-0c6688de566e","photo-1498804103079-a6351b050096")),

dict(name="LumiSmart Smart LED Bulb Pack of 3",brand="LumiSmart",category="Home & Living",
     price=799,original_price=1499,stock=178,rating=4.4,reviews=2134,badge="Sale",
     image_emoji="💡",image_color="#eab308",
     description="Pack of 3 WiFi smart LED bulbs, 9W = 60W equivalent, 16M colour + warm/cool white, voice control via Alexa & Google, schedule + scene modes.",
     highlights=_h("9W = 60W equivalent — save 85% electricity","16.8M colours + tunable white (2700K–6500K)","App + Alexa + Google Home voice control","Group control — manage all bulbs together","Schedule, timer, sunrise/sunset automation","Pack of 3 — cover living room + bedroom"),
     specs_json=_s(Wattage="9W (60W equiv.)",Colors="16.8M + tunable white",Base="E27 screw",SmartHome="Alexa / Google Home",Pack="3 bulbs",App="iOS + Android",Lifespan="25,000 hours",Warranty="1 Year"),
     image_url=_img("photo-1535303311164-664fc9ec6532"),
     images_json=_imgs("photo-1558618047-fcd16d746a8b","photo-1565193566173-7a0ee3dbe261","photo-1507473885765-e6ed057f782c")),

dict(name="KitchenPrime Non-Stick Cookware Set 5pc",brand="KitchenPrime",category="Home & Living",
     price=2499,original_price=4999,stock=32,rating=4.5,reviews=1543,badge=None,
     image_emoji="🍳",image_color="#b91c1c",
     description="5-piece non-stick cookware set — 20cm frypan, 24cm frypan, 20cm saucepan, 24cm casserole, and glass lid. Induction compatible, PFOA-free coating.",
     highlights=_h("PFOA-free non-stick Granitex coating — 3 layers","Induction, gas, ceramic, and electric compatible","Ergonomic heat-resistant handles","Tempered glass lids — see without lifting","Even heat distribution base","Suitable for dishwasher cleaning"),
     specs_json=_s(Pieces="5-piece set",Coating="PFOA-free Granitex 3-layer",Compatible="Induction / Gas / Ceramic / Electric",Handles="Heat-resistant silicone grips",Lids="Tempered glass",Dishwasher="Yes",Warranty="2 Years"),
     image_url=_img("photo-1556909114-f6e7ad7d3136"),
     images_json=_imgs("photo-1590794056226-79ef3a47ccf3","photo-1507048331197-7d4ac70811cf","photo-1556910096-6f5e72db6803")),

dict(name="CleanPro Cordless Stick Vacuum 25000Pa",brand="CleanPro",category="Home & Living",
     price=6999,original_price=11999,stock=19,rating=4.5,reviews=876,badge="Hot",
     image_emoji="🧹",image_color="#374151",
     description="25000Pa powerful cordless stick vacuum with 60-min battery, LED brush head, washable HEPA filter, and wall-mountable charging station.",
     highlights=_h("25000Pa suction — powerful on carpet and hard floors","60-minute battery on Eco mode","LED brush head reveals hidden dust on dark floors","Washable HEPA filter — saves on replacements","Wall-mounted docking + charging station","Converts to handheld vac in seconds"),
     specs_json=_s(Suction="25000Pa",Battery="60 min (eco) / 30 min (max)",Filter="Washable HEPA",Bin="0.8 litres",Weight="1.5kg",LEDBrush="Yes",Dock="Wall-mount charging",Warranty="2 Years"),
     image_url=_img("photo-1558317374-067fb5f30001"),
     images_json=_imgs("photo-1527515637462-cff94eecc1ac","photo-1584622781564-1d987f7333c1","photo-1615397587530-f2c5b23ef26e")),

dict(name="CrispAir Digital Air Fryer 5L",brand="CrispAir",category="Home & Living",
     price=3499,original_price=5999,stock=41,rating=4.8,reviews=3456,badge="Bestseller",
     image_emoji="🥘",image_color="#dc2626",
     description="5-litre digital air fryer with 8 preset cooking modes, 360° rapid air circulation, non-stick basket, viewing window, and 0-200°C temperature range.",
     highlights=_h("5L capacity — feeds a family of 4 easily","8 preset modes: fry, grill, roast, bake, dehydrate & more","Up to 80% less oil than traditional frying","360° Rapid Air technology — even crispy results","Non-stick basket + dishwasher-safe parts","Digital touch display + 60-min timer"),
     specs_json=_s(Capacity="5 litres",Presets="8 cooking programs",TempRange="80–200°C",Power="1700W",Timer="60 minutes",Basket="Non-stick, dishwasher-safe",Display="Digital touch",Warranty="2 Years"),
     image_url=_img("photo-1585515656973-f6e4a1c9e3ea"),
     images_json=_imgs("photo-1556909172-54557c7e4fb7","photo-1615361200141-f45040f367be","photo-1549611016-3a70d82b5040")),

dict(name="SleepWell 1000TC King Bedsheet Set",brand="SleepWell",category="Home & Living",
     price=1299,original_price=2499,stock=67,rating=4.4,reviews=1234,badge=None,
     image_emoji="🛏️",image_color="#7c3aed",
     description="1000 thread count Egyptian cotton blend bedsheet set for King beds — 1 flat sheet, 1 fitted sheet with deep pocket, and 2 pillowcases. Breathable and silky.",
     highlights=_h("1000TC Egyptian cotton blend — hotel-grade softness","Fitted sheet with 38cm deep pocket","Colour-fast dye — won't fade after washing","Hypoallergenic — suitable for sensitive skin","Set: flat sheet + fitted sheet + 2 pillow covers","Available in 10 solid colours"),
     specs_json=_s(ThreadCount="1000TC",Material="Egyptian Cotton Blend",Size="King",Includes="1 flat + 1 fitted + 2 pillowcases",DeepPocket="38cm",Colors="10 colors",Care="Machine wash warm"),
     image_url=_img("photo-1631049552057-403cdb8f0658"),
     images_json=_imgs("photo-1586105251261-72a756497a11","photo-1567016432779-094069958ea5","photo-1629131726692-1accd0c53ce0")),

dict(name="GreenHome Ceramic Plant Pot Set of 3",brand="GreenHome",category="Home & Living",
     price=699,original_price=1299,stock=89,rating=4.5,reviews=876,badge="Eco",
     image_emoji="🌿",image_color="#16a34a",
     description="Set of 3 minimalist ceramic plant pots with bamboo saucers, drainage holes, and matte finish. Ideal for succulents, herbs, and small houseplants.",
     highlights=_h("Matte finish ceramic — premium and modern","Bamboo saucers protect surfaces from water marks","Drainage hole prevents overwatering root rot","Set of 3 graduated sizes: 8cm / 12cm / 16cm","Works for indoor and outdoor plants","Easy to clean with damp cloth"),
     specs_json=_s(Material="Ceramic",Saucers="Bamboo",Sizes="8/12/16cm",DrainageHole="Yes",Finish="Matte",Colors="White/Grey/Terracotta triset",Use="Indoor/Outdoor"),
     image_url=_img("photo-1416879595882-3373a0480b5b"),
     images_json=_imgs("photo-1484154218962-a197022b5858","photo-1463936575829-25148e1db1b8","photo-1558293842-c0fd3db86157")),

dict(name="AromaHome Soy Wax Scented Candles Set of 4",brand="AromaHome",category="Home & Living",
     price=499,original_price=899,stock=123,rating=4.6,reviews=1123,badge=None,
     image_emoji="🕯️",image_color="#d97706",
     description="Set of 4 premium soy wax scented candles in hand-poured glass jars — Vanilla, Lavender, Sandalwood, and Eucalyptus. 40-hour burn time each.",
     highlights=_h("100% natural soy wax — cleaner, longer burn","40-hour burn time per candle","4 fragrances: Vanilla / Lavender / Sandalwood / Eucalyptus","Hand-poured in reusable glass jars","Cotton wick — no lead, no toxins","Presented in gift-ready box"),
     specs_json=_s(Wax="100% Natural Soy",BurnTime="40 hours/candle",Scents="Vanilla / Lavender / Sandalwood / Eucalyptus",Wick="Cotton (lead-free)",Container="Reusable glass jar",Set="4 candles",Packaging="Gift box"),
     image_url=_img("photo-1555685812-4b943f1cb0eb"),
     images_json=_imgs("photo-1608571423902-eed4a5ad8108","photo-1602928321679-560bb453f190","photo-1572804013309-59a88b7e92f1")),

# ── KITCHEN & DINING ──────────────────────────────────────────────────────────
dict(name="QuickCook Instant Pressure Cooker 6L",brand="QuickCook",category="Kitchen & Dining",
     price=4999,original_price=8999,stock=27,rating=4.7,reviews=2345,badge="Bestseller",
     image_emoji="🫕",image_color="#b91c1c",
     description="6-litre multi-function electric pressure cooker with 14 smart programs including slow cook, sauté, steam, yoghurt, and rice modes.",
     highlights=_h("14 smart cooking programs in one pot","6L capacity — feeds 4–6 people easily","Reduces cooking time by up to 70%","7-safety mechanisms — overpressure proof","Delay start + keep warm up to 10 hours","Stainless steel inner pot — dishwasher safe"),
     specs_json=_s(Capacity="6 litres",Programs="14 smart presets",Power="1000W",Safety="7 mechanisms",InnerPot="Stainless steel dishwasher-safe",Timer="24-hr delay start",KeepWarm="10 hours",Warranty="2 Years"),
     image_url=_img("photo-1556909172-54557c7e4fb7"),
     images_json=_imgs("photo-1556909114-f6e7ad7d3136","photo-1590794056226-79ef3a47ccf3","photo-1585515656973-f6e4a1c9e3ea")),

dict(name="ChefBlade Professional Knife Set 6pc",brand="ChefBlade",category="Kitchen & Dining",
     price=1499,original_price=2999,stock=43,rating=4.6,reviews=1234,badge=None,
     image_emoji="🔪",image_color="#1c1917",
     description="6-piece professional kitchen knife set in high-carbon German steel with full-tang design, triple-riveted ergonomic handles, and acrylic display block.",
     highlights=_h("High-carbon German steel — stays sharper longer","Full-tang construction — maximum strength","Triple-riveted ergonomic handle — professional grip","Set: chef's / bread / carving / paring / utility / honing rod","Acrylic display block included","Stain and rust resistant"),
     specs_json=_s(Material="High-carbon German Steel",Pieces="6 knives + 1 honing rod + 1 block",Construction="Full-tang",Handles="Triple-riveted ergonomic",HardnessRating="58 HRC",RustResistant="Yes",Warranty="Lifetime"),
     image_url=_img("photo-1518704618243-b719e5d5f2b8"),
     images_json=_imgs("photo-1556909114-f6e7ad7d3136","photo-1574672280600-4accfa5b6f98","photo-1615361200141-f45040f367be")),

dict(name="BlendMax High-Speed Blender 1000W",brand="BlendMax",category="Kitchen & Dining",
     price=2499,original_price=4499,stock=37,rating=4.5,reviews=876,badge=None,
     image_emoji="🥤",image_color="#0369a1",
     description="Professional 1000W blender with Tritan BPA-free 1.5L jar, 5 speed settings + pulse, self-cleaning mode, and stainless steel 6-blade assembly.",
     highlights=_h("1000W motor — blends ice, frozen fruit, nuts effortlessly","6 stainless steel blades — efficient no-gap design","1.5L Tritan BPA-free jar — won't crack or stain","5 speeds + pulse + self-cleaning function","Overload protection prevents motor burnout","Jar is dishwasher safe"),
     specs_json=_s(Power="1000W",Jar="1.5L Tritan BPA-free",Blades="6 stainless steel",Speeds="5 + pulse",SelfCleaning="Yes",OverloadProtection="Yes",DishwasherSafe="Jar yes",Warranty="2 Years"),
     image_url=_img("photo-1570222094114-d054a817e56b"),
     images_json=_imgs("photo-1556909114-f6e7ad7d3136","photo-1611735341450-74d61e660ad2","photo-1534482421-64566f976cfa")),

dict(name="PrecisionKitchen Digital Kitchen Scale",brand="PrecisionKitchen",category="Kitchen & Dining",
     price=599,original_price=999,stock=145,rating=4.4,reviews=2134,badge="Sale",
     image_emoji="⚖️",image_color="#374151",
     description="Precise 0.1g resolution digital kitchen scale up to 5kg, tare function, 6 unit conversions, large LCD, and slim tempered glass surface.",
     highlights=_h("0.1g precision — perfect for baking and coffee","5kg max load — handles all kitchen tasks","Tare function: weigh containers + zero out","6 unit modes: g / kg / lb / oz / ml / fl.oz","Large backlit LCD — easy to read","Stain-proof tempered glass surface"),
     specs_json=_s(Precision="0.1g",MaxLoad="5kg",Units="g/kg/lb/oz/ml/fl.oz",Display="Backlit LCD",Surface="Tempered glass",Power="2×AAA batteries",AutoOff="3 min",Warranty="1 Year"),
     image_url=_img("photo-1581244277943-fe4a9c777189"),
     images_json=_imgs("photo-1590416360583-d3a73a65e6e3","photo-1556909114-f6e7ad7d3136","photo-1499028344343-cd173ffc68a9")),

dict(name="IronChef Pre-Seasoned Cast Iron Skillet 10\"",brand="IronChef",category="Kitchen & Dining",
     price=1799,original_price=2999,stock=29,rating=4.7,reviews=987,badge=None,
     image_emoji="🍳",image_color="#292524",
     description="10-inch pre-seasoned cast iron skillet, works on all cooktops including induction, naturally non-stick when seasoned, and oven-safe to 500°C.",
     highlights=_h("Pre-seasoned with vegetable oil — ready to cook","Compatible with induction, gas, electric, ceramic, campfire","Oven-safe up to 500°C — from stovetop to oven","Retains heat 3× longer than stainless steel","Naturally non-stick with seasoning builds up over time","A lifetime investment — gets better with age"),
     specs_json=_s(Size="10 inches (25cm)",Material="Cast Iron",Seasoning="Pre-seasoned vegetable oil",OvenSafe="Up to 500°C",Compatible="All cooktops incl. induction",Weight="2.3kg",Warranty="Lifetime"),
     image_url=_img("photo-1590416360583-d3a73a65e6e3"),
     images_json=_imgs("photo-1556909114-f6e7ad7d3136","photo-1549783660-b9bcb1c8b52b","photo-1574672280600-4accfa5b6f98")),

dict(name="BrewGrind Electric Burr Coffee Grinder",brand="BrewGrind",category="Kitchen & Dining",
     price=1299,original_price=2199,stock=38,rating=4.5,reviews=654,badge=None,
     image_emoji="☕",image_color="#1c1917",
     description="Conical burr grinder with 17 grind size settings from espresso-fine to French-press-coarse, 250g hopper, and precision timer for consistent dosing.",
     highlights=_h("Conical burr — consistent grind size every time","17 grind settings: espresso to French press","250g bean hopper — week's worth of coffee","Precision timer — dose coffee by seconds","Heat-dissipating design prevents flavour loss","Removable parts are easy to clean"),
     specs_json=_s(Type="Conical burr",GrindSettings="17",Hopper="250g",Timer="Precision dosing",Power="150W",HeatControl="Yes",DishwasherParts="Grounds bin + lid",Warranty="1 Year"),
     image_url=_img("photo-1507133750040-4a8f57021571"),
     images_json=_imgs("photo-1495474472287-4d71bcdd2085","photo-1509042239860-f550ce710b93","photo-1447933601403-0c6688de566e")),

dict(name="FreshKeep Glass Food Storage Containers 8pc",brand="FreshKeep",category="Kitchen & Dining",
     price=799,original_price=1399,stock=89,rating=4.4,reviews=1543,badge="Eco",
     image_emoji="🥗",image_color="#15803d",
     description="8-piece borosilicate glass food storage set with airtight bamboo lids, oven-safe to 400°F, freezer and microwave safe, and leak-proof.",
     highlights=_h("Borosilicate glass — oven/microwave/freezer/dishwasher safe","Airtight bamboo lids with silicone seal","8 sizes from 100ml to 1.5L","Doesn't absorb odours or stain like plastic","Lead-free, BPA-free, food-grade safe","Bamboo lids are eco-friendly and sustainable"),
     specs_json=_s(Material="Borosilicate Glass",Lids="Bamboo + silicone seal",Pieces="8 containers",OvenSafe="Up to 400°F",Microwave="Yes",Freezer="Yes",Dishwasher="Yes (glass only)",Warranty="1 Year"),
     image_url=_img("photo-1464938050520-ef2270bb8ce8"),
     images_json=_imgs("photo-1556909114-f6e7ad7d3136","photo-1507048331197-7d4ac70811cf","photo-1590794056226-79ef3a47ccf3")),

dict(name="BrewArt French Press Coffee Maker 1L",brand="BrewArt",category="Kitchen & Dining",
     price=899,original_price=1699,stock=56,rating=4.6,reviews=876,badge=None,
     image_emoji="☕",image_color="#92400e",
     description="1-litre double-wall borosilicate glass French press with stainless steel plunger, ultra-fine 4-layer filter, and insulated strap handle. Makes 4–8 cups.",
     highlights=_h("Double-wall glass keeps coffee hot 2× longer","4-layer stainless steel mesh filter — zero grounds in cup","1L capacity — up to 8 cups per brew","Ergonomic insulated strap handle — safe to hold","Works for cold brew too — steep overnight in fridge","Dishwasher safe"),
     specs_json=_s(Capacity="1 litre (8 cups)",Material="Borosilicate glass + stainless steel",Filter="4-layer mesh",Plunger="Stainless steel",DishwasherSafe="Yes",ColdBrew="Yes",Warranty="1 Year"),
     image_url=_img("photo-1544787219-7f47ccb76574"),
     images_json=_imgs("photo-1495474472287-4d71bcdd2085","photo-1447933601403-0c6688de566e","photo-1509042239860-f550ce710b93")),

# ── BEAUTY & SKINCARE ─────────────────────────────────────────────────────────
dict(name="GlowLab 20% Vitamin C Glow Serum",brand="GlowLab",category="Beauty & Skincare",
     price=549,original_price=999,stock=93,rating=4.6,reviews=2109,badge="New",
     image_emoji="✨",image_color="#f59e0b",
     description="20% stabilised L-Ascorbic Acid serum with Hyaluronic Acid and Niacinamide. Fades dark spots, boosts collagen, and delivers a visible glow in 4 weeks.",
     highlights=_h("20% Vitamin C — maximum brightening potency","Hyaluronic Acid for deep skin hydration","Niacinamide minimises pores and evens tone","Dermatologist tested — all skin types","Cruelty-free, paraben-free, fragrance-free","Results in 4 weeks of consistent use"),
     specs_json=_s(Brand="GlowLab",Volume="30ml",VitaminC="20% Stabilised L-Ascorbic Acid",KeyIngredients="HA + Niacinamide",CrueltyFree="Yes",ParabenFree="Yes",DermatologistTested="Yes",ShelfLife="12 months unopened"),
     image_url=_img("photo-1620916566398-39f1143ab7be"),
     images_json=_imgs("photo-1556228578-8c89e6adf883","photo-1598440947619-2c35fc9aa908","photo-1611080626919-7cf5a9dbab12")),

dict(name="ProStyle Professional Hair Dryer 2400W",brand="ProStyle",category="Beauty & Skincare",
     price=1899,original_price=3499,stock=44,rating=4.7,reviews=1543,badge=None,
     image_emoji="💨",image_color="#db2777",
     description="Salon-grade 2400W hair dryer with ionic technology, 3 heat settings, 2 speed modes, cool-shot button, foldable handle, and concentrator + diffuser attachments.",
     highlights=_h("2400W salon-grade power — dries hair 50% faster","Ionic technology reduces frizz and static","3 heat + 2 speed settings for all hair types","Cool-shot button locks in your style","Foldable handle for compact travel storage","Includes concentrator nozzle + diffuser attachment"),
     specs_json=_s(Power="2400W",Technology="Ionic + Far Infrared",HeatSettings="3",SpeedModes="2",CoolShot="Yes",Handle="Foldable",Attachments="Concentrator + Diffuser",Warranty="1 Year"),
     image_url=_img("photo-1522338242992-e1a54906a8da"),
     images_json=_imgs("photo-1527799820374-dcf8d9d4a388","photo-1492106087820-71f1a00d2b11","photo-1559599101-f09722fb4948")),

dict(name="TanShield SPF 50+ Sunscreen Lotion 100ml",brand="TanShield",category="Beauty & Skincare",
     price=399,original_price=699,stock=167,rating=4.5,reviews=2341,badge="Sale",
     image_emoji="🌞",image_color="#f59e0b",
     description="Broad-spectrum SPF 50+ PA+++ sunscreen with lightweight gel formula, no white cast, matte finish, and 3-in-1 moisturiser, primer, and UV filter.",
     highlights=_h("SPF 50+ PA+++ — protects from UVA + UVB rays","Lightweight gel — absorbs in 30 seconds, no greasiness","Zero white cast — suitable for all skin tones","Doubles as makeup primer + moisturiser","Water resistant for 80 minutes","Dermatologist tested, non-comedogenic"),
     specs_json=_s(SPF="50+ PA+++",Volume="100ml",Type="Lightweight gel",WhiteCast="None",WaterResistant="80 min",SkinType="All (non-comedogenic)",DermatologistTested="Yes"),
     image_url=_img("photo-1556228720-195a672e8a03"),
     images_json=_imgs("photo-1598440947619-2c35fc9aa908","photo-1620916566398-39f1143ab7be","photo-1611080626919-7cf5a9dbab12")),

dict(name="LipLux Matte Lipstick Collection 8 Shades",brand="LipLux",category="Beauty & Skincare",
     price=699,original_price=1299,stock=134,rating=4.4,reviews=1876,badge="Hot",
     image_emoji="💄",image_color="#e11d48",
     description="Set of 8 long-stay creamy matte lipsticks in a curated wearable palette — from MLBB nudes to bold reds and berries. 12-hour wear, no feathering.",
     highlights=_h("8 curated shades: nudes, corals, reds, and berries","12-hour long wear — no fading or feathering","Creamy matte formula — comfortable, not drying","Enriched with Vitamin E for lip conditioning","Suitable for all skin undertones","Presented in magnetic closure gift box"),
     specs_json=_s(Shades="8",Formula="Creamy Matte",WearTime="12 hours",VitaminE="Yes",Finish="Matte no-feather",Packaging="Magnetic gift box",CrueltyFree="Yes"),
     image_url=_img("photo-1586495777744-4e6232bf2f9b"),
     images_json=_imgs("photo-1559154698-82d6d6e9765b","photo-1596462502278-27bfdc403348","photo-1519863695799-c7f3c2c30ff2")),

dict(name="NightGlow Retinol + Peptide Night Cream",brand="NightGlow",category="Beauty & Skincare",
     price=799,original_price=1499,stock=76,rating=4.6,reviews=987,badge=None,
     image_emoji="🌙",image_color="#7c3aed",
     description="0.1% retinol night cream fortified with peptides, niacinamide, and hyaluronic acid to visibly reduce fine lines, firm skin, and improve texture overnight.",
     highlights=_h("0.1% Retinol — clinically proven to reduce wrinkles","Peptide complex boosts collagen production","Niacinamide firms and brightens skin tone","Hyaluronic Acid delivers overnight hydration","Fragrance-free — suitable for sensitive skin","pH-balanced, dermatologist-tested formula"),
     specs_json=_s(Retinol="0.1%",KeyActives="Peptides + Niacinamide + HA",Volume="50ml",Use="Night only",SkinType="All, incl. sensitive",FragranceFree="Yes",DermatologistTested="Yes"),
     image_url=_img("photo-1556228578-8c89e6adf883"),
     images_json=_imgs("photo-1620916566398-39f1143ab7be","photo-1598440947619-2c35fc9aa908","photo-1572804013309-59a88b7e92f1")),

dict(name="PureGlow Activated Charcoal Face Wash 150ml",brand="PureGlow",category="Beauty & Skincare",
     price=299,original_price=499,stock=213,rating=4.3,reviews=2134,badge="Sale",
     image_emoji="🫧",image_color="#1c1917",
     description="Deep-pore cleansing charcoal face wash with salicylic acid, tea tree oil, and green clay to control oil, unclog pores, and prevent breakouts.",
     highlights=_h("Activated charcoal draws out deep-pore impurities","2% Salicylic Acid — exfoliates and unclogs pores","Tea Tree Oil has natural antibacterial action","Green Clay absorbs excess oil — matte finish","Sulphate-free and paraben-free formula","150ml — approximately 2-month supply"),
     specs_json=_s(KeyIngredients="Activated Charcoal + 2% Salicylic Acid + Tea Tree + Green Clay",Volume="150ml",SkinType="Oily/Combination/Acne-prone",SulphateFree="Yes",ParabenFree="Yes",CrueltyFree="Yes",Use="Twice daily"),
     image_url=_img("photo-1556228578-8c89e6adf883"),
     images_json=_imgs("photo-1598440947619-2c35fc9aa908","photo-1620916566398-39f1143ab7be","photo-1611080626919-7cf5a9dbab12")),

dict(name="ManGroomed Premium Beard Grooming Kit",brand="ManGroomed",category="Beauty & Skincare",
     price=799,original_price=1499,stock=112,rating=4.5,reviews=1432,badge=None,
     image_emoji="🧔",image_color="#1c1917",
     description="Complete beard grooming kit: electric trimmer, beard oil 30ml, beard balm 50g, boar bristle brush, and stainless steel comb in a premium leather zip pouch.",
     highlights=_h("5-piece complete beard care kit","Electric trimmer: 20 length settings, USB-C charging","Beard oil with argan + jojoba — moisturises and softens","Beard balm with shea butter — shapes and holds","Boar bristle brush exfoliates and distributes oil evenly","Presented in premium leather zip pouch"),
     specs_json=_s(Pieces="5 (trimmer + oil + balm + brush + comb)",TrimmerSettings="20 lengths",Charging="USB-C",OilVolume="30ml (argan + jojoba)",BalmWeight="50g (shea butter)",Pouch="Genuine leather zip",Warranty="1 Year"),
     image_url=_img("photo-1585747860715-2ba37e788b70"),
     images_json=_imgs("photo-1527799820374-dcf8d9d4a388","photo-1559599101-f09722fb4948","photo-1622560480605-d83c853bc5c3")),

dict(name="ShineAway Anti-Frizz Hair Serum 50ml",brand="ShineAway",category="Beauty & Skincare",
     price=449,original_price=799,stock=178,rating=4.4,reviews=1234,badge=None,
     image_emoji="✨",image_color="#d97706",
     description="Lightweight argan oil hair serum that controls frizz, adds mirror shine, protects from heat up to 230°C, and leaves hair silky — not greasy.",
     highlights=_h("Moroccan Argan Oil — frizz control and shine","Heat protection up to 230°C — safe before styling","Non-greasy ultra-light formula","Works on all hair types: straight, wavy, curly","Results: silky, manageable hair in 30 seconds","20-day supply in one 50ml bottle"),
     specs_json=_s(KeyIngredient="Moroccan Argan Oil",Volume="50ml",HeatProtect="Up to 230°C",HairType="All types",Finish="Non-greasy shine",CrueltyFree="Yes",ParabenFree="Yes"),
     image_url=_img("photo-1527799820374-dcf8d9d4a388"),
     images_json=_imgs("photo-1522338242992-e1a54906a8da","photo-1559599101-f09722fb4948","photo-1492106087820-71f1a00d2b11")),

dict(name="StyleKohl Smudge-Proof Kajal Eyeliner",brand="StyleKohl",category="Beauty & Skincare",
     price=199,original_price=349,stock=312,rating=4.5,reviews=3421,badge="Sale",
     image_emoji="👁️",image_color="#1c1917",
     description="Intense black waterproof kajal with twist-up retractable design, dermatologically tested, and 24-hour smudge-proof formula — safe for waterline use.",
     highlights=_h("Intense jet-black pigment — one-stroke opacity","24-hour waterproof + smudge-proof formula","Twist-up retractable — no sharpening needed","Safe for waterline and tightline application","Enriched with Vitamin E — gentle on eyes","Dermatologically and ophthalmologically tested"),
     specs_json=_s(Color="Intense Jet Black",WearTime="24 hours",Waterproof="Yes",Formula="Retractable twist-up",Waterline="Safe",VitaminE="Yes",DermatologistTested="Yes",OphthalmologistTested="Yes"),
     image_url=_img("photo-1583241475880-083f84a5e35e"),
     images_json=_imgs("photo-1596462502278-27bfdc403348","photo-1559154698-82d6d6e9765b","photo-1519863695799-c7f3c2c30ff2")),

dict(name="GlowBase Long-Stay Compact Foundation",brand="GlowBase",category="Beauty & Skincare",
     price=599,original_price=999,stock=98,rating=4.4,reviews=1345,badge=None,
     image_emoji="💅",image_color="#d97706",
     description="Buildable coverage compact foundation with SPF 20, matte finish, 24-hour transfer-proof wear, and 20 shades for all skin tones.",
     highlights=_h("Buildable coverage: light to full in layers","SPF 20 built-in daily UV protection","24-hour transfer and sweat proof","20 inclusive shades for all undertones","Paraben-free, non-comedogenic formula","Includes dual-sided velvet puff applicator"),
     specs_json=_s(Coverage="Buildable",SPF="20",WearTime="24 hours",Finish="Matte",Shades="20",Applicator="Dual-sided velvet puff",ParabenFree="Yes",NonComedogenic="Yes"),
     image_url=_img("photo-1512496015851-a90fb38ba796"),
     images_json=_imgs("photo-1583241475880-083f84a5e35e","photo-1596462502278-27bfdc403348","photo-1586495777744-4e6232bf2f9b")),

# ── SPORTS & FITNESS ──────────────────────────────────────────────────────────
dict(name="ZenYoga Premium Anti-Slip Yoga Mat 6mm",brand="ZenYoga",category="Sports & Fitness",
     price=799,original_price=1499,stock=98,rating=4.7,reviews=3210,badge="Bestseller",
     image_emoji="🧘",image_color="#16a34a",
     description="6mm thick TPE yoga mat with alignment lines, double-sided texture, moisture-wicking surface, and carrying strap. Eco-friendly, non-toxic, and odourless.",
     highlights=_h("6mm thick — optimal joint cushioning","Double-sided texture: grip side + smooth side","Alignment lines for perfect pose positioning","Moisture-wicking top layer absorbs sweat","Eco-friendly TPE — no PVC, no toxic chemicals","Includes carrying strap + wash instructions"),
     specs_json=_s(Thickness="6mm",Material="Eco-TPE",Dimensions="183×61cm",DoubleSided="Yes",AlignmentLines="Yes",Weight="1.1kg",Colors="8 colors",Warranty="1 Year"),
     image_url=_img("photo-1545205597-3d9d02c29597"),
     images_json=_imgs("photo-1599447421416-3414f7f1b1c7","photo-1601925228519-fa03e3db949e","photo-1607962837359-5e7e89f86776")),

dict(name="FitBand Resistance Band Set 5 Levels",brand="FitBand",category="Sports & Fitness",
     price=499,original_price=999,stock=178,rating=4.6,reviews=2341,badge="Hot",
     image_emoji="💪",image_color="#ef4444",
     description="Set of 5 resistance bands from 10lb to 50lb, made from natural latex, anti-snap, colour-coded by resistance level, and with non-slip grip pattern.",
     highlights=_h("5 resistance levels: 10/20/30/40/50 lb","Natural latex — snap-resistant, durable","Colour-coded: easy to select the right resistance","Anti-slip ridged grip — stays in place","Use for squats, glutes, arms, back, yoga","Includes mesh carry bag"),
     specs_json=_s(Pieces="5 bands",Resistance="10/20/30/40/50 lb",Material="Natural Latex",ColorCoded="Yes",AntiSnap="Yes",Length="60cm flat loop",Includes="Mesh carry bag",Warranty="6 months"),
     image_url=_img("photo-1598971861713-54ad16a7e72e"),
     images_json=_imgs("photo-1571019614242-c5c5dee9f50b","photo-1517836357463-d25dfeac3438","photo-1548690596-f1722c190938")),

dict(name="AquaSteel Insulated Water Bottle 1L",brand="AquaSteel",category="Sports & Fitness",
     price=599,original_price=999,stock=213,rating=4.5,reviews=2876,badge=None,
     image_emoji="🚰",image_color="#0891b2",
     description="1-litre double-wall vacuum insulated stainless steel water bottle that keeps drinks cold 24 hours or hot 12 hours. BPA-free, leakproof lid, and carrying loop.",
     highlights=_h("24-hour cold / 12-hour hot retention","Double-wall vacuum insulation — no condensation","18/8 premium food-grade stainless steel","Wide-mouth opening — fits ice cubes + easy cleaning","Leakproof lid with secure seal + carrying loop","Fits standard cup holders in cars"),
     specs_json=_s(Capacity="1 litre",Material="18/8 Stainless Steel",Insulation="Double-wall vacuum",ColdRetention="24 hours",HotRetention="12 hours",Lid="Leakproof loop cap",BPA="BPA-free",Colors="8 colors"),
     image_url=_img("photo-1602143407151-7111542de6e8"),
     images_json=_imgs("photo-1497436072909-60f360e1d4b1","photo-1532938911079-1b06ac7ceec7","photo-1555658636-6e4a3526b78d")),

dict(name="FitMix Leak-Proof Protein Shaker 750ml",brand="FitMix",category="Sports & Fitness",
     price=349,original_price=699,stock=234,rating=4.4,reviews=1876,badge="Sale",
     image_emoji="🥛",image_color="#059669",
     description="750ml Tritan BPA-free protein shaker with stainless steel blender ball, dual powder + supplement compartment, and leak-proof screw lid.",
     highlights=_h("750ml Tritan BPA-free main shaker bottle","Stainless steel blender ball — lump-free shakes","Dual storage: powder pouch + pill storage","Leak-proof screw-on lid — take it anywhere","Dishwasher safe (top rack)","Graduated markings in ml + oz"),
     specs_json=_s(Capacity="750ml",Material="Tritan BPA-free",BlenderBall="Stainless steel",DualStorage="Yes",DishwasherSafe="Yes (top rack)",Markings="ml + oz",Colors="6 colors"),
     image_url=_img("photo-1571748982800-fa51b89d0d4b"),
     images_json=_imgs("photo-1517836357463-d25dfeac3438","photo-1551422376-b8e25c7cb13b","photo-1580910051074-3eb694886505")),

dict(name="JumpFit Speed Skipping Rope",brand="JumpFit",category="Sports & Fitness",
     price=299,original_price=599,stock=312,rating=4.3,reviews=1543,badge="Sale",
     image_emoji="🎗️",image_color="#f97316",
     description="Adjustable speed skipping rope with tangle-free ball-bearing handles, 3m PVC wire (adjustable down to 2m), and comfortable foam grips.",
     highlights=_h("Ball-bearing handles — fast spin, tangle-free","Adjustable 3m rope — fits all heights","Foam-wrapped ergonomic anti-slip handles","Suitable for speed jumping, double-unders, HIIT","Lightweight at just 180g — take anywhere","Includes travel pouch"),
     specs_json=_s(RopeLength="3m adjustable",Bearings="Ball-bearing anti-tangle",Handles="Foam grip ergonomic",Weight="180g",Material="PVC wire",RopeType="Speed",Includes="Travel pouch"),
     image_url=_img("photo-1601422407692-ec4eeec1d9b3"),
     images_json=_imgs("photo-1571019614242-c5c5dee9f50b","photo-1598971861713-54ad16a7e72e","photo-1517836357463-d25dfeac3438")),

dict(name="PowerLift Adjustable Dumbbell Set 10kg",brand="PowerLift",category="Sports & Fitness",
     price=2499,original_price=4999,stock=27,rating=4.7,reviews=876,badge="New",
     image_emoji="🏋️",image_color="#7c3aed",
     description="Space-saving adjustable dumbbell set: one pair that adjusts from 2.5kg to 10kg per hand via quick-lock dial mechanism. Replaces 8 pairs of dumbbells.",
     highlights=_h("Adjusts 2.5kg to 10kg in 2.5kg increments","Replaces 8 pairs of fixed dumbbells","Quick-lock dial mechanism — change weight in 3 seconds","Non-slip knurled chrome handle","Durable ABS plastic + steel construction","Compact storage base included per dumbbell"),
     specs_json=_s(WeightRange="2.5kg–10kg (per dumbbell)",Increments="2.5kg",Mechanism="Quick-lock dial",Handle="Knurled chrome",Material="ABS + Steel",Base="Included",Warranty="2 Years"),
     image_url=_img("photo-1534438327276-14e5300c3a48"),
     images_json=_imgs("photo-1581009146145-b5ef050c2e1e","photo-1517836357463-d25dfeac3438","photo-1548690596-f1722c190938")),

dict(name="CoreFit Ab Roller Wheel + Kneepads",brand="CoreFit",category="Sports & Fitness",
     price=449,original_price=899,stock=134,rating=4.5,reviews=1234,badge=None,
     image_emoji="💪",image_color="#dc2626",
     description="Double ab roller wheel with extra-wide 15cm stability wheels, non-slip foam handles, and thick kneepads for comfortable core training.",
     highlights=_h("Double wheel for maximum stability","Extra-wide 15cm wheel design — won't wobble","Foam-wrapped ergonomic handles","Non-slip rubber wheel tread — protects floor","Thick kneepads included (anti-skid)","Compact for any workout space"),
     specs_json=_s(WheelWidth="15cm double wheel",Handles="Foam ergonomic",WheelTread="Non-slip rubber",Kneepads="Included",Weight="620g",Compatibility="All floor types"),
     image_url=_img("photo-1571019614242-c5c5dee9f50b"),
     images_json=_imgs("photo-1517836357463-d25dfeac3438","photo-1598971861713-54ad16a7e72e","photo-1534438327276-14e5300c3a48")),

dict(name="SportBag Waterproof Gym Duffel Bag 40L",brand="SportBag",category="Sports & Fitness",
     price=1199,original_price=1999,stock=56,rating=4.5,reviews=987,badge=None,
     image_emoji="🎒",image_color="#1e3a5f",
     description="40L waterproof gym bag with wet/dry compartment separator, shoe tunnel, laptop sleeve, and multiple pockets. Removable shoulder strap.",
     highlights=_h("40L roomy main compartment for all gym gear","Separate wet/dry compartments — no damp smell","Dedicated shoe tunnel at bottom — keeps separate","Padded laptop sleeve (fits 15\" laptop)","Removable padded shoulder strap + top carry handle","Water-resistant 600D polyester exterior"),
     specs_json=_s(Capacity="40 litres",Material="Water-resistant 600D Polyester",WetDryCompartment="Yes",ShoeTunnel="Yes",LaptopFit="15 inch",Straps="Shoulder + top handle",Colors="Black/Navy/Grey",Warranty="1 Year"),
     image_url=_img("photo-1553558008258-2c3e3e0ee618"),
     images_json=_imgs("photo-1622560480605-d83c853bc5c3","photo-1553062407-98eeb64c6a45","photo-1547622660-f6c0b60b1b97")),

dict(name="RollEase High-Density Foam Roller 60cm",brand="RollEase",category="Sports & Fitness",
     price=749,original_price=1499,stock=89,rating=4.6,reviews=765,badge=None,
     image_emoji="🏃",image_color="#16a34a",
     description="60cm high-density EVA foam roller with grid texture for myofascial release, post-workout recovery, and physical therapy. Supports up to 120kg.",
     highlights=_h("High-density EVA foam — firm but gentle","Grid texture targets pressure points effectively","60cm length = full back and leg coverage","Hollow core design is lightweight at 350g","Supports up to 120kg user weight","Works for: quads, hamstrings, IT band, back, calves"),
     specs_json=_s(Length="60cm",Diameter="15cm",Material="High-density EVA",TextureType="Grid pattern",Weight="350g hollow core",MaxLoad="120kg",Colors="4 colors"),
     image_url=_img("photo-1611162617213-7d7a39e9b1d6"),
     images_json=_imgs("photo-1571019614242-c5c5dee9f50b","photo-1548690596-f1722c190938","photo-1517836357463-d25dfeac3438")),

dict(name="ArmbandFit Running Phone Armband",brand="ArmbandFit",category="Sports & Fitness",
     price=299,original_price=599,stock=198,rating=4.3,reviews=1432,badge="Sale",
     image_emoji="📱",image_color="#0891b2",
     description="Universal running phone armband fits phones up to 7-inch, with transparent touchscreen window, key pocket, reflective strips, and adjustable Velcro strap.",
     highlights=_h("Fits phones up to 7\" — universal compatibility","Transparent TPU window — full touchscreen use","Reflective strips for low-light visibility and safety","Zippered key/card pocket","Adjustable Velcro strap — fits any arm size","Sweat-proof neoprene material"),
     specs_json=_s(PhoneFit="Up to 7 inch",Material="Sweat-proof Neoprene",Window="Transparent TPU touch-through",Pocket="Zippered key/card",Reflective="Yes",Strap="Adjustable Velcro",Colors="6 colors"),
     image_url=_img("photo-1575311373937-040b8058069f"),
     images_json=_imgs("photo-1571019613454-1cb2f99b2d8b","photo-1601925228519-fa03e3db949e","photo-1607962837359-5e7e89f86776")),

# ── HEALTH & WELLNESS ─────────────────────────────────────────────────────────
dict(name="MassGain Whey Protein Chocolate 1kg",brand="MassGain",category="Health & Wellness",
     price=1999,original_price=2999,stock=67,rating=4.7,reviews=3210,badge="Bestseller",
     image_emoji="💪",image_color="#92400e",
     description="25g protein per serving whey concentrate from grass-fed cows, enriched with BCAA, digestive enzymes, and available in rich chocolate, vanilla, and strawberry.",
     highlights=_h("25g protein per serving (30g scoop)","From grass-fed cows — cleaner protein source","Enriched with BCAA for muscle recovery","Digestive enzyme blend — easy on stomach","30 servings per 1kg pack","Available in Chocolate / Vanilla / Strawberry"),
     specs_json=_s(ProteinPerServing="25g",ServingSize="30g 1 scoop",Servings="30 per 1kg",Source="Grass-fed whey concentrate",BCAA="Yes",DigestiveEnzymes="Yes",Certifications="FSSAI approved",Flavors="Chocolate/Vanilla/Strawberry"),
     image_url=_img("photo-1579722820308-d74e571900a9"),
     images_json=_imgs("photo-1517838277536-f5f99be501cd","photo-1558618666-fcd25c85cd64","photo-1584308666744-24d5c474f2ae")),

dict(name="VitaMax Complete Daily Multivitamin 60 Tabs",brand="VitaMax",category="Health & Wellness",
     price=449,original_price=799,stock=178,rating=4.5,reviews=1543,badge=None,
     image_emoji="💊",image_color="#16a34a",
     description="Comprehensive once-a-day multivitamin with 23 vitamins and minerals, including Vitamin D3, B12, zinc, iron, and Omega-3 for complete daily nutrition.",
     highlights=_h("23 essential vitamins and minerals in one tablet","Vitamin D3 1000IU — critical for immunity and bones","B12 1000mcg — supports energy and nerve health","Chelated minerals for 3× better absorption","One tablet per day — convenient routine","FSSAI approved, GMP certified, no artificial colours"),
     specs_json=_s(Tablets="60",Dose="1 per day",KeyNutrients="Vit D3/B12/Zinc/Iron/Omega-3",Minerals="Chelated form",CertifiedBy="FSSAI + GMP",ArtificialColors="No",Preservatives="No"),
     image_url=_img("photo-1550572017-37b370fd55b3"),
     images_json=_imgs("photo-1584308666744-24d5c474f2ae","photo-1616671276441-2f2c277b8bf6","photo-1579722820308-d74e571900a9")),

dict(name="HerbalPure Giloy + Ashwagandha Capsules 60ct",brand="HerbalPure",category="Health & Wellness",
     price=349,original_price=599,stock=213,rating=4.6,reviews=2109,badge="Hot",
     image_emoji="🌿",image_color="#15803d",
     description="Certified organic Giloy and Ashwagandha capsules, 500mg each, to boost immunity, reduce stress, improve stamina, and support overall well-being.",
     highlights=_h("Giloy (Tinospora Cordifolia) — Ayurvedic immunity booster","Ashwagandha (KSM-66® extract) — reduces cortisol/stress","500mg per capsule — clinical dose","60 capsules — 30-day supply (2/day)","100% organic, no fillers or artificial additives","FSSAI approved and GMP manufactured"),
     specs_json=_s(Capsules="60",PerCapsule="500mg (250mg Giloy + 250mg Ashwagandha KSM-66)",Dose="2 per day",CertifiedOrganic="Yes",Fillers="None",Certifications="FSSAI + GMP + USDA Organic",ShelfLife="24 months"),
     image_url=_img("photo-1584308666744-24d5c474f2ae"),
     images_json=_imgs("photo-1550572017-37b370fd55b3","photo-1579722820308-d74e571900a9","photo-1616671276441-2f2c277b8bf6")),

dict(name="OmegaPure Omega-3 Fish Oil 1000mg 60 Caps",brand="OmegaPure",category="Health & Wellness",
     price=399,original_price=699,stock=167,rating=4.5,reviews=1567,badge=None,
     image_emoji="🐟",image_color="#0891b2",
     description="High-potency 1000mg fish oil capsules with 300mg EPA + DHA per serving, sourced from deep-sea cold-water fish, molecularly distilled, and mercury-tested.",
     highlights=_h("1000mg fish oil with 300mg active EPA + DHA","Cold-water deep-sea sourced — naturally rich","Molecularly distilled — mercury and heavy metal tested","Enteric coated — no fishy burps or aftertaste","60 capsules — 2-month supply","Supports heart, brain, and joint health"),
     specs_json=_s(Capsules="60",FishOil="1000mg per capsule",EPA_DHA="300mg per capsule",Source="Cold-water deep-sea",MolecularlyDistilled="Yes",MercuryTested="Yes",EntericCoated="Yes"),
     image_url=_img("photo-1616671276441-2f2c277b8bf6"),
     images_json=_imgs("photo-1550572017-37b370fd55b3","photo-1584308666744-24d5c474f2ae","photo-1579722820308-d74e571900a9")),

dict(name="CareDigi Digital Blood Pressure Monitor",brand="CareDigi",category="Health & Wellness",
     price=1999,original_price=3499,stock=43,rating=4.7,reviews=1234,badge=None,
     image_emoji="❤️",image_color="#ef4444",
     description="Clinically validated upper arm BP monitor with large LCD, irregular heartbeat detection, 90-reading memory for 2 users, and WHO classification indicator.",
     highlights=_h("Clinically validated accuracy (±3mmHg)","WHO blood pressure classification colour indicator","Detects irregular heartbeat automatically","90-reading memory for 2 users (45 each)","Large backlit LCD — easy to read","One-button operation — simple for seniors"),
     specs_json=_s(Validation="Clinically validated",Accuracy="±3mmHg",Memory="90 readings (2 users)",Arrhythmia="Auto-detection",Display="Large backlit LCD",Cuff="22–42cm arm circumference",Power="4×AA or USB-C",Warranty="3 Years"),
     image_url=_img("photo-1576091160550-2173dba999ef"),
     images_json=_imgs("photo-1584308666744-24d5c474f2ae","photo-1550572017-37b370fd55b3","photo-1616671276441-2f2c277b8bf6")),

dict(name="PulseCheck Finger Pulse Oximeter",brand="PulseCheck",category="Health & Wellness",
     price=699,original_price=1299,stock=134,rating=4.5,reviews=987,badge=None,
     image_emoji="💓",image_color="#ef4444",
     description="Fingertip pulse oximeter with dual-colour OLED display, measures SpO2 and pulse rate, auto power-off, lightweight at 45g, and includes AAA batteries.",
     highlights=_h("Measures SpO2 (oxygen saturation) + pulse rate","Dual-colour OLED display — clearly visible in all light","Auto power-off after 8 sec of no finger","Results in just 15 seconds","Lightweight — only 45g with batteries","Includes lanyard + AAA batteries + carry pouch"),
     specs_json=_s(Measurement="SpO2 + Pulse Rate",PrecisionSpO2="±2%",PrecisionPR="±2bpm",Display="Dual-colour OLED",AutoOff="8 seconds",Weight="45g",Battery="2×AAA included",Warranty="1 Year"),
     image_url=_img("photo-1584744982491-665216d29c47"),
     images_json=_imgs("photo-1576091160550-2173dba999ef","photo-1584308666744-24d5c474f2ae","photo-1550572017-37b370fd55b3")),

dict(name="HeatEase XL Electric Heating Pad",brand="HeatEase",category="Health & Wellness",
     price=899,original_price=1599,stock=76,rating=4.6,reviews=1432,badge=None,
     image_emoji="🔥",image_color="#dc2626",
     description="XL 40×50cm moist heat therapy pad with 6 temperature settings, 2-hour auto shut-off, machine-washable cover, and fast heat-up in 30 seconds.",
     highlights=_h("Extra-large 40×50cm — covers full back or abdomen","6 temperature settings: 40°C to 65°C","Moist heat option — penetrates deeper than dry heat","Heats up in 30 seconds — ready fast","2-hour auto shut-off safety protection","Removable machine-washable soft flannel cover"),
     specs_json=_s(Size="40×50cm XL",TempSettings="6 (40–65°C)",HeatUpTime="30 seconds",HeatType="Dry + Moist",AutoShutOff="2 hours",Cover="Removable machine-washable",Power="55W",Warranty="1 Year"),
     image_url=_img("photo-1559598467-f8b76c8155d0"),
     images_json=_imgs("photo-1616671276441-2f2c277b8bf6","photo-1584308666744-24d5c474f2ae","photo-1550572017-37b370fd55b3")),

dict(name="ImmuneBoost Daily Defence Syrup 200ml",brand="ImmuneBoost",category="Health & Wellness",
     price=299,original_price=499,stock=189,rating=4.3,reviews=876,badge=None,
     image_emoji="🍃",image_color="#15803d",
     description="Ayurvedic immunity syrup with Tulsi, Amla, Giloy, and Neem extracts. Sugar-free, alcohol-free, suitable for the entire family including children above 5 years.",
     highlights=_h("5 Ayurvedic herbs: Tulsi, Amla, Giloy, Neem, Turmeric","No sugar, no alcohol — safe for daily use","Suitable for adults and children above 5","Helps fight seasonal infections and cold/flu","200ml — up to 40 days supply for adults","FSSAI approved, GMP certified"),
     specs_json=_s(Volume="200ml",KeyHerbs="Tulsi/Amla/Giloy/Neem/Turmeric",SugarFree="Yes",AlcoholFree="Yes",AgeGroup="5 years and above",Dose="5ml twice daily",Certifications="FSSAI + GMP",ShelfLife="24 months"),
     image_url=_img("photo-1573461160327-2c87a7413eca"),
     images_json=_imgs("photo-1584308666744-24d5c474f2ae","photo-1616671276441-2f2c277b8bf6","photo-1550572017-37b370fd55b3")),

# ── STATIONERY ────────────────────────────────────────────────────────────────
dict(name="InkMate Premium Gel Pen Set 12 Colors",brand="InkMate",category="Stationery",
     price=299,original_price=499,stock=234,rating=4.5,reviews=2109,badge="Sale",
     image_emoji="✏️",image_color="#6366f1",
     description="12-piece gel pen set in vibrant colours with 0.7mm tip, smooth ink flow, quick-dry formula, and metal clip. Ideal for journaling, art, and school/office.",
     highlights=_h("12 vivid colours including metallic and neon shades","0.7mm fine tip — smooth, consistent ink flow","Quick-dry ink — no smudging while writing","Metal clip barrel — sturdy and premium feel","Works on: regular paper, cardstock, sticky notes","Refillable design — eco-friendly long-term use"),
     specs_json=_s(Pieces="12 pens",TipSize="0.7mm",Ink="Quick-dry gel",Colors="Standard + metallic + neon",Clip="Metal",Refillable="Yes",Warranty="6 months"),
     image_url=_img("photo-1455390582262-044cdead277a"),
     images_json=_imgs("photo-1491841573634-28140fc7ced7","photo-1503736334956-4c8f8e4a946d","photo-1517697471339-4aa32003c11a")),

dict(name="ClassicNotes Genuine Leather Journal A5",brand="ClassicNotes",category="Stationery",
     price=549,original_price=999,stock=78,rating=4.7,reviews=1234,badge="Hot",
     image_emoji="📗",image_color="#78350f",
     description="Full-grain leather hardcover A5 journal with 200 acid-free ivory pages, ribbon bookmark, pen loop, and magnetic closure strap.",
     highlights=_h("Full-grain genuine leather cover — ages beautifully","200 pages of thick 100gsm acid-free ivory paper","Ribbon bookmark + pen loop + magnetic strap","Lay-flat binding for comfortable writing","Suitable for pen, pencil, and fine liners","Gift-boxed — perfect as a present"),
     specs_json=_s(Material="Full-grain Genuine Leather",Size="A5 (21×14.8cm)",Pages="200 (100gsm acid-free ivory)",Binding="Lay-flat stitched",Extras="Ribbon bookmark + pen loop + magnetic strap",Packaging="Gift box",Warranty="30-day return"),
     image_url=_img("photo-1517842264405-72bb906a1936"),
     images_json=_imgs("photo-1531346878377-a5be20888e57","photo-1544947950-fa07a98d237f","photo-1465188162913-8fb5709d6d57")),

dict(name="StickyOrg Colour Sticky Notes Set 10 Pads",brand="StickyOrg",category="Stationery",
     price=249,original_price=449,stock=312,rating=4.3,reviews=876,badge="Sale",
     image_emoji="📝",image_color="#f59e0b",
     description="10-pad sticky notes set with 5 shapes (3×3, 4×4, flag, arrow, lined), 100 sheets each, repositionable adhesive, and 5 vibrant colour families.",
     highlights=_h("10 pads × 100 sheets = 1000 sticky notes total","5 different shapes and sizes for varied use","Repositionable adhesive — sticks and re-sticks","No residue left on surfaces","Vibrant colours: yellow, blue, green, pink, orange","Works on: screens, books, walls, whiteboards, desks"),
     specs_json=_s(Pads="10",SheetsPerPad="100",TotalSheets="1000",Shapes="5 (square/large/flag/arrow/lined)",Adhesive="Repositionable no-residue",Colors="5 color families",Sizes="75×75mm / 102×102mm / various"),
     image_url=_img("photo-1484480974693-6ca0a78fb36b"),
     images_json=_imgs("photo-1517697471339-4aa32003c11a","photo-1455390582262-044cdead277a","photo-1503736334956-4c8f8e4a946d")),

dict(name="ArtDraw Professional Drawing Pencil Set 24pc",brand="ArtDraw",category="Stationery",
     price=349,original_price=699,stock=134,rating=4.6,reviews=987,badge=None,
     image_emoji="✏️",image_color="#92400e",
     description="24 professional graphite drawing pencils from 9H (hardest) to 9B (softest), in a rolling canvas case with eraser, pencil extender, and sharpener.",
     highlights=_h("24 grades: 9H to 9B — complete drawing range","Premium cedar wood casing — sharpens cleanly","Includes sharpener, eraser, and pencil extender","Canvas roll case keeps everything organised","Professional quality used by art students and pros","Break-resistant clay graphite core"),
     specs_json=_s(Pieces="24 pencils + sharpener + eraser + extender",Grades="9H to 9B",Casing="Cedar wood",Core="Break-resistant clay graphite",Case="Canvas roll",BrandTier="Professional grade",Warranty="30-day return"),
     image_url=_img("photo-1503736334956-4c8f8e4a946d"),
     images_json=_imgs("photo-1455390582262-044cdead277a","photo-1491841573634-28140fc7ced7","photo-1517697471339-4aa32003c11a")),

dict(name="DeskZen Bamboo Desk Organiser Set",brand="DeskZen",category="Stationery",
     price=699,original_price=1299,stock=89,rating=4.4,reviews=765,badge="Eco",
     image_emoji="🗂️",image_color="#65a30d",
     description="Bamboo desk organiser set with 5 compartments: pencil cup, two small trays, business card holder, and document file slot. Natural, sustainable, and elegant.",
     highlights=_h("100% natural bamboo — eco-friendly and durable","5-piece modular set — arrange as you prefer","Holds: pens, scissors, paperclips, cards, A4 files","Natural grain texture — looks premium on any desk","Easy assembly — no tools needed","Wipe-clean surface"),
     specs_json=_s(Material="100% Natural Bamboo",Pieces="5 modular compartments",Includes="Pen cup + 2 trays + card holder + file slot",Assembly="Tool-free",Cleaning="Wipe-clean",Color="Natural bamboo grain",Warranty="30-day return"),
     image_url=_img("photo-1513519245088-0e12902e5a38"),
     images_json=_imgs("photo-1455390582262-044cdead277a","photo-1484480974693-6ca0a78fb36b","photo-1465188162913-8fb5709d6d57")),

dict(name="WriteBoard Magnetic Whiteboard 60×45cm",brand="WriteBoard",category="Stationery",
     price=899,original_price=1599,stock=45,rating=4.4,reviews=654,badge=None,
     image_emoji="📋",image_color="#0369a1",
     description="60×45cm magnetic whiteboard with 3 drywipe markers, magnetic eraser, 6 coloured magnets, and wall-mount hardware. Ghosting-free nano-coating surface.",
     highlights=_h("Nano-coating ghosting-free surface — erases perfectly","Magnetic — attach notes, memos, and reminders","Includes 3 markers (black/red/blue) + eraser + 6 magnets","60×45cm — ideal size for home, office, study room","Easy wall mount: screws + hooks included","Aluminium frame — lightweight yet sturdy"),
     specs_json=_s(Size="60×45cm",Surface="Nano-coating ghosting-free",Magnetic="Yes",Includes="3 markers + eraser + 6 magnets + wall mount",Frame="Aluminium",Weight="1.2kg",Warranty="1 Year"),
     image_url=_img("photo-1577563908411-5077b6dc7624"),
     images_json=_imgs("photo-1484480974693-6ca0a78fb36b","photo-1455390582262-044cdead277a","photo-1513519245088-0e12902e5a38")),

dict(name="JotBook Premium Hardcover Notebooks 2-Pack",brand="JotBook",category="Stationery",
     price=399,original_price=699,stock=167,rating=4.5,reviews=1123,badge=None,
     image_emoji="📒",image_color="#6366f1",
     description="2-pack of A5 hardcover notebooks with 200 lined pages each, ribbon bookmark, elastic closure, and pen-friendly 90gsm paper — no bleed-through.",
     highlights=_h("90gsm paper — no bleed-through with any pen type","200 lined pages per notebook (2 journals = 400 pages)","Hardcover with textured linen finish","Ribbon bookmark + elastic band closure per notebook","Lay-flat binding for comfortable writing","Pack of 2 — brilliant value"),
     specs_json=_s(Size="A5 (21×14.8cm)",Pages="200 per notebook (400 total)",Paper="90gsm lined acid-free",Cover="Hardcover linen texture",Binding="Lay-flat stitched",Extras="Ribbon + elastic closure (per notebook)",Pack="2 notebooks"),
     image_url=_img("photo-1543286386-713bdd548da4"),
     images_json=_imgs("photo-1517842264405-72bb906a1936","photo-1531346878377-a5be20888e57","photo-1465188162913-8fb5709d6d57")),

# ── TOYS & GAMING ─────────────────────────────────────────────────────────────
dict(name="BrickMaster STEM Building Blocks 500pc",brand="BrickMaster",category="Toys & Gaming",
     price=2999,original_price=4999,stock=38,rating=4.8,reviews=1543,badge="Bestseller",
     image_emoji="🧱",image_color="#f97316",
     description="500-piece STEM engineering building blocks set compatible with all major brands, with motors, gears, axles, and panels. Builds 12+ different models from one set.",
     highlights=_h("500 bricks + panels + gears + axles + motor","Compatible with LEGO, Mega Bloks, and all leading brands","Instruction book for 12+ unique model builds","ABS plastic — non-toxic, durable, BPA-free","Whet engineering curiosity in children 6+","Storage box included"),
     specs_json=_s(Pieces="500",Compatibility="Universal brick-compatible",Models="12+ instruction builds",Material="ABS BPA-free plastic",AgeGroup="6 years and above",Motor="1 included",Storage="Box included",Certification="EN71 / IS 9873"),
     image_url=_img("photo-1585366119957-373c206f81d7"),
     images_json=_imgs("photo-1558618666-fcd25c85cd64","photo-1563862810-c66e5fb31c0e","photo-1566576912321-d58ddd7a6088")),

dict(name="ChessElite Premium Carved Chess Set",brand="ChessElite",category="Toys & Gaming",
     price=1299,original_price=2499,stock=24,rating=4.9,reviews=543,badge="Hot",
     image_emoji="♟️",image_color="#1c1917",
     description="Handcrafted Sheesham wood chess set with 32 weighted pieces, folding chessboard with storage drawer, and felt-base pieces to protect surfaces.",
     highlights=_h("Handcrafted Sheesham (Rosewood) + Boxwood pieces","Weighted and felted pieces — satisfying to play with","Folding chessboard with built-in storage drawer","King height: 9.5cm — tournament regulation size","Includes spare queens for both sides","Gift-boxed — ready to present"),
     specs_json=_s(Material="Sheesham + Boxwood",KingHeight="9.5cm (regulation)",Weighting="Lead-weighted felt base",Board="Folding with storage drawer",Pieces="34 total (incl. 2 spare queens per side)",Packaging="Gift box",Origin="Handcrafted in India"),
     image_url=_img("photo-1586521995568-39abaa0c2311"),
     images_json=_imgs("photo-1558618666-fcd25c85cd64","photo-1563862810-c66e5fb31c0e","photo-1519744346361-7a029b427a59")),

dict(name="TurboRace Remote Control Car 1:18 Scale",brand="TurboRace",category="Toys & Gaming",
     price=1499,original_price=2999,stock=46,rating=4.6,reviews=876,badge="New",
     image_emoji="🏎️",image_color="#ef4444",
     description="1:18 scale RC car with 2.4GHz controller, 30km/h top speed, 4WD, LED headlights, rechargeable batteries, and all-terrain suspension for indoor and outdoor play.",
     highlights=_h("30km/h top speed — exciting for all ages","4WD all-terrain — sand, grass, gravel, flooring","2.4GHz controller — 50m range, lag-free","LED headlights — race even in the dark","Rechargeable batteries: car + controller via USB","Anti-roll cage crash-resistant body"),
     specs_json=_s(Scale="1:18",TopSpeed="30km/h",Drive="4-wheel drive",Frequency="2.4GHz",Range="50m",Battery="Rechargeable Li-Ion USB",LEDs="Yes",AgeGroup="6 years and above",Warranty="6 months"),
     image_url=_img("photo-1563862810-c66e5fb31c0e"),
     images_json=_imgs("photo-1585366119957-373c206f81d7","photo-1558618666-fcd25c85cd64","photo-1566576912321-d58ddd7a6088")),

dict(name="CardShark Premium Waterproof Playing Cards",brand="CardShark",category="Toys & Gaming",
     price=299,original_price=599,stock=287,rating=4.5,reviews=1234,badge=None,
     image_emoji="🃏",image_color="#1c1917",
     description="2-deck set of premium 100% PVC waterproof playing cards with jumbo index, standard poker size, perfectly smooth glide, and included card shuffler.",
     highlights=_h("100% PVC waterproof — no warping or staining","Jumbo index — easy to read for all ages","Perfectly smooth glide — ideal for card tricks","2 decks (red + blue) included","Includes manual card shuffler","Presented in flip-top gift tin"),
     specs_json=_s(Decks="2 (red + blue)",Material="100% PVC waterproof",Index="Jumbo",Size="Standard poker",Includes="Manual card shuffler + gift tin",AgeGroup="8 years and above"),
     image_url=_img("photo-1519744346361-7a029b427a59"),
     images_json=_imgs("photo-1586521995568-39abaa0c2311","photo-1563862810-c66e5fb31c0e","photo-1558618666-fcd25c85cd64")),

dict(name="SpeedCube Professional 3×3 Rubik's Cube",brand="SpeedCube",category="Toys & Gaming",
     price=399,original_price=799,stock=156,rating=4.7,reviews=2109,badge="Hot",
     image_emoji="🧩",image_color="#6366f1",
     description="Professional speed cube with magnetic positioning, corner-cutting ability, adjustable spring tension, and smooth anti-pop mechanism. WCA competition legal.",
     highlights=_h("Magnetic positioning for faster, accurate turns","Corner-cutting up to 45° — no lockups","Adjustable spring tension (tight/medium/loose)","Smooth stickerless bright colour tiles — no fading","WCA competition legal size (57mm)","Anti-pop mechanism — pieces stay in place"),
     specs_json=_s(Size="57mm (WCA legal)",Mechanism="Corner-cutting + anti-pop",Magnets="Yes — positioning assist",Tension="Adjustable spring",Surface="Stickerless bright tiles",AgeGroup="6 years and above",Certification="WCA legal"),
     image_url=_img("photo-1580896520869-e7dbad8fee9e"),
     images_json=_imgs("photo-1585366119957-373c206f81d7","photo-1558618666-fcd25c85cd64","photo-1563862810-c66e5fb31c0e")),

dict(name="DrawingFun Kids Creative Art Kit 120pc",brand="DrawingFun",category="Toys & Gaming",
     price=999,original_price=1799,stock=67,rating=4.7,reviews=1432,badge=None,
     image_emoji="🎨",image_color="#ec4899",
     description="120-piece creative art kit for children aged 4–12 with crayons, washable markers, watercolours, coloured pencils, sketch pads, and stencils in a tin case.",
     highlights=_h("120 pieces: crayons, markers, watercolours, pencils","All washable pigments — safe and easy to clean","Sketch pads (2×30 sheets) included","12 shape stencils for guided drawing","Non-toxic, ASTM D-4236 + IS 9686 certified","Organiser tin case — everything in one place"),
     specs_json=_s(Pieces="120",Includes="Crayons + Washable markers + Watercolours + Coloured pencils + 2 sketch pads + 12 stencils",TinCase="Yes",Washable="Yes",NonToxic="Yes",Certifications="ASTM D-4236 + IS 9686",AgeGroup="4–12 years"),
     image_url=_img("photo-1513364776144-60967b0f800f"),
     images_json=_imgs("photo-1558618666-fcd25c85cd64","photo-1585366119957-373c206f81d7","photo-1566576912321-d58ddd7a6088")),

dict(name="PuzzleWorld 3D Wooden Puzzle 250pc",brand="PuzzleWorld",category="Toys & Gaming",
     price=799,original_price=1499,stock=43,rating=4.6,reviews=654,badge=None,
     image_emoji="🧩",image_color="#92400e",
     description="Laser-cut 250-piece 3D wooden jigsaw puzzle that assembles into a detailed architectural landmark model. No glue needed — interlocking pieces hold together perfectly.",
     highlights=_h("250 laser-cut natural wood pieces — no rough edges","Interlocking without glue — sturdy finished model","3D architectural model when complete","Suitable for ages 14+ and adults","Eco-friendly natural birchwood material","Illustrated assembly guide included"),
     specs_json=_s(Pieces="250",Material="Natural birchwood",Assembly="Interlocking, no glue",FinishedSize="Varies by model",AgeGroup="14 years and above",AssemblyTime="3–5 hours",Includes="Illustrated guide",Warranty="30-day return"),
     image_url=_img("photo-1558618666-fcd25c85cd64"),
     images_json=_imgs("photo-1563862810-c66e5fb31c0e","photo-1585366119957-373c206f81d7","photo-1519744346361-7a029b427a59")),

dict(name="MagicKit Junior Magic Tricks Set 30 Tricks",brand="MagicKit",category="Toys & Gaming",
     price=699,original_price=1299,stock=89,rating=4.5,reviews=876,badge=None,
     image_emoji="🎩",image_color="#7c3aed",
     description="Beginner magic kit with 30 tricks including appearing flowers, coin magic, card tricks, rope magic, and more. Includes tutorial video access and instruction manual.",
     highlights=_h("30 complete magic tricks — beginner to intermediate","Includes all props needed for every trick","Tutorial video access via QR code","Step-by-step illustrated instruction manual","Includes magic wand, props, cards, rope, coins","Suitable for ages 8+ — great for confidence"),
     specs_json=_s(Tricks="30",Props="Full props included for all tricks",Videos="QR code tutorial access",Manual="Step-by-step illustrated",Includes="Wand + cards + rope + coins + flowers",AgeGroup="8 years and above"),
     image_url=_img("photo-1566576912321-d58ddd7a6088"),
     images_json=_imgs("photo-1585366119957-373c206f81d7","photo-1563862810-c66e5fb31c0e","photo-1558618666-fcd25c85cd64")),

dict(name="TableTennis Pro Ping Pong Set",brand="TableTennis",category="Toys & Gaming",
     price=899,original_price=1699,stock=34,rating=4.4,reviews=543,badge=None,
     image_emoji="🏓",image_color="#ef4444",
     description="Professional table tennis set with 2 pre-assembled rackets (5-ply wood + rubber), net clamp set, 6 balls, and carry bag. Suitable for all table types up to 10cm thick.",
     highlights=_h("2 pre-assembled rackets — 5-ply wood blade + 2mm rubber","Net and post clamp — fits tables up to 10cm thick","6 high-bounce 3-star quality balls included","Carry bag for storing all equipment","Suitable for casual and semi-competitive play","Table not included"),
     specs_json=_s(Rackets="2 pre-assembled",Blade="5-ply wood",Rubber="2mm both sides",Net="Retractable clamp type",Balls="6 three-star quality",TableFit="Up to 10cm thick",Includes="Carry bag",AgeGroup="6 years and above"),
     image_url=_img("photo-1559796483-96e1bf6e07c5"),
     images_json=_imgs("photo-1519744346361-7a029b427a59","photo-1558618666-fcd25c85cd64","photo-1563862810-c66e5fb31c0e")),

dict(name="NightGlow Galaxy Star Projector",brand="NightGlow",category="Toys & Gaming",
     price=1199,original_price=1999,stock=56,rating=4.7,reviews=1234,badge="Hot",
     image_emoji="🌌",image_color="#1e1b4b",
     description="Galaxy star projector with 12 lighting modes, 360° rotation, built-in speaker with Bluetooth, sleep timer, and white noise function. Perfect for nurseries and bedrooms.",
     highlights=_h("12 lighting modes: nebula + stars + moon + aurora","360° motorised dome rotation — immersive sky effect","Bluetooth speaker — play lullabies or music","Built-in white noise for improved sleep quality","Sleep timer: 1hr / 2hr / 4hr / always-on","App control via iOS and Android"),
     specs_json=_s(Modes="12",Rotation="360° motorised",Speaker="Bluetooth 5.0",WhiteNoise="6 built-in sounds",Timer="1/2/4hr or continuous",App="iOS + Android",Power="USB-C",AgeGroup="All ages"),
     image_url=_img("photo-1419242902214-272b3f66ee7a"),
     images_json=_imgs("photo-1558618047-fcd16d746a8b","photo-1565193566173-7a0ee3dbe261","photo-1558618666-fcd25c85cd64")),

dict(name="Premier Cricket Bat Kashmir Willow",brand="CricketPro",category="Sports & Fitness",
     price=1799,original_price=3499,stock=23,rating=4.6,reviews=876,badge=None,
     image_emoji="🏏",image_color="#92400e",
     description="Grade A Kashmir Willow cricket bat with full size (SH) handle, toe guard, anti-scuff sheet pre-applied, and 6-8 clear grains for straight-grain hitting.",
     highlights=_h("Grade A Kashmir Willow — responsive hitting","Full size Short Handle — 86.4cm total length","6–8 clear straight grains for maximum power","Protective toe guard and anti-scuff sheet pre-applied","Cane and rubber handle for superior grip","Ready to use — oiling not required before play"),
     specs_json=_s(Wood="Grade A Kashmir Willow",Size="Full Size Short Handle (SH)",Length="86.4cm",Grains="6–8 straight grains",Handle="Cane + rubber",ToeCap="Yes",AntiScuff="Pre-applied",Warranty="3 months"),
     image_url=_img("photo-1531415074968-036ba1b575da"),
     images_json=_imgs("photo-1598971861713-54ad16a7e72e","photo-1601422407692-ec4eeec1d9b3","photo-1534438327276-14e5300c3a48")),

dict(name="NexusPods True Wireless Earbuds 30hr",brand="NexusPods",category="Electronics",
     price=2299,original_price=3999,stock=52,rating=4.7,reviews=1876,badge="New",
     image_emoji="🎧",image_color="#8b5cf6",
     description="Premium TWS earbuds with ANC, 10mm drivers, 30-hour total battery life, wireless charging case, IPX4 rating, and aptX HD audio support.",
     highlights=_h("Active Noise Cancellation — focus anywhere","10mm drivers with bass boost mode","30-hour total: 8hr earbuds + 22hr wireless charging case","Wireless charging case (Qi compatible)","IPX4 splash resistant — gym and rain safe","aptX HD & AAC — crystal clear audio quality"),
     specs_json=_s(ANC="Yes",Drivers="10mm",Battery="8hr + 22hr wireless case",ChargingCase="Wireless Qi",Resistance="IPX4",Codecs="aptX HD + AAC + SBC",Connectivity="Bluetooth 5.3",Warranty="1 Year"),
     image_url=_img("photo-1606220945770-b5b6c2c55bf1"),
     images_json=_imgs("photo-1590658268037-6bf12165a8df","photo-1592921451044-ac7a3b62484c","photo-1613040809024-b4ef7ba99bc3")),

dict(name="UltraSlim 10W Solar Power Bank 20000mAh",brand="SolarX",category="Electronics",
     price=2499,original_price=4499,stock=34,rating=4.5,reviews=765,badge=None,
     image_emoji="☀️",image_color="#f59e0b",
     description="20000mAh solar power bank with dual solar panels, 10W wireless charging, USB-C 22.5W PD, LED flashlight, and rugged IPX5 waterproof shell.",
     highlights=_h("20000mAh — charges phone up to 5×","Dual solar panels — charge from sunlight","10W Qi wireless + USB-C 22.5W PD wired output","Built-in LED flashlight with SOS mode","IPX5 waterproof + shockproof rugged shell","Dual input: solar + USB-C for faster charging"),
     specs_json=_s(Capacity="20000mAh",Solar="Dual panel charging",Wireless="10W Qi",USBC="22.5W PD",Flashlight="LED + SOS",Waterproof="IPX5",Weight="480g",Warranty="1 Year"),
     image_url=_img("photo-1609091839311-d5365f9ff1c5"),
     images_json=_imgs("photo-1585771724684-38269d6639fd","photo-1526289034009-0240ddb68ce3","photo-1620138546344-7b2c38516edf")),

dict(name="Premium Running Shoes Pro 2.0",brand="SpeedStep",category="Men's Fashion",
     price=2999,original_price=4999,stock=41,rating=4.8,reviews=2134,badge="Bestseller",
     image_emoji="👟",image_color="#22c55e",
     description="Advanced running shoes with carbon fibre plate, React foam midsole, knit mesh upper, anti-torsion heel, and energy-return outsole for marathon performance.",
     highlights=_h("Carbon fibre plate for propulsive energy return","React foam midsole — responsive and lightweight","Knit mesh upper — breathable and stretchy fit","Anti-torsion heel for stability on long runs","Reflective detailing for night safety","Sizes UK 5 to 13 including half sizes"),
     specs_json=_s(Upper="Knit Mesh",Midsole="React Foam + Carbon Fibre Plate",Outsole="Energy-return rubber",HeelDrop="8mm",Sizes="UK 5–13",Colors="White/Neon/Black",Weight="260g (UK9)",Warranty="3 months"),
     image_url=_img("photo-1606107557195-0e29a4b5b4aa"),
     images_json=_imgs("photo-1542291026-7eec264c27ff","photo-1491553895911-0055eca6402d","photo-1539185441755-769473a23570")),

dict(name="HomeBreeze Table Fan 3-Speed 400mm",brand="HomeBreeze",category="Home & Living",
     price=1299,original_price=2499,stock=67,rating=4.3,reviews=1234,badge=None,
     image_emoji="🌀",image_color="#0891b2",
     description="400mm oscillating table fan with 3 speed settings, 90° wide oscillation, 4-blade design, 7-hour timer, and ultra-quiet 39dB motor for bedrooms.",
     highlights=_h("Ultra-quiet 39dB — perfect for bedroom use","3 speed settings: Low / Medium / High","90° automatic oscillation — covers full room","7-hour programmable sleep timer","400mm blade sweep — powerful airflow","Simple 3-button control + remote control"),
     specs_json=_s(BladeSize="400mm",Speeds="3",Oscillation="90°",Noise="39dB (low speed)",Timer="7-hour programmable",Remote="Included",Power="55W",Warranty="2 Years"),
     image_url=_img("photo-1626785774573-4b799315345d"),
     images_json=_imgs("photo-1565193566173-7a0ee3dbe261","photo-1558618047-fcd16d746a8b","photo-1507473885765-e6ed057f782c")),

dict(name="Running Sneakers Women's Flex 3.0",brand="SpeedStep",category="Women's Fashion",
     price=1999,original_price=3499,stock=54,rating=4.6,reviews=1543,badge="New",
     image_emoji="👟",image_color="#f43f5e",
     description="Lightweight women's running shoe with engineered mesh upper, foam flex sole, arch support system, and wide toe box for natural foot movement.",
     highlights=_h("Engineered mesh — lightweight and breathable","Foam flex sole returns energy with every step","Arch support system for injury prevention","Wide toe box — natural comfortable foot spread","Reflective strips for low-light visibility","Sizes UK 3–9 incl. half sizes, 5 colours"),
     specs_json=_s(Upper="Engineered Mesh",Sole="Foam Flex",ArchSupport="Yes",ToeBox="Wide",Sizes="UK 3–9",Colors="5 colors",Weight="210g (UK6)",Warranty="3 months"),
     image_url=_img("photo-1491553895911-0055eca6402d"),
     images_json=_imgs("photo-1542291026-7eec264c27ff","photo-1606107557195-0e29a4b5b4aa","photo-1539185441755-769473a23570")),

dict(name="Men's UV400 Polarized Sports Sunglasses",brand="VisionElite",category="Men's Fashion",
     price=799,original_price=1499,stock=98,rating=4.4,reviews=876,badge=None,
     image_emoji="🕶️",image_color="#374151",
     description="Sporty wraparound UV400 polarized sunglasses with TR90 flexible frame, rubber nose pads, anti-slip temple tips, ideal for running, cycling, and driving.",
     highlights=_h("UV400 lens — 100% UVA + UVB protection","Polarized — eliminates glare from water and roads","TR90 flexible frame — won't break on impact","Rubber non-slip nose pads + temple tips","Wraparound design — no peripheral glare","Includes hard case + cleaning cloth"),
     specs_json=_s(Lens="UV400 Polarized",Frame="TR90 flexible",NosePads="Non-slip rubber",TempleTips="Anti-slip rubber",Style="Wraparound sport",Colors="Black/Silver/Blue/Gunmetal",Includes="Hard case + cloth"),
     image_url=_img("photo-1572635196237-14b3f281503f"),
     images_json=_imgs("photo-1551816230-ef5deaed4a26","photo-1511499767150-a48a237f0083","photo-1574258495973-f010dfbb5371")),

dict(name="Smart Robot Vacuum Cleaner with Mapping",brand="CleanPro",category="Home & Living",
     price=12999,original_price=19999,stock=12,rating=4.7,reviews=876,badge="Hot",
     image_emoji="🤖",image_color="#0369a1",
     description="Smart robot vacuum with LiDAR laser mapping, 3000Pa suction, self-emptying base (60-day capacity), mop function, and app-scheduled room-by-room cleaning.",
     highlights=_h("LiDAR laser mapping — precise room boundary detection","3000Pa powerful suction — deep carpet and hard floor","Self-emptying base holds 60 days of dustbin","Vacuum + mop combo in one unit","App control: schedule, zone, virtual barriers","Auto-returns to dock when battery is low"),
     specs_json=_s(Mapping="LiDAR Laser",Suction="3000Pa",SelfEmptying="60-day capacity base",MopFunction="Yes",Navigation="Room mapping with virtual barriers",App="iOS + Android",BatteryLife="180 min",Warranty="2 Years"),
     image_url=_img("photo-1558317374-067fb5f30001"),
     images_json=_imgs("photo-1527515637462-cff94eecc1ac","photo-1584622781564-1d987f7333c1","photo-1615397587530-f2c5b23ef26e")),

dict(name="Elegant Silk Touch Premium Hoodie",brand="UrbanWear",category="Men's Fashion",
     price=1299,original_price=2499,stock=76,rating=4.6,reviews=1234,badge="Trending",
     image_emoji="👕",image_color="#6366f1",
     description="Ultra-premium 100% ring-spun cotton hoodie with brushed fleece interior, kangaroo pocket, ribbed cuffs, and a relaxed oversized fit. Machine washable.",
     highlights=_h("100% ring-spun cotton — butter-soft feel","Brushed fleece inner — extra warmth without weight","Generous kangaroo front pocket","Ribbed cuffs and waistband hold shape over time","Machine washable — colour fade resistant","Sizes XS–3XL, 10 colours"),
     specs_json=_s(Material="100% Ring-spun Cotton + Fleece lining",Fit="Oversized relaxed",Pockets="Kangaroo front",Cuffs="Ribbed",Sizes="XS–3XL",Colors="10 colors",Care="Machine wash cold",Origin="India"),
     image_url=_img("photo-1556821840-3a63f15732ce"),
     images_json=_imgs("photo-1618354691373-d851c5c3a990","photo-1509631179647-0177331693ae","photo-1527719327859-c6ce80353573")),
]

# ── Reviews ───────────────────────────────────────────────────────────────────

def _r(n,rat,t,b,v=True,h=0):
    return dict(user_name=n,rating=rat,title=t,body=b,verified=v,helpful=h)

SEED_REVIEWS = {
"Wireless Noise-Cancelling Headphones":[
    _r("Rahul M.",5,"Best headphones under ₹3000!","ANC is amazing — blocks everything. Battery lasts all day. Studio-grade sound. 100% worth it!",True,234),
    _r("Priya S.",5,"Exceeded expectations","Game-changer for WFH. Calls are crystal clear — colleagues can't hear my kids!",True,178),
    _r("Arjun K.",4,"Great but slightly tight","Sound is phenomenal. ANC brilliant. Just a little tight after 3+ hours. No other complaints.",False,89),
    _r("Vikram N.",4,"Good sound, average mic","Music listening: 5 stars. Mic for calls: decent. Overall great buy at this price.",True,67),
],
"Smart LED Desk Lamp":[
    _r("Sneha P.",5,"Perfect study companion","Eye-care mode is a lifesaver. USB-C port charges my phone while I work. Love it!",True,112),
    _r("Kartik B.",4,"Good quality, wish brighter","All features work great. Warmest mode is very cozy. Wish max brightness was slightly higher.",True,45),
    _r("Ananya T.",5,"Sleek and functional","Looks so premium on desk. Memory function is super convenient.",False,89),
],
"Mechanical Gaming Keyboard":[
    _r("Aditya G.",5,"Gaming beast!","Tactile feedback is addictive. RGB is vibrant. Anti-ghosting is perfect.",True,203),
    _r("Rohit S.",5,"Best keyboard I've owned","Night and day vs membrane. Key travel is satisfying. Wrist rest is a bonus.",True,167),
    _r("Neha V.",4,"Great for coding and gaming","Both experiences excellent. Only wish it had wireless support.",False,78),
],
"10000mAh Slim Power Bank":[
    _r("Meera L.",5,"Slim and fast!","Charged my iPhone 2.5 times on a long flight. Fits in jeans pocket. Genuinely fast.",True,312),
    _r("Suresh K.",4,"Does what it promises","Reliable. Charges Samsung S23 about 2.5 times. Doesn't get hot. Good value.",True,198),
    _r("Lavanya M.",5,"Perfect for travel","Used for 5-day trip. Charged 3 devices. No issues whatsoever.",True,145),
],
"NexusPhone 5G Pro Smartphone":[
    _r("Vivek R.",5,"Flagship killer!","Camera quality rivals phones twice the price. 5G speeds are blazing. Battery lasts easily 2 days.",True,542),
    _r("Anitha S.",5,"Best phone I've used","120Hz display is buttery smooth. Snapdragon 8 Gen 2 handles everything without a hiccup.",True,387),
    _r("Karan M.",4,"Great phone, heating on gaming","Excellent specs and camera. Gets slightly warm during extended gaming sessions but otherwise flawless.",False,213),
],
"AirSound TWS Wireless Earbuds Pro":[
    _r("Deepika P.",5,"Excellent for the price!","ANC works surprisingly well. Battery lasts all workday. Sound signature is balanced and clear.",True,187),
    _r("Sanjay K.",4,"Good earbuds, case is bulky","Audio quality is great for this price. The charging case is a bit larger than expected.",True,89),
],
"FitPro Smart Fitness Watch":[
    _r("Preethi A.",5,"Accurate heart rate tracking","SpO2 and heart rate match my hospital monitor closely. Sleep tracking is very useful.",True,234),
    _r("Rohit V.",4,"Great watch, GPS slightly slow","Overall excellent. GPS locks in about 30 seconds — not instant but good enough.",True,112),
],
"BoomBox Portable Bluetooth Speaker":[
    _r("Amrit J.",5,"Pool-party essential!","Dropped it in the pool. It kept playing. Sound is genuinely loud and clear. Love it.",True,178),
    _r("Simran K.",4,"Good sound, charging could be faster","Sound quality and waterproofing are excellent. Takes 3.5 hrs to fully charge which is a bit slow.",True,67),
],
"ClearVue 4K HD Webcam":[
    _r("Rajesh T.",5,"Crystal clear video calls","My team actually commented on how much better my video looks. Microphone is surprisingly good too.",True,145),
    _r("Leela M.",4,"Great cam, software optional","Works perfectly plug-and-play. The optional software has some bugs but you don't really need it.",False,56),
],
"HyperGlide Wireless Gaming Mouse":[
    _r("Siddharth P.",5,"Ultra light and precise!","At 63g you barely feel it's there. 25600 DPI is crazy precise. Battery lasts weeks.",True,267),
    _r("Tanuj R.",5,"Best mouse I've used","Switched from a wired mouse and I'll never go back. Truly zero perceptible latency.",True,198),
],
"USB 7-Port Powered Hub":[
    _r("Vasanth K.",4,"Solid hub for the price","All 7 ports work as advertised. Runs my external SSD, keyboard, mouse, and more simultaneously.",True,89),
    _r("Priya N.",4,"Handy for clean desk setup","Reduced cable clutter significantly. Individual power switches are a great feature.",False,45),
],
"ErgoDesk Adjustable Laptop Stand":[
    _r("Ashish M.",5,"Neck pain gone after 2 weeks","At the right height, my posture improved dramatically. Build quality feels premium.",True,212),
    _r("Kavitha S.",4,"Great stand, folds nicely","Stable and adjustable. Folds very slim for travel. Slight wobble at maximum height but manageable.",True,78),
],
"SafeView 1080p Smart Security Camera":[
    _r("Sunil P.",5,"Worth every rupee!","Night vision is impressive — see clear colour video even in complete darkness. App is intuitive.",True,134),
    _r("Reena K.",4,"Good camera, cloud needs subscription after free period","60-day free period is generous. After that you'll want the subscription. Hardware is excellent.",True,67),
],
"ChargeFast 15W Wireless Charging Pad":[
    _r("Dhruv T.",5,"Fast and reliable","Charges my Samsung S24 at full 15W. Stand is stable and grippy. LED is pleasantly dim at night.",True,89),
    _r("Sonal M.",4,"Works great through my cover","Charges through my 2mm silicone case perfectly. Exactly as advertised.",True,45),
],
"SoundWar Gaming Headset 7.1":[
    _r("Aman R.",5,"Immersive 7.1 sound!","Positional audio in FPS games is genuinely useful. Memory foam earcups are comfortable for hours.",True,156),
    _r("Pooja V.",4,"Great headset, mic is good not great","Gaming experience is stellar. Microphone works fine but voice recording quality is average.",False,78),
],
"SpeedDrive External SSD 1TB":[
    _r("Tejas N.",5,"Blazing fast!","Transferred 100GB in under 2 minutes. Sleek design. Build quality is excellent.",True,234),
    _r("Smita R.",4,"Great for content creation","Editing 4K footage directly from this SSD with zero lag. Very pleased.",True,145),
],
"GlowStrip RGB Smart LED Strip":[
    _r("Arnav S.",5,"Transformed my gaming room!","Music sync mode is unbelievably cool during gaming. App is easy to use. Alexa works perfectly.",True,312),
    _r("Riddhi P.",4,"Great strip, adhesive could be stronger","Colours are vivid and music sync is fun. Adhesive isn't the strongest on rough walls — use extra tape.",True,89),
],
"ArtPad Digital Drawing Tablet":[
    _r("Mitali G.",5,"Perfect for digital art beginners","8192 pressure levels make brush strokes feel incredibly natural. My art improved in weeks.",True,178),
    _r("Rohan K.",4,"Excellent tablet, drivers were tricky","Performance is fantastic. Had some initial driver setup issues on Windows 11 but support resolved it.",True,89),
],
"CineMax Mini Projector HD":[
    _r("Farhan S.",5,"Home cinema experience!","1080p image is sharp and clear even in semi-dark room. Built-in Android TV means all streaming apps work.",True,145),
    _r("Anjali M.",4,"Great projector, speakers could be louder","Picture quality is amazing. The 10W speakers are decent but you'll want external speakers for large rooms.",False,67),
],
"ClassicWear Premium Oxford Shirt":[
    _r("Vikram S.",5,"Best shirt in my wardrobe","Egyptian cotton lives up to the hype — incredibly breathable even in summer. Slim fit is perfect.",True,89),
    _r("Rahul P.",4,"Good quality, size up","Quality is excellent but sizes run slightly small. Go one size up. Worth every rupee though.",True,56),
],
"FitStyle Slim Fit Chino Pants":[
    _r("Aniket R.",5,"Comfortable and stylish","4-way stretch makes these the most comfortable formal pants I've worn. Look great with shirts.",True,67),
    _r("Priya M.",4,"Good chinos, check the length","Quality is excellent. Just note the inseam length — may need alterations for shorter frames.",True,34),
],
"DenimCraft Men's Denim Jacket":[
    _r("Rohan T.",5,"Fits perfectly","The slim cut looks and feels great. Stonewash is the perfect shade — not too light, not too dark.",True,89),
    _r("Gaurav K.",4,"Good jacket, buttons could be sturdier","Overall love the jacket. One button felt a bit loose out of the box but a quick tighten fixed it.",True,45),
],
"LuxWear Premium Genuine Leather Belt":[
    _r("Varun M.",5,"Premium feel","Full-grain leather is much better quality than belts at triple the price. Buckle is solid.",True,56),
    _r("Shruti N.",4,"Good belt, stiff initially","Quality is genuine leather for sure. A bit stiff initially but softens beautifully with wear.",True,34),
],
"PoloClub Men's Polo T-Shirt Pack of 3":[
    _r("Harish K.",5,"Incredible value!","3 quality polo shirts for under ₹1000 is unbeatable. Fabric is piqué and they wash well.",True,112),
    _r("Dinesh R.",4,"Good polos, slight colour variation","Quality is solid. One shirt was slightly lighter in shade than the other two in the pack.",False,45),
],
"SlimCarry Minimalist Leather Wallet":[
    _r("Nikhil S.",5,"Perfect slim wallet","Exactly what I wanted — holds my 6 cards and cash in 6mm. RFID works, tested.",True,89),
    _r("Arun K.",4,"Good wallet, card slots tight initially","Leather quality is excellent. Card slots were very tight initially but loosened up after a week.",True,45),
],
"TimeCraft Classic Chronograph Watch":[
    _r("Rishabh P.",5,"Looks ₹15000, cost ₹3500","Everyone asks where I got it from. Sapphire glass, leather strap, the whole package.",True,178),
    _r("Nisha T.",4,"Good watch, clasp could be smoother","Watch looks stunning and keeps perfect time. The deployment clasp is a little stiff to open.",True,89),
],
"StreetStep Men's Casual Sneakers":[
    _r("Kiran M.",5,"My everyday shoe","These go with literally everything. Comfortable from day one — no breaking in needed.",True,134),
    _r("Tejas P.",4,"Good sneakers, narrow fit","Quality and look are excellent. Those with wider feet should size up half.",True,67),
],
"TrekWay Men's Laptop Backpack 30L":[
    _r("Aditya V.",5,"Love this backpack!","Hidden back anti-theft pocket is genius. Padded laptop sleeve protected through airport security perfectly.",True,156),
    _r("Meena R.",4,"Great bag, shoulder straps could be thicker","Very well organised. Heavy loads feel fine but thicker shoulder strap padding would make it exceptional.",True,78),
],
"FlexFit Men's Sports Jogger Pants":[
    _r("Ranjit K.",5,"Most comfortable joggers ever","4-way stretch is real — squats and lunges feel completely unrestricted. Moisture-wicking actually works.",True,89),
    _r("Pooja S.",4,"Good joggers, drawstring knot loosens","Quality is great. The drawstring knot tends to loosen during workouts — a minor inconvenience.",True,45),
],
"FloralStyle Floral Wrap Summer Dress":[
    _r("Shreya M.",5,"Perfect summer dress!","The chiffon is lightweight and flows beautifully. The wrap ties are adjustable for different body types.",True,134),
    _r("Kavita P.",4,"Pretty dress, slightly see-through","The floral print is gorgeous. Wear a slip underneath as the fabric is slightly sheer in bright light.",True,67),
],
"FlexWear High-Waist Yoga Leggings":[
    _r("Ritu S.",5,"Best leggings I've owned!","Buttery soft, squat-proof tested, high waist doesn't roll down even in inversions. Obsessed.",True,234),
    _r("Ananya K.",5,"My whole yoga class wants these","Everyone in my yoga class asked where I got these. Comfortable for 2-hour sessions.",True,167),
    _r("Priya B.",4,"Love the fit, pocket small","Leggings themselves are perfect. The waistband pocket is a bit small for larger phones.",True,89),
],
"FitFashion Women's Sports Crop Top":[
    _r("Divya N.",5,"Great support and comfort","Built-in bra provides enough support for yoga and low-impact cardio. Fabric is lovely.",True,67),
    _r("Simran T.",4,"Good top, medium support only","For high-impact exercise like running you'll want a separate sports bra. But for yoga — perfect.",True,45),
],
"EcoStyle Canvas Shoulder Tote Bag":[
    _r("Aditi M.",5,"My everyday bag now!","Holds my laptop, lunch, gym clothes, and more with room to spare. Love that it's eco-friendly.",True,89),
    _r("Varsha K.",4,"Great bag, canvas stains easily","Functionality is excellent. Light-coloured canvas picks up marks easily — just keep it in mind.",True,45),
],
"StepStyle Women's Ankle Fashion Boots":[
    _r("Nidhi P.",5,"Comfortable AND stylish!","Block heel means I can wear these to work all day without foot fatigue. Look expensive.",True,112),
    _r("Leela V.",4,"Good boots, sizing runs large","Boots look great and feel reasonably comfortable. Sizing runs half a size large — size down.",True,67),
],
"ElegantTime Women's Rose Gold Watch":[
    _r("Priya N.",5,"Elegant and beautiful!","Received so many compliments the first week. Slim profile sits elegantly on the wrist.",True,145),
    _r("Anishi M.",4,"Lovely watch, links are hard to remove","The watch is gorgeous. Adjusting the mesh strap length needed a jeweller's help as the tool wasn't ideal.",True,78),
],
"LuxCarry Women's Structured Handbag":[
    _r("Neethu K.",5,"Looks like a designer bag!","Structured shape stays perfectly. Gold hardware is solid. Compartments are brilliantly laid out.",True,134),
    _r("Divya S.",4,"Beautiful bag, inside dark","Love the exterior. The inside lining is very dark making it hard to find items — use a pouch.",True,67),
],
"EcoKitchen Bamboo Cutting Board Set":[
    _r("Geeta M.",5,"Eco-friendly and beautiful","Boards are gorgeous on kitchen counter. Sturdy, no smell absorption, easy to clean.",True,134),
    _r("Shyam P.",4,"Great set, oil them regularly","Very practical. Oil with food-grade mineral oil monthly to keep in top shape.",True,78),
],
"ZenAir Aromatherapy Diffuser 500ml":[
    _r("Radha V.",5,"My bedroom is a spa now","Runs silently all night. Lavender oil fills the room beautifully. Sleep quality improved!",True,201),
    _r("Jatin S.",5,"Beautiful LED colours","7 LED modes are stunning. Great living room centpiece. Very quiet operation.",False,145),
    _r("Preethi A.",4,"Good but tank could be bigger","Works great, smells wonderful. 500ml depletes in 8 hours — wish for 750ml option.",True,89),
],
"DreamRest Cervical Memory Foam Pillow Set":[
    _r("Supriya K.",5,"Neck pain completely gone!","Had chronic neck pain for years. After 2 weeks on these pillows, significantly reduced. Works!",True,312),
    _r("Rajesh T.",5,"Best pillows I've used","Memory foam perfectly adapts to head shape. Used to wake with headaches — completely gone.",True,245),
    _r("Nisha G.",4,"Great support, slightly firm","Excellent pillows. Bamboo cover is incredibly soft. Slightly firmer than expected but sleep is great.",True,134),
],
"PureAir HEPA H13 Air Purifier":[
    _r("Ravi K.",5,"Air quality dramatically improved","AQI in bedroom dropped from 150 to under 20. Sleep is noticeably better. Worth every rupee.",True,234),
    _r("Meena S.",4,"Good purifier, filter cost","Performance is excellent. Just be aware replacement filters cost ₹800 every 6 months.",True,112),
],
"BrewPerfect Pour Over Coffee Maker":[
    _r("Amit P.",5,"Amazing coffee every morning","The clarity and flavour of pour-over coffee vs my old drip machine is remarkable.",True,89),
    _r("Sunita K.",4,"Great maker, takes practice","The pour-over technique takes a few tries to master. But the resulting coffee is exceptional.",True,45),
],
"LumiSmart Smart LED Bulb Pack of 3":[
    _r("Dhruv S.",5,"Best smart bulbs for the money","Setup in under 2 minutes. Alexa integration is seamless. Colour range is vivid and accurate.",True,145),
    _r("Kavya M.",4,"Good bulbs, app has minor bugs","Lights work perfectly. App occasionally needs a restart to reconnect but rarely.",True,67),
],
"KitchenPrime Non-Stick Cookware Set 5pc":[
    _r("Anita R.",5,"Excellent non-stick performance!","Even delicate eggs slide off without any oil. Even heat distribution is perfect.",True,178),
    _r("Vijay K.",4,"Good cookware, handles get warm","Non-stick is excellent. The handle joints get slightly warm — use oven mitts for long cooking.",True,89),
],
"CleanPro Cordless Stick Vacuum 25000Pa":[
    _r("Pooja S.",5,"Powerful and light!","25000Pa suction picks up pet fur like magic. LED brush head reveals dust I never knew was there.",True,234),
    _r("Ramesh T.",4,"Great vac, bin too small","Suction and battery life are excellent. The 0.8L bin needs emptying every session with pet hair.",True,112),
],
"CrispAir Digital Air Fryer 5L":[
    _r("Rekha M.",5,"Best kitchen purchase!","Makes crispy chips and chicken with almost no oil. Family of 4 can cook in one batch.",True,312),
    _r("Sanjay P.",5,"Replaced my oven for most cooking","Preheat is instant. Popcorn, fish fingers, vegetables — everything comes out perfectly.",True,234),
    _r("Divya K.",4,"Great fryer, smell while heating","Performance is excellent. Emits a slight plastic smell for first 2-3 uses which disappears after.",True,89),
],
"GlowLab 20% Vitamin C Glow Serum":[
    _r("Tanya M.",5,"My skin is GLOWING!","Used for 6 weeks — dark spots from sun damage visibly lightened. Skin looks brighter.",True,289),
    _r("Shreya K.",5,"Best Vitamin C serum","Doesn't sting or irritate my sensitive skin. Absorbed quickly, no residue.",True,198),
    _r("Nandini R.",4,"Gradual but visible results","After 4 weeks, brighter skin and smaller pores. Adding hyaluronic acid means I skip moisturiser.",False,112),
],
"ProStyle Professional Hair Dryer 2400W":[
    _r("Priya M.",5,"Professional salon results at home","Dries my thick hair in 8 minutes flat. Ionic technology means zero frizz. Game changer.",True,178),
    _r("Radhika S.",4,"Great dryer, heavy for long sessions","Power and performance are excellent. Gets a little arm-tiring for very long sessions — minor complaint.",True,89),
],
"TanShield SPF 50+ Sunscreen":[
    _r("Ananya P.",5,"No white cast — finally!","Skin tone is medium-dark and this absorbs invisibly. SPF protection has kept my tan at bay.",True,234),
    _r("Kartik M.",4,"Good sunscreen, slightly shiny","Works very well. Gives a slight sheen over time — set with powder if you need matte finish.",True,112),
],
"LipLux Matte Lipstick Collection":[
    _r("Ishita T.",5,"8 shades for ₹699!","Quality is incredible for the price. Colour payoff is like high-end brands. Comfortable and long-lasting.",True,178),
    _r("Neha V.",4,"Good lipstick, slightly drying after 4hrs","First 4 hours are perfect. Becomes very slightly dry after that — use a lip balm beforehand.",True,89),
],
"NightGlow Retinol + Peptide Night Cream":[
    _r("Meera K.",5,"Visible results in 3 weeks","Fine lines around my eyes clearly reduced after 3 weeks of use. Skin feels firmer.",True,167),
    _r("Sonam R.",4,"Good cream, use sunscreen in morning!","Works very well. Just remember — retinol increases sun sensitivity, always pair with SPF in morning.",True,89),
],
"PureGlow Activated Charcoal Face Wash":[
    _r("Riya S.",5,"Breakouts reduced!","Used twice a day for 3 weeks. Breakouts reduced by 70% and pores visibly smaller.",True,134),
    _r("Sachin M.",4,"Good face wash, slightly drying","Cleansing efficacy is excellent. Can feel slightly drying if used more than twice daily — moisturise after.",True,67),
],
"ManGroomed Premium Beard Grooming Kit":[
    _r("Dev K.",5,"Complete kit, excellent value","Everything you need for beard care in one purchase. The beard oil smells incredible.",True,112),
    _r("Rajan T.",4,"Good kit, trimmer battery life average","Products are all high quality. The trimmer battery lasts about 45 minutes — fine for weekly trim.",True,56),
],
"ZenYoga Premium Anti-Slip Yoga Mat 6mm":[
    _r("Preethi S.",5,"Best yoga mat I've owned","Grip is incredible even with sweaty hands. 6mm cushioning protects my knees in kneeling poses.",True,234),
    _r("Nisha K.",5,"Alignment lines are super helpful","Alignment lines helped me correct my Warrior II pose immediately. Excellent mat overall.",True,167),
],
"FitBand Resistance Band Set 5 Levels":[
    _r("Arjun S.",5,"Complete gym in a bag","These 5 bands replace my entire home gym for legs and glutes training. Anti-snap is real.",True,178),
    _r("Divya M.",4,"Good bands, lightest one too easy","Quality is excellent. If you're already trained, even the 10lb band will feel light for warm-up only.",True,89),
],
"AquaSteel Insulated Water Bottle 1L":[
    _r("Rohit P.",5,"Ice cold water all day!","Filled with ice water at 7am — still ice cold at 5pm. Genuinely 24-hour cold retention.",True,267),
    _r("Kavitha R.",4,"Good bottle, slightly heavy when full","Insulation is excellent. A full litre of water does make it somewhat heavy for casual handbag carry.",True,112),
],
"MassGain Whey Protein Chocolate 1kg":[
    _r("Vikram T.",5,"Tastes great, mixes perfectly!","No clumping, tastes like chocolate milkshake not chalk. Seeing muscle recovery improvements.",True,312),
    _r("Arun K.",5,"Best protein at this price","Tried many brands — this gives best value for protein quality ratio. Bloating is minimal.",True,234),
    _r("Saurav M.",4,"Good protein, sweetness intense","Quality is great. Chocolate flavour is quite sweet — mix with just water, not milk, for balance.",True,112),
],
"VitaMax Complete Daily Multivitamin":[
    _r("Smitha P.",5,"Noticeable energy improvement","After 2 weeks taking daily, energy levels and focus are noticeably better. Hair looks healthier too.",True,134),
    _r("Rajesh K.",4,"Good multivitamin, difficult to swallow","Comprehensive formula. The tablet is quite large — might want to cut it in half initially.",True,67),
],
"HerbalPure Giloy + Ashwagandha Capsules":[
    _r("Sunita M.",5,"Stress reduced noticeably","After 3 weeks on these, stress and anxiety have genuinely reduced. Sleep quality improved too.",True,189),
    _r("Vikram P.",4,"Good supplement, take consistently","Benefits are real but require consistent 6+ weeks of use. Give it time — not an overnight fix.",True,89),
],
"OmegaPure Omega-3 Fish Oil":[
    _r("Anitha K.",5,"No fishy burps!","Enteric coating means zero fishy aftertaste or burps. Joint inflammation noticeably reduced.",True,145),
    _r("Suresh R.",4,"Good omega-3, capsules large","Quality is excellent. The capsules are large — some may prefer splitting into 2 per day.",True,67),
],
"CareDigi Digital Blood Pressure Monitor":[
    _r("Ramachandra K.",5,"Matches hospital readings exactly","Compared with hospital sphygmomanometer — readings were within 2mmHg. Excellent accuracy.",True,234),
    _r("Lakshmi P.",5,"Easy to use for elderly parents","My 70-year-old parents use this daily without issue. One-button operation is perfect for seniors.",True,178),
],
"HeatEase XL Electric Heating Pad":[
    _r("Meena S.",5,"Back pain relief!","Chronic lower back pain reduced significantly with 30-min sessions twice daily. Very happy.",True,189),
    _r("Priya V.",4,"Good pad, cord could be longer","Moist heat is wonderfully penetrating. The 1.5m cord is just slightly short for couch use from the outlet.",True,89),
],
"InkMate Premium Gel Pen Set 12 Colors":[
    _r("Anika R.",5,"Perfect for journaling!","Smooth consistent flow, no skipping, and the metallic colours look stunning on dark paper.",True,145),
    _r("Sita M.",4,"Good pens, neon slightly less vibrant","All pens write beautifully. Neon colours are a bit less vibrant than expected but still lovely.",True,67),
],
"ClassicNotes Genuine Leather Journal A5":[
    _r("Karthik S.",5,"Luxury journaling experience","Full-grain leather feels incredible. Paper takes fountain pen ink beautifully. No bleed-through.",True,189),
    _r("Priya N.",4,"Beautiful journal, clasp fragile","The journal itself is gorgeous. The magnetic closure felt slightly fragile — treat it gently.",True,89),
],
"ArtDraw Professional Drawing Pencil Set":[
    _r("Meghna K.",5,"Complete drawing set!","From technical 9H architectural drawings to expressive 9B life drawing. Cedar sharpens so cleanly.",True,134),
    _r("Arjun P.",4,"Great pencils, case could be sturdier","Pencil quality is excellent. The canvas roll case is functional but not the most durable.",True,67),
],
"BrickMaster STEM Building Blocks 500pc":[
    _r("Ananya M.",5,"Kids love it!","My 8-year-old spent 6 hours building non-stop. Instruction quality is excellent. Great for STEM.",True,234),
    _r("Vikas P.",4,"Great set, some pieces tiny","Excellent quality and compatibility. Very small pieces — not suitable unsupervised for under 6.",True,112),
],
"ChessElite Premium Carved Chess Set":[
    _r("Suresh K.",5,"Heirloom quality chess set","The carving detail on the knights is incredible. Weighted pieces feel authoritative. A joy to play on.",True,178),
    _r("Anand R.",5,"Professional feel","Board and pieces match the finesse of sets selling for 3× the price. Brilliant purchase.",True,145),
],
"TurboRace Remote Control Car 1:18 Scale":[
    _r("Little Rahul's Dad",5,"Birthday gift success!","Son is obsessed. 30km/h on carpet is genuinely fast and exciting. Battery charge time is reasonable.",True,167),
    _r("Vikram K.",4,"Great car, no spare parts kit","Performance is excellent. Would love a small spare parts kit included for minor repairs.",True,89),
],
"SpeedCube Professional 3×3 Rubik's Cube":[
    _r("Speed Cuber Arjun",5,"Competition ready!","Sub-15 second solves immediately after opening. Magnets give perfect tactile feedback. Best cube under ₹500.",True,234),
    _r("Beginner Priya",4,"Great for beginners too!","Even as a beginner the smooth turning makes learning algorithms much easier than my old stiff cube.",True,112),
],
"NightGlow Galaxy Star Projector":[
    _r("Neha S.",5,"Magical bedtime atmosphere!","Kids fall asleep so much faster with the galaxy mode on. White noise option adds to the calm.",True,234),
    _r("Ravi M.",4,"Great projector, app connectivity drops","Projector itself is wonderful. App occasionally loses connection and needs a restart.",True,89),
],
"TableTennis Pro Ping Pong Set":[
    _r("Sanjay K.",4,"Good set for home use","Rackets feel professional for the price. Net tension is adjustable and fits our 8cm thick table.",True,67),
    _r("Priya T.",5,"Weekend family fun!","We play every weekend now. Kids love it and the rackets have held up well.",True,89),
],
"NexusPods True Wireless Earbuds 30hr":[
    _r("Karan M.",5,"ANC is outstanding!","The ANC is on par with earbuds at twice the price. Wireless charging case is a huge bonus.",True,198),
    _r("Divya K.",4,"Great earbuds, touch controls sensitive","Sound quality is excellent. Touch controls are occasionally triggered accidentally. Software update needed.",True,89),
],
"Premier Cricket Bat Kashmir Willow":[
    _r("Arun Venkat",5,"Great bat for the price!","Edges are thick, hitting zone is sweet. Anti-scuff sheet applied well. Impressed with quality.",True,145),
    _r("Rahul T.",4,"Good bat, needs oiling eventually","One of the best Kashmir willow bats at this price. After a month of use, light oiling recommended.",True,78),
],
"Premium Running Shoes Pro 2.0":[
    _r("Kiran S.",5,"Best running shoes I've had","Did a half-marathon, zero blisters. Carbon plate is noticeably propulsive on the final km stretch.",True,289),
    _r("Ravi P.",4,"Excellent shoes, narrow fit","Exceptional for neutral runners. Those with wide feet should size up or try a wider variant.",True,145),
],
}


def seed_products(app, db):
    with app.app_context():
        if Product.query.count() == 0:
            product_map = {}
            for p in SEED_PRODUCTS:
                product = Product(**p)
                db.session.add(product)
                db.session.flush()
                product_map[p["name"]] = product.id
            db.session.commit()
            print(f"[DB] Seeded {len(SEED_PRODUCTS)} products.")

            for product_name, reviews in SEED_REVIEWS.items():
                pid = product_map.get(product_name)
                if pid:
                    for r in reviews:
                        db.session.add(Review(product_id=pid, **r))
            db.session.commit()
            print(f"[DB] Seeded reviews for all products.")
